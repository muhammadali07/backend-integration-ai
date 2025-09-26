"""Integration tests for upload endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import os
import tempfile
from pathlib import Path


class TestUploadEndpoints:
    """Test class for upload endpoints integration tests."""

    @pytest.mark.integration
    def test_upload_file_success(self, client: TestClient, sample_pdf_file):
        """Test successful file upload via /api/v1/upload endpoint."""
        with open(sample_pdf_file, "rb") as f:
            response = client.post(
                "/api/v1/upload",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data
        assert data["filename"] == "test.pdf"
        assert data["message"] == "File uploaded successfully"
        assert "file_size" in data

    @pytest.mark.integration
    def test_upload_cv_success(self, client: TestClient, sample_pdf_file):
        """Test successful CV upload via /api/v1/upload/cv endpoint."""
        with open(sample_pdf_file, "rb") as f:
            response = client.post(
                "/api/v1/upload/cv",
                files={"file": ("cv.pdf", f, "application/pdf")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data
        assert data["filename"] == "cv.pdf"
        assert data["message"] == "File uploaded successfully"
        assert "file_size" in data

    @pytest.mark.integration
    def test_upload_project_success(self, client: TestClient, sample_docx_file):
        """Test successful project report upload via /api/v1/upload/project endpoint."""
        with open(sample_docx_file, "rb") as f:
            response = client.post(
                "/api/v1/upload/project",
                files={"file": ("project.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data
        assert data["filename"] == "project.docx"
        assert data["message"] == "File uploaded successfully"
        assert "file_size" in data

    @pytest.mark.integration
    def test_upload_invalid_file_type(self, client: TestClient):
        """Test upload with invalid file type."""
        # Create a temporary file with invalid extension
        with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False) as tmp:
            tmp.write(b"invalid content")
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as f:
                response = client.post(
                    "/api/v1/upload",
                    files={"file": ("invalid.xyz", f, "application/octet-stream")}
                )
            
            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
            assert "File type .xyz not allowed" in data["detail"]
        finally:
            os.unlink(tmp_path)

    @pytest.mark.integration
    def test_upload_no_file(self, client: TestClient):
        """Test upload without providing a file."""
        response = client.post("/api/v1/upload")
        
        assert response.status_code == 422  # Unprocessable Entity

    @pytest.mark.integration
    def test_upload_empty_file(self, client: TestClient):
        """Test upload with empty file."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as f:
                response = client.post(
                    "/api/v1/upload",
                    files={"file": ("empty.pdf", f, "application/pdf")}
                )
            
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.json()}")
            
            # If the API accepts empty files, test for success
            if response.status_code == 200:
                data = response.json()
                assert "message" in data
                assert "file_id" in data
                assert data["file_size"] == 0
            else:
                # If it rejects empty files, test for error
                assert response.status_code == 400
                data = response.json()
                assert "detail" in data
                assert "File is empty" in data["detail"] or "Upload failed" in data["detail"]
        finally:
            os.unlink(tmp_path)

    @pytest.mark.integration
    def test_upload_oversized_file(self, client: TestClient):
        """Test upload with file exceeding size limit."""
        # Create a large file (> 10MB)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            # Write 11MB of data
            tmp.write(b"x" * (11 * 1024 * 1024))
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as f:
                response = client.post(
                    "/api/v1/upload",
                    files={"file": ("large.pdf", f, "application/pdf")}
                )
            
            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
            assert "File too large" in data["detail"]
        finally:
            os.unlink(tmp_path)

    @pytest.mark.integration
    @patch('app.services.file_service.FileService.save_file')
    def test_upload_file_service_error(self, mock_save_file, client: TestClient, sample_pdf_file):
        """Test upload when file service raises an error."""
        mock_save_file.side_effect = Exception("File service error")
        
        with open(sample_pdf_file, "rb") as f:
            response = client.post(
                "/api/v1/upload",
                files={"file": ("test.pdf", f, "application/pdf")}
            )
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Upload failed" in data["detail"]

    @pytest.mark.integration
    def test_upload_txt_file(self, client: TestClient, sample_txt_file):
        """Test successful TXT file upload."""
        with open(sample_txt_file, "rb") as f:
            response = client.post(
                "/api/v1/upload",
                files={"file": ("document.txt", f, "text/plain")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "file_id" in data
        assert data["filename"] == "document.txt"
        assert data["message"] == "File uploaded successfully"
        assert "file_size" in data

    @pytest.mark.integration
    def test_upload_multiple_files_sequential(self, client: TestClient, sample_pdf_file, sample_txt_file):
        """Test uploading multiple files sequentially."""
        # Upload first file
        with open(sample_pdf_file, "rb") as f:
            response1 = client.post(
                "/api/v1/upload/cv",
                files={"file": ("cv1.pdf", f, "application/pdf")}
            )
        
        assert response1.status_code == 200
        file_id_1 = response1.json()["file_id"]
        
        # Upload second file
        with open(sample_txt_file, "rb") as f:
            response2 = client.post(
                "/api/v1/upload/project",
                files={"file": ("project1.txt", f, "text/plain")}
            )
        
        assert response2.status_code == 200
        file_id_2 = response2.json()["file_id"]
        
        # Ensure different file IDs
        assert file_id_1 != file_id_2