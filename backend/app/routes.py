from flask import Blueprint, request, current_app, jsonify
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
from .models import Conversion, User
from .converter import ConversionEngine, suggest_best_pipeline
from . import db, limiter

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


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.lower().startswith('bearer '):
            return jsonify({'error': 'Missing token'}), 401
        token = auth_header.split(' ', 1)[1]
        try:
            jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        except Exception:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)

    return decorated


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
    finally:
        os.unlink(tmp.name)
    return jsonify(result)


@bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User exists'}), 400
    user = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201


@bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
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
    db.session.add(Conversion(task_id=task_id, status='PENDING'))
    db.session.commit()
    convert_pdf_to_epub.apply_async(args=[task_id, pdf_path, epub_path, pipeline_id], task_id=task_id)
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


@bp.route('/api/preview/<conversion_id>', methods=['GET'])
@token_required
def preview(conversion_id):
    conv = Conversion.query.filter_by(task_id=conversion_id).first()
    if conv is None and conversion_id.isdigit():
        conv = Conversion.query.get(int(conversion_id))
    if not conv or conv.status != 'SUCCESS' or not conv.output_path or not os.path.exists(conv.output_path):
        return jsonify({'error': 'Preview not available'}), 404
    book = epub.read_epub(conv.output_path)
    pages = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            pages.append(item.get_content().decode('utf-8', errors='ignore'))
    return jsonify({'pages': pages})


@bp.route('/api/history', methods=['GET'])
@token_required
def history():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    pagination = Conversion.query.order_by(Conversion.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify([c.to_dict() for c in pagination.items])

@bp.route('/metrics')
def metrics():
    return current_app.response_class(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
