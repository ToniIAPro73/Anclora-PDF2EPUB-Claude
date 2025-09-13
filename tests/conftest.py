import os
import sys
import pytest

# Add backend directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

# Configure in-memory databases before importing the app factory
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("CONVERSION_DB", ":memory:")
os.environ.setdefault("JWT_SECRET", "test-secret")

from app import create_app, db

@pytest.fixture
def app():
    app = create_app()
    app.config.update({"TESTING": True})
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
