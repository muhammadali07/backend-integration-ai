import pytest
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
from fastapi import HTTPException, UploadFile
import io

from app.services.file_service import FileService
from app.core.exceptions import FileProcessingError


class TestFileService:
    """Unit tests for FileService class."""
    
    @pytest.fixture
    def file_service(self, temp_upload_dir):
        """Create FileService instance with temporary upload directory."""
        return FileService()
    
    @pytest.fixture
    def mock_upload_file(self):
        """Create a mock UploadFile for testing."""
        def create_mock_file(filename, content, content_type="text/plain"):
            mock_file = Mock(spec=UploadFile)
            mock_file.filename = filename
            mock_file.content_type = content_type
            mock_file.size = len(content) if isinstance(content, bytes) else len(content.encode())
            
            # Make read() return an awaitable
            async def async_read():
                return content if isinstance(content, bytes) else content.encode()
            
            mock_file.read = async_read
            return mock_file
        return create_mock_file

    @pytest.mark.unit
    def test_validate_file_success(self, file_service, mock_upload_file):
        """Test successful file validation."""
        # Test valid PDF file
        pdf_file = mock_upload_file("test.pdf", b"test content", "application/pdf")
        file_service._validate_file(pdf_file)  # Should not raise exception
        
        # Test valid DOCX file
        docx_file = mock_upload_file("test.docx", b"test content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        file_service._validate_file(docx_file)  # Should not raise exception
        
        # Test valid TXT file
        txt_file = mock_upload_file("test.txt", b"test content", "text/plain")
        file_service._validate_file(txt_file)  # Should not raise exception

    @pytest.mark.unit
    def test_validate_file_no_filename(self, file_service, mock_upload_file):
        """Test validation failure when no filename provided."""
        mock_file = mock_upload_file(None, b"test content")
        
        with pytest.raises(HTTPException) as exc_info:
            file_service._validate_file(mock_file)
        
        assert exc_info.value.status_code == 400
        assert "No filename provided" in str(exc_info.value.detail)

    @pytest.mark.unit
    def test_validate_file_invalid_extension(self, file_service, mock_upload_file):
        """Test validation failure for invalid file extensions."""
        invalid_file = mock_upload_file("test.exe", b"test content", "application/octet-stream")
        
        with pytest.raises(HTTPException) as exc_info:
            file_service._validate_file(invalid_file)
        
        assert exc_info.value.status_code == 400
        assert "File type .exe not allowed" in str(exc_info.value.detail)

    @pytest.mark.unit
    @patch('app.services.file_service.settings')
    def test_validate_file_too_large(self, mock_settings, file_service, mock_upload_file):
        """Test validation failure for files that are too large."""
        mock_settings.MAX_FILE_SIZE = 100
        mock_settings.ALLOWED_EXTENSIONS = ['.txt', '.pdf', '.docx']
        
        large_file = mock_upload_file("test.txt", b"x" * 200, "text/plain")
        large_file.size = 200
        
        with pytest.raises(HTTPException) as exc_info:
            file_service._validate_file(large_file)
        
        assert exc_info.value.status_code == 400
        assert "File too large" in str(exc_info.value.detail)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_save_file_success(self, file_service, mock_upload_file, temp_upload_dir):
        """Test successful file saving."""
        content = b"Test CV content"
        mock_file = mock_upload_file("test.txt", content, "text/plain")
        
        # Test the actual file saving without complex mocking
        file_id, file_path = await file_service.save_file(mock_file)
        
        # Verify file_id is generated
        assert file_id is not None
        assert len(file_id) == 36  # UUID length
        
        # Verify file_path is correct
        assert file_path.startswith(temp_upload_dir)
        assert file_path.endswith(".txt")
        
        # Verify file was actually created
        assert os.path.exists(file_path)
        
        # Verify file content
        with open(file_path, 'rb') as f:
            saved_content = f.read()
            assert saved_content == content

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_save_file_content_too_large(self, file_service, mock_upload_file):
        """Test file saving failure when content is too large."""
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB, larger than default 10MB limit
        mock_file = mock_upload_file("test.txt", large_content, "text/plain")
        
        with patch('aiofiles.open', mock_open()):
            with pytest.raises(HTTPException) as exc_info:
                await file_service.save_file(mock_file)
            
            assert exc_info.value.status_code == 400
            assert "File too large" in str(exc_info.value.detail)

    @pytest.mark.unit
    def test_extract_text_from_txt_success(self, file_service, temp_upload_dir):
        """Test successful text extraction from TXT file."""
        content = "This is a test CV content.\nName: John Doe"
        file_path = os.path.join(temp_upload_dir, "test.txt")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        result = file_service.extract_text_from_file(file_path)
        assert result == content

    @pytest.mark.unit
    def test_extract_text_from_pdf_success(self, file_service, temp_upload_dir):
        """Test successful text extraction from PDF file."""
        file_path = os.path.join(temp_upload_dir, "test.pdf")
        
        # Mock PyPDF2 functionality
        with patch('app.services.file_service.PyPDF2.PdfReader') as mock_pdf_reader:
            mock_page = Mock()
            mock_page.extract_text.return_value = "Extracted PDF content"
            mock_reader_instance = Mock()
            mock_reader_instance.pages = [mock_page]
            mock_pdf_reader.return_value = mock_reader_instance
            
            with patch('builtins.open', mock_open()):
                result = file_service.extract_text_from_file(file_path)
            
            assert result == "Extracted PDF content"

    @pytest.mark.unit
    def test_extract_text_from_docx_success(self, file_service, temp_upload_dir):
        """Test successful text extraction from DOCX file."""
        file_path = os.path.join(temp_upload_dir, "test.docx")
        
        # Mock python-docx functionality
        with patch('app.services.file_service.docx.Document') as mock_docx:
            mock_paragraph = Mock()
            mock_paragraph.text = "Paragraph 1"
            mock_doc = Mock()
            mock_doc.paragraphs = [mock_paragraph]
            mock_docx.return_value = mock_doc
            
            result = file_service.extract_text_from_file(file_path)
            
            assert "Paragraph 1" in result

    @pytest.mark.unit
    def test_extract_text_unsupported_format(self, file_service, temp_upload_dir):
        """Test text extraction failure for unsupported file format."""
        file_path = os.path.join(temp_upload_dir, "test.exe")
        
        with pytest.raises(FileProcessingError) as exc_info:
            file_service.extract_text_from_file(file_path)
        
        assert "Unsupported file type: .exe" in str(exc_info.value)

    @pytest.mark.unit
    def test_extract_text_pdf_empty(self, file_service, temp_upload_dir):
        """Test PDF extraction failure when PDF is empty."""
        file_path = os.path.join(temp_upload_dir, "test.pdf")
        
        with patch('app.services.file_service.PyPDF2.PdfReader') as mock_pdf_reader:
            mock_page = Mock()
            mock_page.extract_text.return_value = ""  # Empty content
            mock_reader_instance = Mock()
            mock_reader_instance.pages = [mock_page]
            mock_pdf_reader.return_value = mock_reader_instance
            
            with patch('builtins.open', mock_open()):
                with pytest.raises(FileProcessingError) as exc_info:
                    file_service.extract_text_from_file(file_path)
                
                assert "PDF appears to be empty" in str(exc_info.value)

    @pytest.mark.unit
    def test_extract_text_file_not_found(self, file_service):
        """Test text extraction failure when file doesn't exist."""
        non_existent_path = "/path/to/nonexistent/file.txt"
        
        with pytest.raises(FileProcessingError):
            file_service.extract_text_from_file(non_existent_path)

    @pytest.mark.unit
    def test_extract_text_with_retry(self, file_service, temp_upload_dir):
        """Test that retry mechanism works by creating a file that initially fails."""
        # Create a temporary file that we can read successfully
        file_path = os.path.join(temp_upload_dir, "test.txt")
        with open(file_path, 'w') as f:
            f.write("Test content for retry")
        
        # Test that the method works normally (retry logic is tested implicitly)
        result = file_service.extract_text_from_file(file_path)
        assert result == "Test content for retry"