#!/usr/bin/env python3
print("Testing basic Python import...")

try:
    import flask
    print("OK: Flask import")
except Exception as e:
    print(f"ERROR: Flask import failed: {e}")

try:
    from flask import Flask
    print("OK: Flask class import")
except Exception as e:
    print(f"ERROR: Flask class import failed: {e}")

try:
    from flask_cors import CORS
    print("OK: Flask-CORS import")
except Exception as e:
    print(f"ERROR: Flask-CORS import failed: {e}")

try:
    import pymupdf
    print("OK: PyMuPDF import")
except Exception as e:
    print(f"ERROR: PyMuPDF import failed: {e}")

try:
    from app import config
    print("OK: App config import")
except Exception as e:
    print(f"ERROR: App config import failed: {e}")

try:
    from app import create_app
    print("OK: App create_app import")
except Exception as e:
    print(f"ERROR: App create_app import failed: {e}")

print("Test completed!")