"""
Production WSGI entry point for the Anclora PDF2EPUB backend
"""
import os
from app import create_app

# Set production environment
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = 'False'

# Create the application instance for WSGI server
app = create_app()

# No __main__ block - this is intended only for WSGI servers