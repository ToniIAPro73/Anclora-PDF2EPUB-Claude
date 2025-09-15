"""
Enhanced file validation for Anclora PDF2EPUB
Security-focused validation with comprehensive PDF checks
"""
import os
import re
import hashlib
import logging
import tempfile
from typing import Tuple, Dict, Any, Optional, List
from pathlib import Path
import mimetypes

# Optional dependencies - gracefully handle missing imports
magic = None
PyPDF2 = None

try:
    import magic
except ImportError:
    pass

try:
    import PyPDF2
except ImportError:
    pass

logger = logging.getLogger(__name__)


class FileSecurityValidator:
    """Enhanced file security validation with comprehensive checks"""
    
    # Configuration
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE_MB', '25')) * 1024 * 1024  # 25MB default
    ALLOWED_EXTENSIONS = {'pdf'}
    ALLOWED_MIME_TYPES = {'application/pdf'}
    
    # Security patterns to detect in filenames
    SUSPICIOUS_FILENAME_PATTERNS = [
        r'\.{2,}',              # Multiple dots (path traversal)
        r'[<>:"|?*]',           # Windows forbidden characters
        r'[\x00-\x1f\x7f-\x9f]', # Control characters
        r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$',  # Windows reserved names
        r'^\.',                 # Hidden files starting with dot
        r'\.pdf\.',             # Double extensions (pdf.exe, etc.)
    ]
    
    # Malicious PDF patterns (basic signatures)
    MALICIOUS_PDF_PATTERNS = [
        b'/JavaScript',         # JavaScript in PDF
        b'/JS',                # JS in PDF
        b'/OpenAction',        # Auto-execute actions
        b'/AA',                # Additional Actions
        b'eval(',              # Eval function
        b'unescape(',          # Unescape function
        b'%u[0-9a-fA-F]{4}',   # Unicode escapes
        b'fromCharCode',       # Character code conversion
    ]
    
    @classmethod
    def validate_file_presence(cls, files: Dict) -> Tuple[bool, Optional[Dict], Optional[int]]:
        """Check if a file is present in the request"""
        if 'file' not in files:
            logger.warning("No file part in request")
            return False, {'error': 'No file part in request'}, 400
        return True, None, None
    
    @classmethod
    def validate_filename(cls, file) -> Tuple[bool, Optional[Dict], Optional[int]]:
        """Enhanced filename validation with security checks"""
        if not file.filename or file.filename.strip() == '':
            logger.warning("Empty filename provided")
            return False, {'error': 'No file selected'}, 400
        
        filename = file.filename.strip()
        
        # Check filename length
        if len(filename) > 255:
            logger.warning(f"Filename too long: {len(filename)} characters")
            return False, {'error': 'Filename too long (max 255 characters)'}, 400
        
        # Check for suspicious patterns
        for pattern in cls.SUSPICIOUS_FILENAME_PATTERNS:
            if re.search(pattern, filename, re.IGNORECASE):
                logger.warning(f"Suspicious filename pattern detected: {filename}")
                return False, {'error': 'Invalid filename format'}, 400
        
        # Check for valid UTF-8 encoding
        try:
            filename.encode('utf-8')
        except UnicodeEncodeError:
            logger.warning(f"Invalid filename encoding: {filename}")
            return False, {'error': 'Invalid filename encoding'}, 400
        
        return True, None, None
    
    @classmethod
    def validate_file_extension(cls, file) -> Tuple[bool, Optional[Dict], Optional[int]]:
        """Validate file extension"""
        if not file.filename:
            return False, {'error': 'No filename provided'}, 400
        
        # Extract extension
        if '.' not in file.filename:
            logger.warning(f"No extension in filename: {file.filename}")
            return False, {'error': 'File must have an extension'}, 400
        
        extension = file.filename.rsplit('.', 1)[1].lower()
        
        if extension not in cls.ALLOWED_EXTENSIONS:
            logger.warning(f"Disallowed file extension: {extension}")
            return False, {'error': f'Only {", ".join(cls.ALLOWED_EXTENSIONS).upper()} files are allowed'}, 400
        
        return True, None, None
    
    @classmethod
    def validate_file_size(cls, file) -> Tuple[bool, Optional[Dict], Optional[int]]:
        """Enhanced file size validation"""
        # Get current position and file size
        current_pos = file.tell()
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(current_pos)  # Restore original position
        
        if size == 0:
            logger.warning(f"Empty file: {file.filename}")
            return False, {'error': 'File cannot be empty'}, 400
        
        if size > cls.MAX_FILE_SIZE:
            size_mb = size / (1024 * 1024)
            max_mb = cls.MAX_FILE_SIZE / (1024 * 1024)
            logger.warning(f"File too large: {size_mb:.1f}MB (max {max_mb}MB)")
            return False, {'error': f'File too large (max {max_mb}MB)'}, 400
        
        return True, None, None
    
    @classmethod
    def validate_mime_type(cls, file) -> Tuple[bool, Optional[Dict], Optional[int]]:
        """Enhanced MIME type validation"""
        file_content = file.read(8192)  # Read first 8KB for MIME detection
        file.seek(0)  # Reset file pointer
        
        # Try python-magic first (more reliable)
        if magic is not None:
            try:
                mime_type = magic.from_buffer(file_content, mime=True)
                if mime_type not in cls.ALLOWED_MIME_TYPES:
                    logger.warning(f"Invalid MIME type: {mime_type} for file {file.filename}")
                    return False, {'error': f'Invalid file type: {mime_type}'}, 400
            except Exception as e:
                logger.warning(f"Magic MIME detection failed: {e}")
        
        # Fallback to Python's mimetypes
        mime_type, _ = mimetypes.guess_type(file.filename)
        if mime_type and mime_type not in cls.ALLOWED_MIME_TYPES:
            logger.warning(f"Invalid MIME type (fallback): {mime_type}")
            return False, {'error': f'Invalid file type: {mime_type}'}, 400
        
        return True, None, None
    
    @classmethod
    def validate_pdf_structure(cls, file) -> Tuple[bool, Optional[Dict], Optional[int]]:
        """Enhanced PDF structure validation"""
        # Check PDF header
        header = file.read(8)
        file.seek(0)
        
        if not header.startswith(b'%PDF-'):
            logger.warning(f"Invalid PDF header for file {file.filename}")
            return False, {'error': 'Invalid PDF file structure'}, 400
        
        # Validate PDF version
        try:
            version_part = header[5:8].decode('ascii')
            if not re.match(r'\d\.\d', version_part):
                logger.warning(f"Invalid PDF version: {version_part}")
                return False, {'error': 'Invalid PDF version'}, 400
        except Exception:
            logger.warning(f"Could not parse PDF version from header")
            return False, {'error': 'Invalid PDF header format'}, 400
        
        # If PyPDF2 is available, do deeper validation
        if PyPDF2 is not None:
            try:
                with tempfile.NamedTemporaryFile() as tmp_file:
                    file.seek(0)
                    tmp_file.write(file.read())
                    tmp_file.flush()
                    file.seek(0)
                    
                    # Try to read PDF with PyPDF2
                    with open(tmp_file.name, 'rb') as pdf_file:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        
                        # Check if PDF has pages
                        if len(pdf_reader.pages) == 0:
                            logger.warning(f"PDF has no pages: {file.filename}")
                            return False, {'error': 'PDF file contains no pages'}, 400
                        
                        # Check for encrypted PDFs
                        if pdf_reader.is_encrypted:
                            logger.warning(f"Encrypted PDF detected: {file.filename}")
                            return False, {'error': 'Encrypted PDFs are not supported'}, 400
                        
            except Exception as e:
                logger.warning(f"PDF structure validation failed: {e}")
                return False, {'error': 'Corrupted or invalid PDF file'}, 400
        
        return True, None, None
    
    @classmethod
    def scan_for_malicious_content(cls, file) -> Tuple[bool, Optional[Dict], Optional[int]]:
        """Basic malware detection for PDF files"""
        file_content = file.read()
        file.seek(0)
        
        # Check for suspicious patterns
        suspicious_patterns_found = []
        
        for pattern in cls.MALICIOUS_PDF_PATTERNS:
            if isinstance(pattern, bytes):
                if pattern in file_content:
                    suspicious_patterns_found.append(pattern.decode('ascii', errors='ignore'))
            else:
                if re.search(pattern, file_content):
                    suspicious_patterns_found.append(str(pattern))
        
        if suspicious_patterns_found:
            logger.warning(f"Suspicious content detected in {file.filename}: {suspicious_patterns_found}")
            return False, {
                'error': 'File contains potentially malicious content',
                'details': 'JavaScript or executable content detected'
            }, 400
        
        # Check for unusual PDF structure (too many objects, etc.)
        if file_content.count(b'obj') > 10000:  # Reasonable limit for objects
            logger.warning(f"Suspicious number of PDF objects in {file.filename}")
            return False, {'error': 'PDF structure appears suspicious'}, 400
        
        return True, None, None
    
    @classmethod
    def calculate_file_hash(cls, file) -> str:
        """Calculate SHA-256 hash of the file for logging/tracking"""
        content = file.read()
        file.seek(0)
        return hashlib.sha256(content).hexdigest()
    
    @classmethod
    def validate_file_comprehensive(cls, request_files) -> Tuple[bool, Optional[Dict], Optional[int], Optional[Dict]]:
        """
        Run comprehensive validation on uploaded file
        
        Returns:
            (is_valid, error_response, status_code, file_info)
        """
        # Step 1: Check file presence
        valid, error_response, status_code = cls.validate_file_presence(request_files)
        if not valid:
            return valid, error_response, status_code, None
        
        file = request_files['file']
        
        # Step 2: Run all validations in order
        validations = [
            ('filename', cls.validate_filename),
            ('extension', cls.validate_file_extension), 
            ('size', cls.validate_file_size),
            ('mime_type', cls.validate_mime_type),
            ('pdf_structure', cls.validate_pdf_structure),
            ('malicious_content', cls.scan_for_malicious_content),
        ]
        
        validation_results = {}
        
        for validation_name, validation_func in validations:
            try:
                valid, error_response, status_code = validation_func(file)
                validation_results[validation_name] = 'passed' if valid else 'failed'
                
                if not valid:
                    logger.warning(f"File validation failed at {validation_name}: {error_response}")
                    return valid, error_response, status_code, validation_results
                    
            except Exception as e:
                logger.error(f"Validation {validation_name} raised exception: {e}")
                validation_results[validation_name] = 'error'
                return False, {'error': f'Validation error: {validation_name}'}, 500, validation_results
        
        # Step 3: Generate file info for logging
        file_info = {
            'filename': file.filename,
            'size': file.tell() if hasattr(file, 'tell') else 'unknown',
            'hash': cls.calculate_file_hash(file),
            'validations': validation_results
        }
        
        logger.info(f"File validation passed for {file.filename} (hash: {file_info['hash'][:16]}...)")
        
        return True, None, None, file_info


class FileValidationConfig:
    """Configuration management for file validation"""
    
    @staticmethod
    def get_max_file_size() -> int:
        """Get maximum file size in bytes"""
        return FileSecurityValidator.MAX_FILE_SIZE
    
    @staticmethod
    def get_allowed_extensions() -> set:
        """Get allowed file extensions"""
        return FileSecurityValidator.ALLOWED_EXTENSIONS.copy()
    
    @staticmethod
    def update_max_file_size(size_mb: int) -> None:
        """Update maximum file size"""
        FileSecurityValidator.MAX_FILE_SIZE = size_mb * 1024 * 1024
        logger.info(f"Updated max file size to {size_mb}MB")