#!/usr/bin/env python3
"""Test script to start backend safely"""

import sys
import os
from app import create_app

def test_backend():
    try:
        print("Creating Flask app...")
        app = create_app()
        
        print("Starting Flask development server...")
        app.run(
            host='127.0.0.1',  # Use localhost instead of 0.0.0.0
            port=5175,
            debug=True,
            use_reloader=False,  # Disable reloader that might cause segfaults
            threaded=True
        )
        
    except Exception as e:
        print(f"Error starting backend: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_backend()