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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Authentication now handled by Supabase decorators


@bp.route('/api/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    file.seek(0, os.SEEK_END)
    if file.tell() > MAX_FILE_SIZE:
        return jsonify({'error': 'File too large'}), 400
    file.seek(0)
    if magic is not None:
        mime_type = magic.from_buffer(file.read(2048), mime=True)
        file.seek(0)
        if mime_type not in ALLOWED_MIME_TYPES:
            return jsonify({'error': 'Invalid file content'}), 400
    else:
        header = file.read(4)
        file.seek(0)
        if not header.startswith(b"%PDF"):
            return jsonify({'error': 'Invalid file content'}), 400
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


# Authentication routes removed - now handled by Supabase


@bp.route('/api/protected', methods=['GET'])
@supabase_auth_required
def protected():
    return jsonify({'message': 'Access granted'})

@bp.route('/api/convert', methods=['POST'])
@limiter.limit(lambda: current_app.config.get('RATE_LIMIT', '5 per minute'))
@supabase_auth_required
def convert():
    logger.info('Conversion requested')
    if 'file' not in request.files:
        current_app.logger.warning("No file part in request")
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        current_app.logger.warning("Empty filename provided")
        return jsonify({'error': 'No selected file'}), 400
    if not allowed_file(file.filename):
        current_app.logger.warning("Disallowed file extension: %s", file.filename)
        return jsonify({'error': 'Invalid file type'}), 400
    file.seek(0, os.SEEK_END)
    if file.tell() > MAX_FILE_SIZE:
        current_app.logger.warning("File too large: %s", file.filename)
        return jsonify({'error': 'File too large'}), 400
    file.seek(0)

    if magic is not None:
        mime_type = magic.from_buffer(file.read(2048), mime=True)
        file.seek(0)
        if mime_type not in ALLOWED_MIME_TYPES:
            current_app.logger.warning("Invalid MIME type %s for file %s", mime_type, file.filename)
            logging.warning("Invalid MIME type %s for file %s", mime_type, file.filename)
            return jsonify({'error': 'Invalid file content'}), 400
    else:
        header = file.read(4)
        file.seek(0)
        if not header.startswith(b"%PDF"):
            current_app.logger.warning("Invalid MIME type for file %s", file.filename)
            logging.warning("Invalid MIME type for file %s", file.filename)
            return jsonify({'error': 'Invalid file content'}), 400

    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    filename = secure_filename(os.path.basename(file.filename))
    pdf_path = os.path.abspath(os.path.join(upload_folder, f"{uuid.uuid4()}_{filename}"))
    if not pdf_path.startswith(os.path.abspath(upload_folder) + os.sep):
        current_app.logger.warning("Path traversal attempt: %s", file.filename)
        return jsonify({'error': 'Invalid file name'}), 400
    file.save(pdf_path)

    results_folder = current_app.config['RESULTS_FOLDER']
    os.makedirs(results_folder, exist_ok=True)
    epub_filename = os.path.splitext(os.path.basename(pdf_path))[0] + '.epub'
    epub_path = os.path.abspath(os.path.join(results_folder, epub_filename))
    if not epub_path.startswith(os.path.abspath(results_folder) + os.sep):
        current_app.logger.warning("Path traversal attempt for result: %s", epub_filename)
        return jsonify({'error': 'Invalid file name'}), 400

    pipeline_id = request.form.get('pipeline_id')
    if pipeline_id and pipeline_id not in [e.value for e in ConversionEngine]:
        return jsonify({'error': 'Invalid pipeline_id'}), 400

    task_id = str(uuid.uuid4())
    user_id = get_current_user_id()

    # Create conversion record in Supabase
    create_conversion_record(user_id, task_id, filename)

    convert_pdf_to_epub.apply_async(args=[task_id, pdf_path, epub_path, pipeline_id], task_id=task_id)
    conversion_counter.inc()
    return jsonify({'task_id': task_id}), 202

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
