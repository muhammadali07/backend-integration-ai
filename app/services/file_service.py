import os
import uuid
from pathlib import Path
from typing import Optional, List
import logging
from fastapi import UploadFile, HTTPException
import PyPDF2
import docx
import aiofiles
from app.core.config import settings
from app.core.exceptions import FileProcessingError
from app.core.retry import retry_sync, FILE_PROCESSING_RETRY_CONFIG

class FileService:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def _validate_file(self, file: UploadFile) -> None:
        """Validate uploaded file"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_ext} not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Check file size (this is approximate, actual size check happens during upload)
        if hasattr(file, 'size') and file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
            )
    
    async def save_file(self, file: UploadFile) -> tuple[str, str]:
        """Save uploaded file and return file_id and file_path"""
        self._validate_file(file)
        
        # Generate unique file ID and path
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1].lower()
        file_path = os.path.join(self.upload_dir, f"{file_id}{file_ext}")
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
                )
            await f.write(content)
        
        return file_id, file_path
    
    @retry_sync(FILE_PROCESSING_RETRY_CONFIG)
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from uploaded file with retry logic"""
        try:
            file_extension = Path(file_path).suffix.lower()
            
            if file_extension == '.pdf':
                return self._extract_from_pdf(file_path)
            elif file_extension == '.docx':
                return self._extract_from_docx(file_path)
            elif file_extension == '.txt':
                return self._extract_from_txt(file_path)
            else:
                raise FileProcessingError(f"Unsupported file type: {file_extension}")
                
        except FileProcessingError:
            raise
        except Exception as e:
            logging.error(f"Text extraction failed for {file_path}: {str(e)}")
            raise FileProcessingError(f"Failed to extract text from file: {str(e)}", {"file_path": file_path})

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                if not text.strip():
                    raise FileProcessingError("PDF appears to be empty or contains only images")
                
                return text.strip()
        except Exception as e:
            raise FileProcessingError(f"PDF extraction failed: {str(e)}")

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            if not text.strip():
                raise FileProcessingError("DOCX file appears to be empty")
            
            return text.strip()
        except Exception as e:
            raise FileProcessingError(f"DOCX extraction failed: {str(e)}")

    def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            if not text.strip():
                raise FileProcessingError("TXT file is empty")
            
            return text.strip()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    text = file.read()
                return text.strip()
            except Exception as e:
                raise FileProcessingError(f"TXT file encoding error: {str(e)}")
        except Exception as e:
            raise FileProcessingError(f"TXT extraction failed: {str(e)}")
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from file based on extension"""
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return self.extract_text_from_file(file_path)
    
    def get_file_path(self, file_id: str, file_ext: str) -> str:
        """Get file path from file_id"""
        return os.path.join(self.upload_dir, f"{file_id}{file_ext}")
    
    def delete_file(self, file_path: str) -> None:
        """Delete file from filesystem"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            # Log error but don't raise exception for cleanup operations
            print(f"Error deleting file {file_path}: {str(e)}")

# Global instance
file_service = FileService()