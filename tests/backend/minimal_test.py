#!/usr/bin/env python3
"""Minimal test to isolate the segfault cause"""

import os
import sys

def test_minimal_app():
    print("Creating minimal Flask app...")
    
    from flask import Flask
    from app import config  # This loads environment variables
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    
    app = Flask(__name__)
    
    # Basic config
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        UPLOAD_FOLDER=os.environ.get('UPLOAD_FOLDER', 'uploads'),
    )
    
    limiter = Limiter(key_func=get_remote_address)
    limiter.init_app(app)
    
    @app.route('/')
    def hello():
        return "Hello World!"
    
    print("App created successfully. Starting server...")
    
    # Try running with different configurations
    app.run(
        host='127.0.0.1',
        port=5175,
        debug=False,
        use_reloader=False,
        threaded=True
    )

if __name__ == '__main__':
    test_minimal_app()