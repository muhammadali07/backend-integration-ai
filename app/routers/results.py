from fastapi import APIRouter, HTTPException, Path
from app.models.schemas import ResultResponse, JobStatus, CompleteEvaluationResult
from app.services.evaluation_service import evaluation_service

router = APIRouter()

@router.get("/result/{job_id}", response_model=ResultResponse)
async def get_evaluation_result(
    job_id: str = Path(..., description="Evaluation job ID")
):
    """
    Get evaluation result by job ID
    
    Returns the current status and results (if completed) of an evaluation job.
    
    Status can be:
    - queued: Job is waiting to be processed
    - processing: Job is currently being evaluated
    - completed: Job finished successfully with results
    - failed: Job failed with error message
    """
    try:
        # Get job from evaluation service
        job = evaluation_service.get_evaluation_result(job_id)
        
        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Evaluation job with ID '{job_id}' not found"
            )
        
        # Prepare response
        result = None
        if job.status == JobStatus.COMPLETED and job.result:
            result = CompleteEvaluationResult(**job.result)
        
        return ResultResponse(
            id=job.id,
            status=job.status,
            result=result,
            error_message=job.error_message,
            created_at=job.created_at,
            completed_at=job.completed_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve evaluation result: {str(e)}"
        )

@router.get("/results")
async def get_all_results():
    """
    Get all evaluation results (for debugging/admin purposes)
    
    Returns a list of all evaluation jobs with their current status.
    """
    try:
        jobs = evaluation_service.get_all_jobs()
        
        results = []
        for job_id, job in jobs.items():
            result = None
            if job.status == JobStatus.COMPLETED and job.result:
                result = CompleteEvaluationResult(**job.result)
            
            results.append(ResultResponse(
                id=job.id,
                status=job.status,
                result=result,
                error_message=job.error_message,
                created_at=job.created_at,
                completed_at=job.completed_at
            ))
        
        return {"total": len(results), "results": results}
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve all results: {str(e)}"
        )

@router.delete("/result/{job_id}")
async def delete_evaluation_result(
    job_id: str = Path(..., description="Evaluation job ID")
):
    """
    Delete evaluation result by job ID
    
    Removes the evaluation job and its results from memory.
    """
    try:
        jobs = evaluation_service.get_all_jobs()
        
        if job_id not in jobs:
            raise HTTPException(
                status_code=404,
                detail=f"Evaluation job with ID '{job_id}' not found"
            )
        
        del jobs[job_id]
        
        return {"message": f"Evaluation job '{job_id}' deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete evaluation result: {str(e)}"
        )