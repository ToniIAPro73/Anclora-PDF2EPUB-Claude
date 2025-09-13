from flask import Blueprint, request, current_app, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from celery.result import AsyncResult
import os
import uuid
import datetime
import jwt
import logging
from functools import wraps
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

from .tasks import convert_pdf_to_epub, celery_app
from .models import create_conversion, fetch_conversions, create_user, find_user
from . import limiter

bp = Blueprint('routes', __name__)

ALLOWED_EXTENSIONS = {"pdf"}
ALLOWED_MIME_TYPES = {"application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
logger = logging.getLogger(__name__)
conversion_counter = Counter('pdf_conversions_total', 'Total PDF conversion requests')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'Missing token'}), 401
        token = auth.split(' ')[1]
        try:
            jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated


@bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    if find_user(username):
        return jsonify({'error': 'User exists'}), 400
    create_user(username, generate_password_hash(password))
    return jsonify({'message': 'User created'}), 201


@bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    user = find_user(username)
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Invalid credentials'}), 401
    payload = {'sub': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token})


@bp.route('/api/protected', methods=['GET'])
@token_required
def protected():
    return jsonify({'message': 'Access granted'})

@bp.route('/api/convert', methods=['POST'])
@limiter.limit(lambda: current_app.config.get('RATE_LIMIT', '5 per minute'))

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

    mime_type = magic.from_buffer(file.read(2048), mime=True)
    file.seek(0)
    if mime_type not in ALLOWED_MIME_TYPES:
        current_app.logger.warning("Invalid MIME type %s for file %s", mime_type, file.filename)
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

    task_id = str(uuid.uuid4())
    create_conversion(task_id)
    convert_pdf_to_epub.apply_async(args=[task_id, pdf_path, epub_path], task_id=task_id)
    conversion_counter.inc()
    return jsonify({'task_id': task_id}), 202

@bp.route('/api/status/<task_id>', methods=['GET'])
@token_required
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
    return jsonify(response)


@bp.route('/api/history', methods=['GET'])
@token_required
def history():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    conversions = fetch_conversions(page, per_page)
    return jsonify(conversions)

@bp.route('/metrics')
def metrics():
    return current_app.response_class(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
