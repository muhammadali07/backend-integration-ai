from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import UploadResponse
from app.services.file_service import file_service

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload CV or Project Report file
    
    Accepts: PDF, DOCX, TXT files
    Returns: File ID for later use in evaluation
    """
    try:
        file_id, file_path = await file_service.save_file(file)
        
        return UploadResponse(
            message="File uploaded successfully",
            file_id=file_id,
            filename=file.filename,
            file_size=len(await file.read()) if hasattr(file, 'read') else 0
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/upload/cv", response_model=UploadResponse)
async def upload_cv(file: UploadFile = File(...)):
    """
    Upload CV file specifically
    
    Accepts: PDF, DOCX, TXT files
    Returns: File ID for later use in evaluation
    """
    return await upload_file(file)

@router.post("/upload/project", response_model=UploadResponse)
async def upload_project_report(file: UploadFile = File(...)):
    """
    Upload Project Report file specifically
    
    Accepts: PDF, DOCX, TXT files
    Returns: File ID for later use in evaluation
    """
    return await upload_file(file)