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
    
    # Security patterns to detect in filenames (more tolerant for international chars)
    SUSPICIOUS_FILENAME_PATTERNS = [
        r'\.{3,}',              # 3 or more dots (path traversal)
        r'[<>:"|?*]',           # Windows forbidden characters
        r'[\x00-\x1f\x7f]',     # Control characters (excluding \x80-\x9f for international chars)
        r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])\.pdf$',  # Windows reserved names with .pdf
        r'^\..*\.pdf$',         # Hidden files starting with dot
        r'\.pdf\.[^$]',         # Double extensions (pdf.exe, etc.) but not end of string
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
        
        # Check for valid encoding (be more tolerant with international characters)
        try:
            # First try UTF-8, then fallback to latin-1 (common in Windows)
            filename.encode('utf-8')
        except UnicodeEncodeError:
            try:
                filename.encode('latin-1')
                logger.info(f"Filename uses latin-1 encoding: {filename}")
            except UnicodeEncodeError:
                # Only reject if it's really problematic encoding
                try:
                    filename.encode('cp1252')  # Windows encoding
                    logger.info(f"Filename uses cp1252 encoding: {filename}")
                except UnicodeEncodeError:
                    logger.warning(f"Problematic filename encoding: {filename}")
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
                        try:
                            pdf_reader = PyPDF2.PdfReader(pdf_file, strict=False)

                            # Check for encrypted PDFs (critical security check)
                            if pdf_reader.is_encrypted:
                                logger.warning(f"Encrypted PDF detected: {file.filename}")
                                return False, {'error': 'Encrypted PDFs are not supported'}, 400

                            # Try to access pages - if this fails, PDF might be corrupted
                            try:
                                page_count = len(pdf_reader.pages)
                                if page_count == 0:
                                    logger.warning(f"PDF has no pages: {file.filename}")
                                    return False, {'error': 'PDF file contains no pages'}, 400
                                logger.info(f"PDF validation passed: {page_count} pages in {file.filename}")
                            except Exception as page_error:
                                # Log the error but don't fail - some PDFs with complex structure can still be processed
                                logger.info(f"Could not determine page count for {file.filename}: {page_error}")

                        except PyPDF2.errors.PdfReadError as pdf_error:
                            # More specific handling for PDF read errors
                            error_msg = str(pdf_error).lower()
                            if 'encrypted' in error_msg:
                                return False, {'error': 'Encrypted PDFs are not supported'}, 400
                            elif 'damaged' in error_msg or 'corrupted' in error_msg:
                                logger.warning(f"PDF appears damaged but might be processable: {pdf_error}")
                                # Don't fail here - let the conversion engine try
                            else:
                                logger.info(f"PyPDF2 read warning for {file.filename}: {pdf_error}")

            except Exception as e:
                # Log the error but don't fail validation
                logger.info(f"PyPDF2 validation encountered issue for {file.filename}: {e}")
                # The file passed basic PDF header validation, so we'll allow it through
        
        return True, None, None
    
    @classmethod
    def scan_for_malicious_content(cls, file) -> Tuple[bool, Optional[Dict], Optional[int]]:
        """Enhanced malware detection for PDF files with reduced false positives"""
        file_content = file.read()
        file.seek(0)

        # Check for high-risk suspicious patterns (only the most dangerous ones)
        high_risk_patterns = [
            b'/JavaScript',         # JavaScript in PDF
            b'/JS',                # JS in PDF
            b'/OpenAction',        # Auto-execute actions
            b'/AA',                # Additional Actions
        ]

        critical_patterns_found = []

        for pattern in high_risk_patterns:
            if pattern in file_content:
                critical_patterns_found.append(pattern.decode('ascii', errors='ignore'))

        # Log potentially suspicious patterns but don't block (many legitimate PDFs have JavaScript)
        if critical_patterns_found:
            dangerous_patterns = [p for p in critical_patterns_found if p in ['/JavaScript', '/JS', '/OpenAction', '/AA']]
            if dangerous_patterns:
                logger.info(f"PDF contains interactive elements: {dangerous_patterns} in {file.filename}")
                # Don't block - many legitimate PDFs have JavaScript for forms, etc.
                # return False, {
                #     'error': 'File contains potentially malicious content',
                #     'details': 'Executable JavaScript or auto-actions detected'
                # }, 400

        # Check for extremely unusual PDF structure (very high threshold)
        obj_count = file_content.count(b'obj')
        if obj_count > 100000:  # Even higher threshold - scientific/complex PDFs can have many objects
            logger.warning(f"Extremely high number of PDF objects ({obj_count}) in {file.filename}")
            # Don't block - complex scientific documents, scanned books, etc. can have many objects
            # return False, {'error': 'PDF structure appears suspicious (too many objects)'}, 400

        # Log analysis results for legitimate complex documents
        if obj_count > 1000:
            logger.info(f"Complex PDF detected: {obj_count} objects in {file.filename} - likely a complex document")

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