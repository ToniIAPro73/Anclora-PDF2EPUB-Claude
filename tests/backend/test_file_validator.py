"""
Tests for enhanced file validation system
Sprint 1.3 - File Validation
"""
import os
import tempfile
import pytest
from io import BytesIO
from unittest.mock import Mock, patch
import sys
import io

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from file_validator import FileSecurityValidator, FileValidationConfig


class TestFileSecurityValidator:
    """Test suite for FileSecurityValidator"""
    
    def create_mock_file(self, filename="test.pdf", content=b"%PDF-1.4\ntest content", size=None):
        """Create a mock file object for testing"""
        if size is not None:
            content = b"%PDF-1.4\n" + b"x" * (size - 10)
        
        file_obj = BytesIO(content)
        file_obj.filename = filename
        file_obj.name = filename
        return file_obj
    
    def test_validate_file_presence_success(self):
        """Test successful file presence validation"""
        files = {'file': self.create_mock_file()}
        valid, error, status = FileSecurityValidator.validate_file_presence(files)
        assert valid is True
        assert error is None
        assert status is None
    
    def test_validate_file_presence_missing(self):
        """Test missing file validation"""
        files = {}
        valid, error, status = FileSecurityValidator.validate_file_presence(files)
        assert valid is False
        assert error['error'] == 'No file part in request'
        assert status == 400
    
    def test_validate_filename_success(self):
        """Test successful filename validation"""
        file_obj = self.create_mock_file("valid_document.pdf")
        valid, error, status = FileSecurityValidator.validate_filename(file_obj)
        assert valid is True
        assert error is None
        assert status is None
    
    def test_validate_filename_empty(self):
        """Test empty filename validation"""
        file_obj = self.create_mock_file("")
        valid, error, status = FileSecurityValidator.validate_filename(file_obj)
        assert valid is False
        assert error['error'] == 'No file selected'
        assert status == 400
    
    def test_validate_filename_too_long(self):
        """Test filename too long validation"""
        long_filename = "a" * 300 + ".pdf"
        file_obj = self.create_mock_file(long_filename)
        valid, error, status = FileSecurityValidator.validate_filename(file_obj)
        assert valid is False
        assert 'too long' in error['error']
        assert status == 400
    
    def test_validate_filename_suspicious_patterns(self):
        """Test suspicious filename patterns"""
        suspicious_names = [
            "../test.pdf",      # Path traversal
            "test<script>.pdf", # HTML/script injection
            "test\x00.pdf",     # Null byte
            "CON.pdf",          # Windows reserved name
            ".hidden.pdf",      # Hidden file
            "test.pdf.exe",     # Double extension
        ]
        
        for filename in suspicious_names:
            file_obj = self.create_mock_file(filename)
            valid, error, status = FileSecurityValidator.validate_filename(file_obj)
            assert valid is False, f"Should reject suspicious filename: {filename}"
            assert status == 400
    
    def test_validate_file_extension_success(self):
        """Test successful file extension validation"""
        file_obj = self.create_mock_file("document.pdf")
        valid, error, status = FileSecurityValidator.validate_file_extension(file_obj)
        assert valid is True
        assert error is None
        assert status is None
    
    def test_validate_file_extension_invalid(self):
        """Test invalid file extension validation"""
        invalid_files = [
            "document.txt",
            "document.exe",
            "document.docx",
            "document",  # No extension
        ]
        
        for filename in invalid_files:
            file_obj = self.create_mock_file(filename)
            valid, error, status = FileSecurityValidator.validate_file_extension(file_obj)
            assert valid is False, f"Should reject invalid extension: {filename}"
            assert status == 400
    
    def test_validate_file_size_success(self):
        """Test successful file size validation"""
        # Create a file smaller than the limit (25MB)
        file_obj = self.create_mock_file(size=1024 * 1024)  # 1MB
        valid, error, status = FileSecurityValidator.validate_file_size(file_obj)
        assert valid is True
        assert error is None
        assert status is None
    
    def test_validate_file_size_too_large(self):
        """Test file too large validation"""
        # Create a file larger than the limit
        file_obj = self.create_mock_file(size=30 * 1024 * 1024)  # 30MB
        valid, error, status = FileSecurityValidator.validate_file_size(file_obj)
        assert valid is False
        assert 'too large' in error['error']
        assert status == 400
    
    def test_validate_file_size_empty(self):
        """Test empty file validation"""
        file_obj = self.create_mock_file(content=b"")
        valid, error, status = FileSecurityValidator.validate_file_size(file_obj)
        assert valid is False
        assert 'empty' in error['error']
        assert status == 400
    
    def test_validate_pdf_structure_success(self):
        """Test successful PDF structure validation"""
        file_obj = self.create_mock_file(content=b"%PDF-1.4\nvalid pdf content")
        valid, error, status = FileSecurityValidator.validate_pdf_structure(file_obj)
        assert valid is True
        assert error is None
        assert status is None
    
    def test_validate_pdf_structure_invalid_header(self):
        """Test invalid PDF header validation"""
        invalid_contents = [
            b"not a pdf",
            b"<html>fake pdf</html>",
            b"%PDFwrong",
            b"%PDF-",  # Incomplete header
        ]
        
        for content in invalid_contents:
            file_obj = self.create_mock_file(content=content)
            valid, error, status = FileSecurityValidator.validate_pdf_structure(file_obj)
            assert valid is False, f"Should reject invalid PDF content: {content[:20]}"
            assert status == 400
    
    def test_scan_for_malicious_content_clean(self):
        """Test scanning clean PDF content"""
        clean_content = b"%PDF-1.4\nclean pdf content without suspicious patterns"
        file_obj = self.create_mock_file(content=clean_content)
        valid, error, status = FileSecurityValidator.scan_for_malicious_content(file_obj)
        assert valid is True
        assert error is None
        assert status is None
    
    def test_scan_for_malicious_content_suspicious(self):
        """Test scanning PDF with malicious content"""
        malicious_contents = [
            b"%PDF-1.4\n/JavaScript (eval('malicious code'))",
            b"%PDF-1.4\n/JS (unescape('%75%6E%65%73%63%61%70%65'))",
            b"%PDF-1.4\n/OpenAction << /S /JavaScript >>",
            b"%PDF-1.4\nfromCharCode(suspicious)",
        ]
        
        for content in malicious_contents:
            file_obj = self.create_mock_file(content=content)
            valid, error, status = FileSecurityValidator.scan_for_malicious_content(file_obj)
            assert valid is False, f"Should detect malicious content: {content[:50]}"
            assert 'malicious' in error['error']
            assert status == 400
    
    def test_scan_for_malicious_content_too_many_objects(self):
        """Test scanning PDF with suspicious number of objects"""
        # Create content with many 'obj' patterns
        suspicious_content = b"%PDF-1.4\n" + b"obj\n" * 15000
        file_obj = self.create_mock_file(content=suspicious_content)
        valid, error, status = FileSecurityValidator.scan_for_malicious_content(file_obj)
        assert valid is False
        assert 'suspicious' in error['error']
        assert status == 400
    
    def test_calculate_file_hash(self):
        """Test file hash calculation"""
        content = b"%PDF-1.4\ntest content"
        file_obj = self.create_mock_file(content=content)
        hash_value = FileSecurityValidator.calculate_file_hash(file_obj)
        
        # Should return a 64-character hex string (SHA-256)
        assert len(hash_value) == 64
        assert all(c in '0123456789abcdef' for c in hash_value)
        
        # Same content should produce same hash
        file_obj2 = self.create_mock_file(content=content)
        hash_value2 = FileSecurityValidator.calculate_file_hash(file_obj2)
        assert hash_value == hash_value2
    
    def test_validate_file_comprehensive_success(self):
        """Test comprehensive validation with valid file"""
        file_obj = self.create_mock_file("valid_document.pdf", b"%PDF-1.4\nvalid content")
        files = {'file': file_obj}
        
        valid, error, status, file_info = FileSecurityValidator.validate_file_comprehensive(files)
        
        assert valid is True
        assert error is None
        assert status is None
        assert file_info is not None
        assert file_info['filename'] == 'valid_document.pdf'
        assert 'hash' in file_info
        assert 'validations' in file_info
        
        # All validations should pass
        for validation_name, result in file_info['validations'].items():
            assert result == 'passed', f"Validation {validation_name} should pass"
    
    def test_validate_file_comprehensive_failure(self):
        """Test comprehensive validation with invalid file"""
        file_obj = self.create_mock_file("invalid.txt", b"not a pdf")
        files = {'file': file_obj}
        
        valid, error, status, file_info = FileSecurityValidator.validate_file_comprehensive(files)
        
        assert valid is False
        assert error is not None
        assert status == 400
        assert file_info is not None
        
        # Should have at least one failed validation
        failed_validations = [name for name, result in file_info['validations'].items() if result == 'failed']
        assert len(failed_validations) > 0
    
    @patch('file_validator.magic')
    def test_validate_mime_type_with_magic(self, mock_magic):
        """Test MIME type validation with python-magic"""
        mock_magic.from_buffer.return_value = 'application/pdf'
        
        file_obj = self.create_mock_file(content=b"%PDF-1.4\ntest")
        valid, error, status = FileSecurityValidator.validate_mime_type(file_obj)
        
        assert valid is True
        assert error is None
        assert status is None
    
    @patch('file_validator.magic')
    def test_validate_mime_type_invalid_with_magic(self, mock_magic):
        """Test invalid MIME type validation with python-magic"""
        mock_magic.from_buffer.return_value = 'text/plain'
        
        file_obj = self.create_mock_file(content=b"not a pdf")
        valid, error, status = FileSecurityValidator.validate_mime_type(file_obj)
        
        assert valid is False
        assert 'Invalid file type' in error['error']
        assert status == 400


class TestFileValidationConfig:
    """Test suite for FileValidationConfig"""
    
    def test_get_max_file_size(self):
        """Test getting max file size"""
        size = FileValidationConfig.get_max_file_size()
        assert isinstance(size, int)
        assert size > 0
    
    def test_get_allowed_extensions(self):
        """Test getting allowed extensions"""
        extensions = FileValidationConfig.get_allowed_extensions()
        assert isinstance(extensions, set)
        assert 'pdf' in extensions
    
    def test_update_max_file_size(self):
        """Test updating max file size"""
        original_size = FileValidationConfig.get_max_file_size()
        
        # Update to 50MB
        FileValidationConfig.update_max_file_size(50)
        new_size = FileValidationConfig.get_max_file_size()
        assert new_size == 50 * 1024 * 1024
        
        # Restore original size
        FileValidationConfig.update_max_file_size(original_size // (1024 * 1024))


class TestIntegrationScenarios:
    """Integration tests for real-world scenarios"""
    
    def test_realistic_pdf_upload(self):
        """Test with a realistic PDF upload scenario"""
        # Create a more realistic PDF content
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f 
0000000010 00000 n 
0000000053 00000 n 
0000000125 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
229
%%EOF"""
        
        file_obj = BytesIO(pdf_content)
        file_obj.filename = "document.pdf"
        file_obj.name = "document.pdf"
        files = {'file': file_obj}
        
        valid, error, status, file_info = FileSecurityValidator.validate_file_comprehensive(files)
        
        assert valid is True
        assert error is None
        assert status is None
        assert file_info['filename'] == 'document.pdf'
    
    def test_edge_case_filenames(self):
        """Test edge cases for filenames"""
        edge_cases = [
            ("document with spaces.pdf", True),   # Spaces should be OK
            ("document-with-dashes.pdf", True),   # Dashes should be OK
            ("document_with_underscores.pdf", True),  # Underscores should be OK
            ("document123.pdf", True),            # Numbers should be OK
            ("文档.pdf", True),                   # Unicode should be OK
            ("a.pdf", True),                     # Single letter should be OK
        ]
        
        for filename, should_pass in edge_cases:
            file_obj = BytesIO(b"%PDF-1.4\ntest")
            file_obj.filename = filename
            file_obj.name = filename
            
            valid, error, status = FileSecurityValidator.validate_filename(file_obj)
            if should_pass:
                assert valid is True, f"Should accept filename: {filename}"
            else:
                assert valid is False, f"Should reject filename: {filename}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])