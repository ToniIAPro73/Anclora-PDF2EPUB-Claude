"""
Simplified routes without Celery dependency for CORS testing
"""
from flask import Blueprint, request, jsonify
import logging
import uuid

bp = Blueprint('simple_routes', __name__)
logger = logging.getLogger(__name__)

@bp.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze a PDF file and suggest conversion pipelines"""
    try:
        logger.info("Analyze endpoint called")

        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Mock analysis response
        return jsonify({
            'pipelines': [
                {
                    'id': 'engines.low',
                    'quality': 'Low',
                    'estimated_time': 30
                },
                {
                    'id': 'engines.medium',
                    'quality': 'Medium', 
                    'estimated_time': 60
                },
                {
                    'id': 'engines.high',
                    'quality': 'High',
                    'estimated_time': 120
                }
            ],
            'recommended': 'engines.medium',
            'message': 'File analyzed successfully (mock response)'
        })

    except Exception as e:
        logger.error(f"Analyze error: {e}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@bp.route('/api/convert', methods=['POST'])
def convert():
    """Convert a PDF file to EPUB format (simplified version)"""
    try:
        logger.info("Convert endpoint called")

        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        pipeline_id = request.form.get('pipeline_id', 'engines.medium')
        task_id = str(uuid.uuid4())

        # Mock conversion response
        return jsonify({
            'task_id': task_id,
            'message': 'Conversion started successfully (mock response)',
            'pipeline_id': pipeline_id,
            'status': 'PROCESSING',
            'note': 'This is a simplified version without Celery'
        }), 202

    except Exception as e:
        logger.error(f"Convert error: {e}")
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500

@bp.route('/api/status/<task_id>', methods=['GET'])
def status(task_id):
    """Get conversion status"""
    try:
        logger.info(f"Status check for task: {task_id}")
        
        # Mock status response
        return jsonify({
            'status': 'COMPLETED',
            'progress': 100,
            'message': 'Conversion completed successfully (mock)',
            'result': {
                'output_path': f'results/{task_id}.epub'
            }
        })

    except Exception as e:
        logger.error(f"Status check error: {e}")
        return jsonify({'error': f'Status check failed: {str(e)}'}), 500

@bp.route('/api/history', methods=['GET'])
def history():
    """Get conversion history"""
    try:
        logger.info("History endpoint called")
        
        # Mock history response
        return jsonify([
            {
                'id': 1,
                'task_id': 'mock-task-1',
                'filename': 'example1.pdf',
                'status': 'COMPLETED',
                'created_at': '2024-01-01T10:00:00Z',
                'pipeline_id': 'engines.medium'
            },
            {
                'id': 2,
                'task_id': 'mock-task-2', 
                'filename': 'example2.pdf',
                'status': 'PROCESSING',
                'created_at': '2024-01-01T11:00:00Z',
                'pipeline_id': 'engines.high'
            }
        ])

    except Exception as e:
        logger.error(f"History error: {e}")
        return jsonify({'error': f'History failed: {str(e)}'}), 500

@bp.route('/api/protected', methods=['GET'])
def protected():
    """Protected endpoint for testing authentication"""
    return jsonify({'message': 'Access granted (simplified version)'})
