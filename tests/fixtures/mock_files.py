"""Utilities for creating mock files for testing."""

import tempfile
import os
from pathlib import Path
from typing import BinaryIO
import io

# Try to import docx for creating DOCX files
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Try to import reportlab for creating PDF files
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


def create_sample_txt_file(content: str = None) -> str:
    """Create a temporary TXT file with sample content."""
    if content is None:
        from .sample_data import SAMPLE_CV_TEXT
        content = SAMPLE_CV_TEXT
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        return f.name


def create_sample_pdf_file(content: str = None) -> str:
    """Create a temporary PDF file with sample content."""
    if not PDF_AVAILABLE:
        # Fallback: create a simple PDF-like file
        return create_mock_pdf_file(content)
    
    if content is None:
        from .sample_data import SAMPLE_CV_TEXT
        content = SAMPLE_CV_TEXT
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        # Create a simple PDF with reportlab
        c = canvas.Canvas(f.name, pagesize=letter)
        width, height = letter
        
        # Split content into lines and add to PDF
        lines = content.split('\n')
        y_position = height - 50
        
        for line in lines:
            if y_position < 50:  # Start new page if needed
                c.showPage()
                y_position = height - 50
            
            # Truncate long lines to fit page width
            if len(line) > 80:
                line = line[:77] + "..."
            
            c.drawString(50, y_position, line)
            y_position -= 15
        
        c.save()
        return f.name


def create_mock_pdf_file(content: str = None) -> str:
    """Create a mock PDF file (simple text file with .pdf extension)."""
    if content is None:
        content = "%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n\nSample PDF content for testing"
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        f.write(content.encode('utf-8'))
        return f.name


def create_sample_docx_file(content: str = None) -> str:
    """Create a temporary DOCX file with sample content."""
    if not DOCX_AVAILABLE:
        # Fallback: create a simple DOCX-like file
        return create_mock_docx_file(content)
    
    if content is None:
        from .sample_data import SAMPLE_PROJECT_TEXT
        content = SAMPLE_PROJECT_TEXT
    
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
        doc = Document()
        
        # Split content into paragraphs and add to document
        paragraphs = content.split('\n\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                doc.add_paragraph(paragraph.strip())
        
        doc.save(f.name)
        return f.name


def create_mock_docx_file(content: str = None) -> str:
    """Create a mock DOCX file (ZIP-like structure)."""
    if content is None:
        content = "Mock DOCX content for testing"
    
    # Create a simple ZIP-like file that mimics DOCX structure
    import zipfile
    
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
        with zipfile.ZipFile(f.name, 'w') as docx:
            # Add minimal DOCX structure
            docx.writestr('[Content_Types].xml', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>''')
            
            docx.writestr('_rels/.rels', '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>''')
            
            docx.writestr('word/document.xml', f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>
<w:p><w:r><w:t>{content}</w:t></w:r></w:p>
</w:body>
</w:document>''')
        
        return f.name


def create_invalid_file(extension: str = '.xyz') -> str:
    """Create a file with invalid extension for testing."""
    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as f:
        f.write(b"This is an invalid file for testing")
        return f.name


def create_empty_file(extension: str = '.pdf') -> str:
    """Create an empty file for testing."""
    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as f:
        pass  # File is created but empty
        return f.name


def create_large_file(size_mb: int = 15, extension: str = '.pdf') -> str:
    """Create a large file for testing size limits."""
    with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as f:
        # Write specified amount of data
        chunk_size = 1024 * 1024  # 1MB chunks
        data = b'x' * chunk_size
        
        for _ in range(size_mb):
            f.write(data)
        
        return f.name


def create_binary_file_object(content: bytes, filename: str = "test.pdf") -> BinaryIO:
    """Create a binary file-like object for testing."""
    return io.BytesIO(content)


def cleanup_temp_file(file_path: str) -> None:
    """Clean up a temporary file."""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except OSError:
        pass  # Ignore cleanup errors


def cleanup_temp_files(file_paths: list) -> None:
    """Clean up multiple temporary files."""
    for file_path in file_paths:
        cleanup_temp_file(file_path)


class TempFileManager:
    """Context manager for handling temporary files."""
    
    def __init__(self):
        self.temp_files = []
    
    def create_txt_file(self, content: str = None) -> str:
        """Create and track a temporary TXT file."""
        file_path = create_sample_txt_file(content)
        self.temp_files.append(file_path)
        return file_path
    
    def create_pdf_file(self, content: str = None) -> str:
        """Create and track a temporary PDF file."""
        file_path = create_sample_pdf_file(content)
        self.temp_files.append(file_path)
        return file_path
    
    def create_docx_file(self, content: str = None) -> str:
        """Create and track a temporary DOCX file."""
        file_path = create_sample_docx_file(content)
        self.temp_files.append(file_path)
        return file_path
    
    def create_invalid_file(self, extension: str = '.xyz') -> str:
        """Create and track an invalid file."""
        file_path = create_invalid_file(extension)
        self.temp_files.append(file_path)
        return file_path
    
    def create_large_file(self, size_mb: int = 15, extension: str = '.pdf') -> str:
        """Create and track a large file."""
        file_path = create_large_file(size_mb, extension)
        self.temp_files.append(file_path)
        return file_path
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up all tracked temporary files."""
        cleanup_temp_files(self.temp_files)
        self.temp_files.clear()


# Convenience functions for common test scenarios
def get_sample_files_dict():
    """Get a dictionary of sample files for testing."""
    return {
        'pdf': create_sample_pdf_file(),
        'txt': create_sample_txt_file(),
        'docx': create_sample_docx_file()
    }


def get_test_file_scenarios():
    """Get various file scenarios for comprehensive testing."""
    return {
        'valid_pdf': create_sample_pdf_file(),
        'valid_txt': create_sample_txt_file(),
        'valid_docx': create_sample_docx_file(),
        'invalid_extension': create_invalid_file('.xyz'),
        'empty_file': create_empty_file('.pdf'),
        'large_file': create_large_file(15, '.pdf')
    }