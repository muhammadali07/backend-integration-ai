import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from app.models.schemas import (
    EvaluationRequest, 
    EvaluationResult, 
    JobStatus, 
    LLMProvider,
    CompleteEvaluationResult
)
from app.services.file_service import file_service
from app.services.llm_service import llm_service
from app.services.vector_service import vector_service

class EvaluationService:
    def __init__(self):
        # In-memory storage for evaluation jobs (in production, use Redis or database)
        self.jobs: Dict[str, EvaluationResult] = {}
    
    async def start_evaluation(self, request: EvaluationRequest) -> str:
        """Start asynchronous evaluation process"""
        job_id = str(uuid.uuid4())
        
        # Create job record
        job = EvaluationResult(
            id=job_id,
            status=JobStatus.QUEUED,
            created_at=datetime.now()
        )
        self.jobs[job_id] = job
        
        # Start evaluation in background
        asyncio.create_task(self._process_evaluation(job_id, request))
        
        return job_id
    
    async def _process_evaluation(self, job_id: str, request: EvaluationRequest):
        """Process evaluation in background"""
        try:
            # Update status to processing
            self.jobs[job_id].status = JobStatus.PROCESSING
            
            # Extract text from uploaded files
            cv_text = ""
            project_text = ""
            
            if request.cv_file_id:
                cv_text = await self._extract_file_text(request.cv_file_id)
            
            if request.project_report_file_id:
                project_text = await self._extract_file_text(request.project_report_file_id)
            
            # Get enhanced context from vector database
            enhanced_job_description = vector_service.get_job_description_context(request.job_description)
            cv_scoring_context = vector_service.get_scoring_rubric_context("cv")
            project_scoring_context = vector_service.get_scoring_rubric_context("project")
            
            # Perform evaluations
            cv_result = {}
            project_result = {}
            
            if cv_text:
                cv_result = await llm_service.evaluate_cv(
                    cv_text=cv_text,
                    job_description=f"{enhanced_job_description}\n\nScoring Guidelines:\n{cv_scoring_context}",
                    provider=request.llm_provider
                )
            
            if project_text and request.study_case_brief:
                project_result = await llm_service.evaluate_project(
                    project_text=project_text,
                    study_case_brief=f"{request.study_case_brief}\n\nScoring Guidelines:\n{project_scoring_context}",
                    provider=request.llm_provider
                )
            
            # Generate overall summary
            overall_summary = await llm_service.generate_overall_summary(
                cv_result=cv_result,
                project_result=project_result,
                provider=request.llm_provider
            )
            
            # Combine results
            complete_result = CompleteEvaluationResult(
                cv_match_rate=cv_result.get("cv_match_rate", 0.0),
                cv_feedback=cv_result.get("cv_feedback", "No CV evaluation performed"),
                project_score=project_result.get("project_score", 0.0),
                project_feedback=project_result.get("project_feedback", "No project evaluation performed"),
                overall_summary=overall_summary
            )
            
            # Update job with results
            self.jobs[job_id].status = JobStatus.COMPLETED
            self.jobs[job_id].completed_at = datetime.now()
            self.jobs[job_id].result = complete_result.dict()
            
        except Exception as e:
            # Handle errors
            self.jobs[job_id].status = JobStatus.FAILED
            self.jobs[job_id].error_message = str(e)
            self.jobs[job_id].completed_at = datetime.now()
    
    async def _extract_file_text(self, file_id: str) -> str:
        """Extract text from uploaded file"""
        try:
            # Try different file extensions
            for ext in ['.pdf', '.docx', '.txt']:
                file_path = file_service.get_file_path(file_id, ext)
                try:
                    return file_service.extract_text(file_path)
                except:
                    continue
            
            raise Exception(f"Could not find or read file with ID: {file_id}")
        
        except Exception as e:
            raise Exception(f"Failed to extract text from file {file_id}: {str(e)}")
    
    def get_evaluation_result(self, job_id: str) -> Optional[EvaluationResult]:
        """Get evaluation result by job ID"""
        return self.jobs.get(job_id)
    
    def get_all_jobs(self) -> Dict[str, EvaluationResult]:
        """Get all evaluation jobs (for debugging)"""
        return self.jobs
    
    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Clean up old completed jobs"""
        current_time = datetime.now()
        jobs_to_remove = []
        
        for job_id, job in self.jobs.items():
            if job.completed_at:
                age_hours = (current_time - job.completed_at).total_seconds() / 3600
                if age_hours > max_age_hours:
                    jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.jobs[job_id]
    
    def get_job_statistics(self) -> Dict[str, Any]:
        """Get job statistics"""
        total_jobs = len(self.jobs)
        status_counts = {}
        
        for job in self.jobs.values():
            status = job.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_jobs": total_jobs,
            "status_breakdown": status_counts
        }

# Global instance
evaluation_service = EvaluationService()