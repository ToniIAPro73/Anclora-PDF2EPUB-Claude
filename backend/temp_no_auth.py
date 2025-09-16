#!/usr/bin/env python3
"""
Temporary solution: Start backend without authentication for testing
This allows you to test PDF conversion while we fix the JWT issue
"""

import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_temp_app():
    """Create Flask app with authentication disabled"""
    from flask import Flask, request, jsonify, send_from_directory
    from werkzeug.utils import secure_filename
    import tempfile
    import uuid
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'temp_secret_for_testing'
    
    @app.route('/api/convert', methods=['POST'])
    def convert_no_auth():
        """Convert endpoint without authentication for testing"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Simulate successful conversion
            task_id = str(uuid.uuid4())
            
            return jsonify({
                'message': 'Conversion started successfully',
                'task_id': task_id,
                'status': 'PENDING'
            })
            
        except Exception as e:
            return jsonify({'error': f'Conversion failed: {str(e)}'}), 500
    
    @app.route('/api/status/<task_id>', methods=['GET'])
    def get_status(task_id):
        """Get conversion status (mock)"""
        return jsonify({
            'task_id': task_id,
            'status': 'COMPLETED',
            'message': 'Conversion completed successfully (DEMO MODE)'
        })
    
    @app.route('/api/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({'status': 'OK', 'mode': 'NO_AUTH_DEMO'})
    
    return app

if __name__ == '__main__':
    print("=" * 50)
    print("🔧 MODO TEMPORAL SIN AUTENTICACION")
    print("=" * 50)
    print("⚠️  SOLO PARA TESTING - NO USAR EN PRODUCCION")
    print("")
    print("✅ Backend temporal en: http://127.0.0.1:5175")
    print("✅ Conversion endpoint: /api/convert (sin auth)")
    print("✅ Status endpoint: /api/status/<task_id>")
    print("")
    print("Mientras configuramos JWT correctamente...")
    print("=" * 50)
    
    app = create_temp_app()
    app.run(host='127.0.0.1', port=5175, debug=True)