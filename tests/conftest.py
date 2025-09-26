import pytest
import tempfile
import os
from pathlib import Path
import httpx
from unittest.mock import Mock, patch
import asyncio

from app.core.config import settings
from main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture
def temp_upload_dir():
    """Create a temporary directory for file uploads during testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_upload_dir = settings.UPLOAD_DIR
        settings.UPLOAD_DIR = temp_dir
        yield temp_dir
        settings.UPLOAD_DIR = original_upload_dir


@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing."""
    content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n178\n%%EOF"
    
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        temp_file.write(content)
        temp_file.flush()
        yield temp_file.name
    
    # Clean up the temporary file
    try:
        os.unlink(temp_file.name)
    except FileNotFoundError:
        pass


@pytest.fixture
def sample_txt_file():
    """Create a sample text file for testing."""
    content = b"This is a sample CV content.\nName: John Doe\nExperience: 5 years in software development."
    
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
        temp_file.write(content)
        temp_file.flush()
        yield temp_file.name
    
    # Clean up the temporary file
    try:
        os.unlink(temp_file.name)
    except FileNotFoundError:
        pass


@pytest.fixture
def sample_docx_file():
    """Create a sample DOCX file for testing."""
    # Minimal DOCX structure
    content = b"PK\x03\x04\x14\x00\x00\x00\x08\x00"
    
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_file:
        temp_file.write(content)
        temp_file.flush()
        yield temp_file.name
    
    # Clean up the temporary file
    try:
        os.unlink(temp_file.name)
    except FileNotFoundError:
        pass


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "technical_skills": {
            "score": 85,
            "feedback": "Strong technical background in Python and web development"
        },
        "experience": {
            "score": 75,
            "feedback": "Good experience level for the position"
        },
        "education": {
            "score": 80,
            "feedback": "Relevant educational background"
        },
        "overall_score": 80,
        "recommendation": "Recommended for interview",
        "strengths": ["Technical skills", "Problem solving"],
        "areas_for_improvement": ["Communication skills"]
    }


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"overall_score": 80, "recommendation": "Recommended"}'
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini client for testing."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.text = '{"overall_score": 75, "recommendation": "Consider for interview"}'
    mock_client.generate_content.return_value = mock_response
    return mock_client


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    original_env = {}
    test_env = {
        "OPENAI_API_KEY": "test_openai_key",
        "GEMINI_API_KEY": "test_gemini_key",
        "DEFAULT_LLM_PROVIDER": "mock",
        "DEBUG": "true"
    }
    
    # Store original values
    for key in test_env:
        original_env[key] = os.environ.get(key)
        os.environ[key] = test_env[key]
    
    yield
    
    # Restore original values
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value