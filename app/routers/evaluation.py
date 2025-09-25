from fastapi import APIRouter, HTTPException
from app.models.schemas import EvaluationRequest, EvaluationResponse, JobStatus
from app.services.evaluation_service import evaluation_service

router = APIRouter()

@router.post("/evaluate", response_model=EvaluationResponse)
async def start_evaluation(request: EvaluationRequest):
    """
    Start candidate evaluation process
    
    This endpoint accepts CV and/or project report file IDs along with job requirements
    and starts an asynchronous evaluation process using AI/LLM analysis.
    
    Returns a job ID that can be used to check evaluation status and results.
    """
    try:
        # Validate that at least one file is provided
        if not request.cv_file_id and not request.project_report_file_id:
            raise HTTPException(
                status_code=400, 
                detail="At least one file (CV or project report) must be provided"
            )
        
        # Validate job description
        if not request.job_description.strip():
            raise HTTPException(
                status_code=400,
                detail="Job description is required"
            )
        
        # Start evaluation process
        job_id = await evaluation_service.start_evaluation(request)
        
        return EvaluationResponse(
            id=job_id,
            status=JobStatus.QUEUED,
            message="Evaluation job created successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to start evaluation: {str(e)}"
        )

@router.get("/evaluate/stats")
async def get_evaluation_stats():
    """
    Get evaluation job statistics
    
    Returns statistics about evaluation jobs for monitoring purposes.
    """
    try:
        stats = evaluation_service.get_job_statistics()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statistics: {str(e)}"
        )