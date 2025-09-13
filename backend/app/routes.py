from flask import Blueprint, request, current_app, jsonify
from werkzeug.utils import secure_filename
from celery.result import AsyncResult
import os
import uuid

from .tasks import convert_pdf_to_epub, celery_app
from .models import create_conversion, fetch_conversions
from .auth import token_required

bp = Blueprint('routes', __name__)

ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/api/convert', methods=['POST'])
@token_required
def convert():
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
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    filename = secure_filename(file.filename)
    pdf_path = os.path.join(upload_folder, f"{uuid.uuid4()}_{filename}")
    file.save(pdf_path)
    results_folder = current_app.config['RESULTS_FOLDER']
    os.makedirs(results_folder, exist_ok=True)
    epub_filename = os.path.splitext(os.path.basename(pdf_path))[0] + '.epub'
    epub_path = os.path.join(results_folder, epub_filename)
    task_id = str(uuid.uuid4())
    create_conversion(task_id)
    convert_pdf_to_epub.apply_async(args=[task_id, pdf_path, epub_path], task_id=task_id)
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
