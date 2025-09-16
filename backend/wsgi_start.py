#!/usr/bin/env python3
"""WSGI-based backend starter to avoid Flask dev server segfaults"""

import os
import sys
from app import create_app

# Create the Flask application
application = create_app()

if __name__ == '__main__':
    print("Starting backend with Waitress WSGI server...")
    try:
        # Try using waitress if available
        from waitress import serve
        print("Using Waitress WSGI server on http://127.0.0.1:5175")
        serve(application, host='127.0.0.1', port=5175)
    except ImportError:
        print("Waitress not available, installing...")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'waitress'])
        from waitress import serve
        print("Using Waitress WSGI server on http://127.0.0.1:5175")
        serve(application, host='127.0.0.1', port=5175)