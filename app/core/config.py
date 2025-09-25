import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # File upload settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx", ".txt"]
    
    # Vector DB settings
    CHROMA_PERSIST_DIR: str = "chroma_db"
    
    # LLM settings
    DEFAULT_LLM_PROVIDER: str = "openai"  # or "gemini" or "mock"
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    GEMINI_MODEL: str = "gemini-pro"
    
    class Config:
        env_file = ".env"

settings = Settings()