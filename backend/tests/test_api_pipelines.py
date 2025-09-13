import os
import sys
import tempfile
import fitz
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db


def _create_pdf() -> str:
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    doc = fitz.open()
    doc.new_page().insert_text((72, 72), "hello")
    doc.save(path)
    doc.close()
    return path


def _setup_app(tmpdir):
    os.environ['UPLOAD_FOLDER'] = str(tmpdir / 'uploads')
    os.environ['RESULTS_FOLDER'] = str(tmpdir / 'results')
    os.environ['DATABASE_URL'] = 'sqlite:///' + str(tmpdir / 'app.db')
    os.environ['SECRET_KEY'] = 'test-secret'
    app = create_app()
    with app.app_context():
        db.create_all()
    return app


def test_analyze_endpoint_returns_pipeline(tmp_path):
    app = _setup_app(tmp_path)
    client = app.test_client()

    pdf_path = _create_pdf()
    with open(pdf_path, 'rb') as f:
        response = client.post('/api/analyze', data={'file': (f, 'sample.pdf')})

    os.remove(pdf_path)
    assert response.status_code == 200, '/api/analyze not implemented'
    data = response.get_json()
    assert 'pipeline_id' in data


def test_convert_accepts_pipeline_id(tmp_path, monkeypatch):
    app = _setup_app(tmp_path)
    client = app.test_client()

    class Dummy:
        def __init__(self, *a, **k):
            self.id = 'task'

        def apply_async(self, args=None, task_id=None):
            return None

    monkeypatch.setattr('app.routes.convert_pdf_to_epub', Dummy())

    pdf_path = _create_pdf()
    with open(pdf_path, 'rb') as f:
        response = client.post('/api/convert', data={'file': (f, 'sample.pdf'), 'pipeline_id': 'sample'})

    os.remove(pdf_path)
    assert response.status_code == 202, 'pipeline_id not handled'
