"""
Test routes without authentication to debug the 401 issue
"""
from flask import Blueprint, jsonify, request
import logging

test_bp = Blueprint('test', __name__)
logger = logging.getLogger(__name__)

@test_bp.route('/api/test/ping', methods=['GET'])
def ping():
    """Simple ping endpoint without auth"""
    return jsonify({'status': 'ok', 'message': 'Backend is working'})

@test_bp.route('/api/test/convert-no-auth', methods=['POST'])
def convert_no_auth():
    """Test conversion endpoint without authentication"""
    try:
        logger.info("Test conversion endpoint called")
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Mock successful response
        return jsonify({
            'message': 'TEST: Conversion would start here (no auth)',
            'task_id': 'test-task-123',
            'status': 'DEMO_MODE',
            'note': 'This is a test endpoint to verify backend communication'
        })
        
    except Exception as e:
        logger.error(f"Test conversion error: {e}")
        return jsonify({'error': f'Test conversion failed: {str(e)}'}), 500

@test_bp.route('/api/test/auth-debug', methods=['POST'])
def auth_debug():
    """Debug authentication headers"""
    auth_header = request.headers.get('Authorization', 'NO_AUTH_HEADER')
    
    return jsonify({
        'authorization_header': auth_header[:50] + '...' if len(auth_header) > 50 else auth_header,
        'has_auth': bool(auth_header and auth_header != 'NO_AUTH_HEADER'),
        'content_type': request.content_type,
        'method': request.method,
        'files': list(request.files.keys()) if request.files else []
    })