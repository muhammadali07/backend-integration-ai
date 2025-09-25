import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import logging
from app.core.config import settings
from app.core.exceptions import VectorDatabaseError
from app.core.retry import retry_sync, VECTOR_DB_RETRY_CONFIG

class VectorService:
    def __init__(self):
        """Initialize ChromaDB client with error handling"""
        try:
            self.client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            self.collection = self._get_or_create_collection()
            self._initialize_default_data()
            logging.info("Vector database initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize vector database: {str(e)}")
            raise VectorDatabaseError(f"Vector database initialization failed: {str(e)}")
    
    @retry_sync(VECTOR_DB_RETRY_CONFIG)
    def _get_or_create_collection(self):
        """Get or create the main collection with retry logic"""
        try:
            return self.client.get_or_create_collection(
                name="job_requirements",
                metadata={"description": "Job descriptions and evaluation criteria"}
            )
        except Exception as e:
            logging.error(f"Failed to get/create collection: {str(e)}")
            raise VectorDatabaseError(f"Collection creation failed: {str(e)}")
    
    def _initialize_default_data(self):
        """Initialize collection with default job descriptions and scoring rubrics"""
        default_data = [
            {
                "id": "backend_job_desc_1",
                "content": """
                Backend Developer Position:
                - 3+ years experience in backend development
                - Proficiency in Python, Node.js, or similar languages
                - Experience with REST APIs and microservices
                - Database experience (SQL/NoSQL)
                - Cloud platforms (AWS, GCP, Azure)
                - Understanding of AI/ML integration is a plus
                - Strong problem-solving and communication skills
                """,
                "type": "job_description",
                "category": "backend_developer"
            },
            {
                "id": "cv_scoring_rubric",
                "content": """
                CV Evaluation Scoring Rubric:
                
                Technical Skills Match (0.0-1.0):
                - 0.9-1.0: Expert level in required technologies
                - 0.7-0.8: Strong proficiency with most requirements
                - 0.5-0.6: Moderate skills, some gaps
                - 0.3-0.4: Basic skills, significant gaps
                - 0.0-0.2: Minimal relevant skills
                
                Experience Level (0.0-1.0):
                - 0.9-1.0: 5+ years relevant experience
                - 0.7-0.8: 3-4 years relevant experience
                - 0.5-0.6: 1-2 years relevant experience
                - 0.3-0.4: <1 year relevant experience
                - 0.0-0.2: No relevant experience
                """,
                "type": "scoring_rubric",
                "category": "cv_evaluation"
            },
            {
                "id": "project_scoring_rubric",
                "content": """
                Project Evaluation Scoring Rubric (1-5 scale):
                
                Correctness (1-5):
                - 5: Fully meets all requirements with excellent implementation
                - 4: Meets most requirements with good implementation
                - 3: Meets basic requirements with acceptable implementation
                - 2: Partially meets requirements with some issues
                - 1: Fails to meet most requirements
                
                Code Quality (1-5):
                - 5: Clean, well-structured, highly maintainable code
                - 4: Good structure with minor improvements needed
                - 3: Acceptable structure with some refactoring needed
                - 2: Poor structure, difficult to maintain
                - 1: Very poor code quality, major issues
                """,
                "type": "scoring_rubric",
                "category": "project_evaluation"
            }
        ]
        
        try:
            ids = [item["id"] for item in default_data]
            documents = [item["content"] for item in default_data]
            metadatas = [{"type": item["type"], "category": item["category"]} for item in default_data]
            
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            print("Initialized vector database with default data")
        except Exception as e:
            print(f"Failed to initialize default data: {str(e)}")
    
    def add_job_description(self, job_id: str, job_description: str, category: str = "general") -> bool:
        """Add job description to vector database"""
        if not self.collection:
            return False
        
        try:
            self.collection.add(
                ids=[job_id],
                documents=[job_description],
                metadatas=[{"type": "job_description", "category": category}]
            )
            return True
        except Exception as e:
            print(f"Failed to add job description: {str(e)}")
            return False
    
    def add_scoring_rubric(self, rubric_id: str, rubric_content: str, category: str = "general") -> bool:
        """Add scoring rubric to vector database"""
        if not self.collection:
            return False
        
        try:
            self.collection.add(
                ids=[rubric_id],
                documents=[rubric_content],
                metadatas=[{"type": "scoring_rubric", "category": category}]
            )
            return True
        except Exception as e:
            print(f"Failed to add scoring rubric: {str(e)}")
            return False
    
    @retry_sync(VECTOR_DB_RETRY_CONFIG)
    def search_context(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant context with retry logic and fallback"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            if not results["documents"] or not results["documents"][0]:
                logging.warning("No results found in vector search, using fallback context")
                return self._get_fallback_context()
            
            context_items = []
            for i, doc in enumerate(results["documents"][0]):
                context_items.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"][0] else {},
                    "distance": results["distances"][0][i] if results["distances"][0] else 1.0
                })
            
            return context_items
            
        except Exception as e:
            logging.warning(f"Vector search failed, using fallback context: {str(e)}")
            return self._get_fallback_context()

    def _get_fallback_context(self) -> List[Dict[str, Any]]:
        """Provide fallback context when vector search fails"""
        return [
            {
                "content": "General software engineering skills: programming languages, problem-solving, system design, testing, debugging, version control, and collaboration.",
                "metadata": {"type": "fallback", "category": "general_skills"},
                "distance": 0.5
            },
            {
                "content": "Technical evaluation criteria: code quality, architecture design, documentation, testing coverage, performance optimization, and best practices.",
                "metadata": {"type": "fallback", "category": "evaluation_criteria"},
                "distance": 0.5
            }
        ]
    
    def get_job_description_context(self, job_description: str) -> str:
        """Get relevant job description context for evaluation"""
        results = self.search_relevant_context(
            query=job_description,
            context_type="job_description",
            n_results=2
        )
        
        if not results:
            return job_description
        
        # Combine original job description with similar ones
        context = f"Primary Job Description:\n{job_description}\n\n"
        context += "Similar Job Requirements:\n"
        for result in results:
            context += f"- {result['content']}\n"
        
        return context
    
    def get_scoring_rubric_context(self, evaluation_type: str) -> str:
        """Get relevant scoring rubric for evaluation type"""
        results = self.search_relevant_context(
            query=f"{evaluation_type} evaluation scoring",
            context_type="scoring_rubric",
            n_results=2
        )
        
        if not results:
            return "Use standard evaluation criteria."
        
        context = "Scoring Guidelines:\n"
        for result in results:
            context += f"{result['content']}\n\n"
        
        return context
    
    def health_check(self) -> Dict[str, Any]:
        """Check vector database health"""
        if not self.client or not self.collection:
            return {"status": "unhealthy", "error": "ChromaDB not initialized"}
        
        try:
            count = self.collection.count()
            return {
                "status": "healthy",
                "document_count": count,
                "collection_name": self.collection.name
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

# Global instance
vector_service = VectorService()