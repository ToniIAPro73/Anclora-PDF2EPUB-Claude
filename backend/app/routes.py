from flask import Blueprint, request, current_app, jsonify, send_from_directory, url_for
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from celery.result import AsyncResult
import os
import uuid
import datetime
import jwt
import logging
import ebooklib
from ebooklib import epub
try:
    import magic  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    magic = None
from functools import wraps
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, REGISTRY

from .tasks import convert_pdf_to_epub, celery_app
from .converter import ConversionEngine, suggest_best_pipeline
from .supabase_auth import supabase_auth_required, get_current_user_id
from .supabase_client import (
    create_conversion_record,
    update_conversion_status,
    get_user_conversions,
    get_conversion_by_task_id
)
from . import limiter

bp = Blueprint('routes', __name__)

ALLOWED_EXTENSIONS = {"pdf"}
ALLOWED_MIME_TYPES = {"application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
logger = logging.getLogger(__name__)
if 'pdf_conversions_total' in REGISTRY._names_to_collectors:
    conversion_counter = REGISTRY._names_to_collectors['pdf_conversions_total']
else:
    conversion_counter = Counter('pdf_conversions_total', 'Total PDF conversion requests')

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class FileValidator:
    """Validator for PDF file uploads"""
    
    @staticmethod
    def validate_file_presence(files):
        """Check if a file is present in the request"""
        if 'file' not in files:
            logger.warning("No file part in request")
            return False, {'error': 'No file part'}, 400
        return True, None, None
    
    @staticmethod
    def validate_filename(file):
        """Check if the filename is valid"""
        if file.filename == '':
            logger.warning("Empty filename provided")
            return False, {'error': 'No selected file'}, 400
        return True, None, None
    
    @staticmethod
    def validate_file_extension(file):
        """Check if the file has a valid extension"""
        if not allowed_file(file.filename):
            logger.warning(f"Disallowed file extension: {file.filename}")
            return False, {'error': 'Invalid file type'}, 400
        return True, None, None
    
    @staticmethod
    def validate_file_size(file):
        """Check if the file size is within limits"""
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        if size > MAX_FILE_SIZE:
            logger.warning(f"File too large: {file.filename}")
            return False, {'error': 'File too large'}, 400
        return True, None, None
    
    @staticmethod
    def validate_file_content(file):
        """Check if the file content is valid PDF"""
        if magic is not None:
            mime_type = magic.from_buffer(file.read(2048), mime=True)
            file.seek(0)
            if mime_type not in ALLOWED_MIME_TYPES:
                logger.warning(f"Invalid MIME type {mime_type} for file {file.filename}")
                return False, {'error': 'Invalid file content'}, 400
        else:
            header = file.read(4)
            file.seek(0)
            if not header.startswith(b"%PDF"):
                logger.warning(f"Invalid file content for file {file.filename}")
                return False, {'error': 'Invalid file content'}, 400
        return True, None, None
    
    @classmethod
    def validate_pdf(cls, request_files):
        """Run all validation checks on the uploaded PDF file"""
        # Check file presence
        valid, error_response, status_code = cls.validate_file_presence(request_files)
        if not valid:
            return valid, error_response, status_code
        
        file = request_files['file']
        
        # Run all validations
        validations = [
            cls.validate_filename,
            cls.validate_file_extension,
            cls.validate_file_size,
            cls.validate_file_content
        ]
        
        for validation in validations:
            valid, error_response, status_code = validation(file)
            if not valid:
                return valid, error_response, status_code
        
        return True, None, None

@bp.route('/api/analyze', methods=['POST'])
def analyze():
    # Validate the uploaded file
    valid, error_response, status_code = FileValidator.validate_pdf(request.files)
    if not valid:
        return jsonify(error_response), status_code
    
    file = request.files['file']
    
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        file.save(tmp.name)
    try:
        result = suggest_best_pipeline(tmp.name)
        if 'recommended' in result and 'pipeline_id' not in result:
            result['pipeline_id'] = result['recommended']
    finally:
        os.unlink(tmp.name)
    return jsonify(result)

@bp.route('/api/protected', methods=['GET'])
@supabase_auth_required
def protected():
    return jsonify({'message': 'Access granted'})

@bp.route('/api/convert', methods=['POST'])
@limiter.limit(lambda: current_app.config.get('RATE_LIMIT', '5 per minute'))
@supabase_auth_required
def convert():
    """
    Convert a PDF file to EPUB format
    
    This endpoint:
    1. Validates the uploaded PDF file
    2. Saves the file to the upload folder
    3. Creates a conversion record in Supabase
    4. Starts an asynchronous conversion task
    5. Returns the task ID for status tracking
    
    Returns:
        JSON response with task_id or error message
    """
    logger.info('Conversion requested')
    
    try:
        # Validate the uploaded file
        valid, error_response, status_code = FileValidator.validate_pdf(request.files)
        if not valid:
            return jsonify(error_response), status_code
        
        file = request.files['file']
        
        # Prepare file paths
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate a secure filename with UUID to prevent collisions
        filename = secure_filename(os.path.basename(file.filename))
        pdf_path = os.path.abspath(os.path.join(upload_folder, f"{uuid.uuid4()}_{filename}"))
        
        # Security check for path traversal
        if not pdf_path.startswith(os.path.abspath(upload_folder) + os.sep):
            logger.warning(f"Path traversal attempt: {file.filename}")
            return jsonify({'error': 'Invalid file name'}), 400
        
        # Save the uploaded file
        file.save(pdf_path)
        
        # Prepare output path
        results_folder = current_app.config['RESULTS_FOLDER']
        os.makedirs(results_folder, exist_ok=True)
        epub_filename = os.path.splitext(os.path.basename(pdf_path))[0] + '.epub'
        epub_path = os.path.abspath(os.path.join(results_folder, epub_filename))
        
        # Security check for path traversal
        if not epub_path.startswith(os.path.abspath(results_folder) + os.sep):
            logger.warning(f"Path traversal attempt for result: {epub_filename}")
            return jsonify({'error': 'Invalid file name'}), 400
        
        # Validate pipeline ID if provided
        pipeline_id = request.form.get('pipeline_id')
        if pipeline_id and pipeline_id not in [e.value for e in ConversionEngine]:
            return jsonify({'error': 'Invalid pipeline_id'}), 400
        
        # Generate task ID and get user ID
        task_id = str(uuid.uuid4())
        user_id = get_current_user_id()
        
        if not user_id:
            logger.error("User ID not found in request context")
            return jsonify({'error': 'Authentication error'}), 401
        
        # Create conversion record in Supabase
        record = create_conversion_record(user_id, task_id, filename)
        if not record:
            logger.error(f"Failed to create conversion record for user {user_id}")
            return jsonify({'error': 'Failed to create conversion record'}), 500
        
        # Start asynchronous conversion task
        logger.info(f"Starting conversion task {task_id} for user {user_id}")
        convert_pdf_to_epub.apply_async(
            args=[task_id, pdf_path, epub_path, pipeline_id], 
            task_id=task_id
        )
        
        # Increment conversion counter for metrics
        conversion_counter.inc()
        
        return jsonify({
            'task_id': task_id,
            'message': 'Conversion started successfully'
        }), 202
        
    except Exception as e:
        logger.exception(f"Unexpected error in conversion: {str(e)}")
        return jsonify({
            'error': 'Server error',
            'message': 'An unexpected error occurred during conversion'
        }), 500

@bp.route('/api/status/<task_id>', methods=['GET'])
@supabase_auth_required
def task_status(task_id):
    result = AsyncResult(task_id, app=celery_app)
    response = {
        'task_id': task_id,
        'status': result.state
    }
    if result.state == 'SUCCESS':
        response['result'] = result.result
    elif result.state == 'FAILURE':
        response['error'] = str(result.info)
    elif result.info:
        # For PROGRESS or other intermediate states
        if isinstance(result.info, dict):
            response.update(result.info)
        else:
            response['message'] = str(result.info)
    return jsonify(response)

@bp.route('/api/preview/<conversion_id>', methods=['GET'])
@supabase_auth_required
def preview(conversion_id):
    conv = get_conversion_by_task_id(conversion_id)
    if not conv or conv.get('status') != 'COMPLETED' or not conv.get('output_path') or not os.path.exists(conv['output_path']):
        return jsonify({'error': 'Preview not available'}), 404

    book = epub.read_epub(conv['output_path'])
    pages = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            pages.append(item.get_content().decode('utf-8', errors='ignore'))
    return jsonify({'pages': pages})

@bp.route('/api/history', methods=['GET'])
@supabase_auth_required
def history():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    offset = (page - 1) * per_page

    user_id = get_current_user_id()
    conversions = get_user_conversions(user_id, per_page, offset)

    results = []
    for c in conversions:
        item = dict(c)
        if c.get('thumbnail_path'):
            item['thumbnail_url'] = url_for('routes.thumbnail', filename=c['thumbnail_path'], _external=False)
        results.append(item)

    return jsonify(results)

@bp.route('/thumbnails/<path:filename>', methods=['GET'])
def thumbnail(filename):
    thumb_dir = current_app.config['THUMBNAIL_FOLDER']
    return send_from_directory(thumb_dir, filename)

@bp.route('/metrics')
def metrics():
    return current_app.response_class(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@bp.route('/api/debug', methods=['GET'])
def debug():
    """Debug endpoint to check environment variables and configuration"""
    import os
    return jsonify({
        'SUPABASE_URL': os.getenv('SUPABASE_URL'),
        'SUPABASE_JWT_SECRET_EXISTS': os.getenv('SUPABASE_JWT_SECRET') is not None,
        'SUPABASE_JWT_SECRET_LENGTH': len(os.getenv('SUPABASE_JWT_SECRET', '')) if os.getenv('SUPABASE_JWT_SECRET') else 0,
        'AUTH_HEADERS': {k: v for k, v in request.headers.items() if k.lower() in ('authorization', 'x-client-info')},
    })
