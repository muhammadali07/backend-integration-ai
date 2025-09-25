from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid
from datetime import datetime

class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class LLMProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    MOCK = "mock"

class UploadResponse(BaseModel):
    message: str
    file_id: str
    filename: str
    file_size: int

class EvaluationRequest(BaseModel):
    cv_file_id: Optional[str] = None
    project_report_file_id: Optional[str] = None
    job_description: str = Field(..., description="Job vacancy description")
    study_case_brief: Optional[str] = Field(None, description="Study case brief for project evaluation")
    llm_provider: Optional[LLMProvider] = LLMProvider.OPENAI

class EvaluationResponse(BaseModel):
    id: str
    status: JobStatus
    message: str = "Evaluation job created successfully"

class CVEvaluation(BaseModel):
    technical_skills_match: float = Field(..., ge=0, le=1)
    experience_level: float = Field(..., ge=0, le=1)
    relevant_achievements: float = Field(..., ge=0, le=1)
    cultural_fit: float = Field(..., ge=0, le=1)
    cv_match_rate: float = Field(..., ge=0, le=1)
    cv_feedback: str

class ProjectEvaluation(BaseModel):
    correctness: float = Field(..., ge=1, le=5)
    code_quality: float = Field(..., ge=1, le=5)
    resilience: float = Field(..., ge=1, le=5)
    documentation: float = Field(..., ge=1, le=5)
    creativity_bonus: float = Field(..., ge=1, le=5)
    project_score: float = Field(..., ge=1, le=5)
    project_feedback: str

class EvaluationResult(BaseModel):
    id: str
    status: JobStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class CompleteEvaluationResult(BaseModel):
    cv_match_rate: float
    cv_feedback: str
    project_score: float
    project_feedback: str
    overall_summary: str

class ResultResponse(BaseModel):
    id: str
    status: JobStatus
    result: Optional[CompleteEvaluationResult] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None