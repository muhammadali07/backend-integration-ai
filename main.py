from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging

from app.routers import upload, evaluation, results
from app.core.exceptions import (
    EvaluationError, FileProcessingError, LLMServiceError, 
    VectorDatabaseError, ValidationError,
    evaluation_exception_handler, file_processing_exception_handler,
    llm_service_exception_handler, vector_database_exception_handler,
    validation_exception_handler, general_exception_handler
)
from app.core.config import settings

app = FastAPI(
    title="Candidate Evaluation Backend",
    description="AI-powered candidate evaluation system using LLM and vector database",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(EvaluationError, evaluation_exception_handler)
app.add_exception_handler(FileProcessingError, file_processing_exception_handler)
app.add_exception_handler(LLMServiceError, llm_service_exception_handler)
app.add_exception_handler(VectorDatabaseError, vector_database_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(evaluation.router, prefix="/api/v1", tags=["evaluation"])
app.include_router(results.router, prefix="/api/v1", tags=["results"])

@app.get("/")
async def root():
    return {"message": "Candidate Evaluation API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )