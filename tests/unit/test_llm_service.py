import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.llm_service import LLMService
from app.models.schemas import LLMProvider, CVEvaluation, ProjectEvaluation
from app.core.exceptions import LLMServiceError


class TestLLMService:
    
    @pytest.fixture
    def llm_service(self):
        """Create LLMService instance for testing"""
        return LLMService()
    
    def test_init_with_openai_key(self, llm_service):
        """Test LLMService initialization with OpenAI API key"""
        with patch('app.services.llm_service.settings.OPENAI_API_KEY', 'test-key'):
            with patch('app.services.llm_service.settings.GEMINI_API_KEY', None):
                service = LLMService()
                assert hasattr(service, 'setup_clients')
    
    def test_init_with_gemini_key(self, llm_service):
        """Test LLMService initialization with Gemini API key"""
        with patch('app.services.llm_service.settings.OPENAI_API_KEY', None):
            with patch('app.services.llm_service.settings.GEMINI_API_KEY', 'test-key'):
                service = LLMService()
                assert hasattr(service, 'setup_clients')
    
    def test_init_with_no_keys(self, llm_service):
        """Test LLMService initialization with no API keys"""
        with patch('app.services.llm_service.settings.OPENAI_API_KEY', None):
            with patch('app.services.llm_service.settings.GEMINI_API_KEY', None):
                service = LLMService()
                assert hasattr(service, 'setup_clients')
    
    @pytest.mark.asyncio
    async def test_evaluate_cv_with_openai_success(self, llm_service):
        """Test successful CV evaluation with OpenAI"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "technical_skills_match": 0.85,
            "experience_level": 0.8,
            "relevant_achievements": 0.7,
            "cultural_fit": 0.9,
            "cv_match_rate": 0.81,
            "cv_feedback": "Excellent technical skills"
        }
        '''
        
        with patch.object(llm_service, '_call_openai', return_value=mock_response.choices[0].message.content):
            with patch('app.services.llm_service.OPENAI_AVAILABLE', True):
                with patch('app.services.llm_service.settings.OPENAI_API_KEY', 'test-key'):
                    result = await llm_service.evaluate_cv("CV text", "Job requirements", LLMProvider.OPENAI)
                    
                    assert isinstance(result, CVEvaluation)
                    assert result.technical_skills_match == 0.85
                    assert result.cv_feedback == "Excellent technical skills"
    
    @pytest.mark.asyncio
    async def test_evaluate_cv_with_gemini_success(self, llm_service):
        """Test successful CV evaluation with Gemini"""
        mock_response = '''
        {
            "technical_skills_match": 0.75,
            "experience_level": 0.8,
            "relevant_achievements": 0.65,
            "cultural_fit": 0.85,
            "cv_match_rate": 0.76,
            "cv_feedback": "Good technical foundation"
        }
        '''
        
        with patch.object(llm_service, '_call_gemini', return_value=mock_response):
            with patch('app.services.llm_service.GEMINI_AVAILABLE', True):
                with patch('app.services.llm_service.settings.GEMINI_API_KEY', 'test-key'):
                    result = await llm_service.evaluate_cv("CV text", "Job requirements", LLMProvider.GEMINI)
                    
                    assert isinstance(result, CVEvaluation)
                    assert result.technical_skills_match == 0.75
                    assert result.cv_feedback == "Good technical foundation"
    
    @pytest.mark.asyncio
    async def test_evaluate_cv_with_mock_provider(self, llm_service):
        """Test CV evaluation with mock provider"""
        result = await llm_service.evaluate_cv("CV text", "Job requirements", LLMProvider.MOCK)
        
        assert isinstance(result, CVEvaluation)
        assert result.technical_skills_match == 0.82
        assert result.cv_feedback == "Strong in backend and cloud, limited AI integration experience."
    
    @pytest.mark.asyncio
    async def test_evaluate_cv_openai_api_error(self, llm_service):
        """Test CV evaluation with OpenAI API error"""
        with patch.object(llm_service, '_call_openai', side_effect=LLMServiceError("API Error")):
            with patch('app.services.llm_service.OPENAI_AVAILABLE', True):
                with patch('app.services.llm_service.settings.OPENAI_API_KEY', 'test-key'):
                    result = await llm_service.evaluate_cv("CV text", "Job requirements", LLMProvider.OPENAI)
                    
                    # Should fallback to mock data
                    assert isinstance(result, CVEvaluation)
                    assert result.technical_skills_match == 0.82
    
    @pytest.mark.asyncio
    async def test_evaluate_cv_gemini_api_error(self, llm_service):
        """Test CV evaluation with Gemini API error"""
        with patch.object(llm_service, '_call_gemini', side_effect=LLMServiceError("API Error")):
            with patch('app.services.llm_service.GEMINI_AVAILABLE', True):
                with patch('app.services.llm_service.settings.GEMINI_API_KEY', 'test-key'):
                    result = await llm_service.evaluate_cv("CV text", "Job requirements", LLMProvider.GEMINI)
                    
                    # Should fallback to mock data
                    assert isinstance(result, CVEvaluation)
                    assert result.technical_skills_match == 0.82
    
    @pytest.mark.asyncio
    async def test_evaluate_cv_invalid_json_response(self, llm_service):
        """Test CV evaluation with invalid JSON response"""
        with patch.object(llm_service, '_call_openai', return_value="Invalid JSON response"):
            with patch('app.services.llm_service.OPENAI_AVAILABLE', True):
                with patch('app.services.llm_service.settings.OPENAI_API_KEY', 'test-key'):
                    result = await llm_service.evaluate_cv("CV text", "Job requirements", LLMProvider.OPENAI)
                    
                    # Should fallback to mock data
                    assert isinstance(result, CVEvaluation)
                    assert result.technical_skills_match == 0.82
    
    @pytest.mark.asyncio
    async def test_evaluate_cv_no_provider_available(self, llm_service):
        """Test CV evaluation when no provider is available"""
        with patch('app.services.llm_service.OPENAI_AVAILABLE', False):
            with patch('app.services.llm_service.GEMINI_AVAILABLE', False):
                result = await llm_service.evaluate_cv("CV text", "Job requirements", LLMProvider.OPENAI)
                
                # Should fallback to mock data
                assert isinstance(result, CVEvaluation)
                assert result.technical_skills_match == 0.82
    
    @pytest.mark.asyncio
    async def test_evaluate_cv_fallback_to_mock(self, llm_service):
        """Test CV evaluation fallback to mock when no API keys"""
        with patch('app.services.llm_service.settings.OPENAI_API_KEY', None):
            with patch('app.services.llm_service.settings.GEMINI_API_KEY', None):
                result = await llm_service.evaluate_cv("CV text", "Job requirements", LLMProvider.OPENAI)
                
                # Should use mock data
                assert isinstance(result, CVEvaluation)
                assert result.technical_skills_match == 0.82
                assert result.cv_feedback == "Strong in backend and cloud, limited AI integration experience."
    
    def test_create_cv_prompt(self, llm_service):
        """Test CV evaluation prompt creation"""
        cv_text = "Software Engineer with 5 years experience"
        job_description = "Backend Developer position"
        
        prompt = llm_service._create_cv_evaluation_prompt(cv_text, job_description)
        
        assert cv_text in prompt
        assert job_description in prompt
        assert "technical_skills_match" in prompt
        assert "cv_match_rate" in prompt
    
    @pytest.mark.asyncio
    async def test_evaluate_cv_with_retry_mechanism(self, llm_service):
        """Test CV evaluation with retry mechanism"""
        # Mock first call fails, second succeeds
        mock_response = '''
        {
            "technical_skills_match": 0.8,
            "experience_level": 0.75,
            "relevant_achievements": 0.7,
            "cultural_fit": 0.85,
            "cv_match_rate": 0.78,
            "cv_feedback": "Solid technical background"
        }
        '''
        
        with patch.object(llm_service, '_call_openai', side_effect=[LLMServiceError("Temporary error"), mock_response]):
            with patch('app.services.llm_service.OPENAI_AVAILABLE', True):
                with patch('app.services.llm_service.settings.OPENAI_API_KEY', 'test-key'):
                    result = await llm_service.evaluate_cv("CV text", "Job requirements", LLMProvider.OPENAI)
                    
                    # Should fallback to mock on retry failure
                    assert isinstance(result, CVEvaluation)
                    assert result.technical_skills_match == 0.82
    
    @pytest.mark.asyncio
    async def test_evaluate_cv_empty_inputs(self, llm_service):
        """Test CV evaluation with empty inputs"""
        result = await llm_service.evaluate_cv("", "", LLMProvider.MOCK)
        
        assert isinstance(result, CVEvaluation)
        assert result.technical_skills_match == 0.82
        assert result.cv_feedback == "Strong in backend and cloud, limited AI integration experience."
    
    @pytest.mark.asyncio
    async def test_evaluate_cv_none_inputs(self, llm_service):
        """Test CV evaluation with None inputs"""
        # This should handle None gracefully and return mock data
        result = await llm_service.evaluate_cv(None, None, LLMProvider.MOCK)
        
        assert isinstance(result, CVEvaluation)
        assert result.technical_skills_match == 0.82
        assert result.cv_feedback == "Strong in backend and cloud, limited AI integration experience."