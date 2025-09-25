from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import logging
from typing import Any, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EvaluationError(Exception):
    """Base exception for evaluation-related errors"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class FileProcessingError(EvaluationError):
    """Exception raised when file processing fails"""
    pass

class LLMServiceError(EvaluationError):
    """Exception raised when LLM service fails"""
    pass

class VectorDatabaseError(EvaluationError):
    """Exception raised when vector database operations fail"""
    pass

class ValidationError(EvaluationError):
    """Exception raised when input validation fails"""
    pass

# Global exception handlers
async def evaluation_exception_handler(request: Request, exc: EvaluationError):
    """Handle custom evaluation exceptions"""
    logger.error(f"Evaluation error: {exc.message}", extra={"details": exc.details})
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Evaluation Error",
            "message": exc.message,
            "details": exc.details,
            "type": exc.__class__.__name__
        }
    )

async def file_processing_exception_handler(request: Request, exc: FileProcessingError):
    """Handle file processing exceptions"""
    logger.error(f"File processing error: {exc.message}", extra={"details": exc.details})
    
    return JSONResponse(
        status_code=400,
        content={
            "error": "File Processing Error",
            "message": exc.message,
            "details": exc.details
        }
    )

async def llm_service_exception_handler(request: Request, exc: LLMServiceError):
    """Handle LLM service exceptions"""
    logger.error(f"LLM service error: {exc.message}", extra={"details": exc.details})
    
    return JSONResponse(
        status_code=503,
        content={
            "error": "LLM Service Error",
            "message": "AI service temporarily unavailable. Using fallback evaluation.",
            "details": {"original_error": exc.message}
        }
    )

async def vector_database_exception_handler(request: Request, exc: VectorDatabaseError):
    """Handle vector database exceptions"""
    logger.warning(f"Vector database error: {exc.message}", extra={"details": exc.details})
    
    return JSONResponse(
        status_code=503,
        content={
            "error": "Vector Database Error",
            "message": "Context retrieval service temporarily unavailable. Using basic evaluation.",
            "details": {"original_error": exc.message}
        }
    )

async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle validation exceptions"""
    logger.warning(f"Validation error: {exc.message}", extra={"details": exc.details})
    
    return JSONResponse(
        status_code=400,
        content={
            "error": "Validation Error",
            "message": exc.message,
            "details": exc.details
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "request_id": getattr(request.state, 'request_id', 'unknown')
        }
    )