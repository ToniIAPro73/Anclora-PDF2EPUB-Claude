import os
import sys
import tempfile
from unittest.mock import MagicMock
import fitz
import io
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
import app.routes as routes


def _create_pdf() -> str:
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "hello")
    doc.save(path)
    doc.close()
    return path


def _setup_app(tmpdir):
    os.environ['UPLOAD_FOLDER'] = str(tmpdir / 'uploads')
    os.environ['RESULTS_FOLDER'] = str(tmpdir / 'results')
    os.environ['THUMBNAIL_FOLDER'] = str(tmpdir / 'thumbnails')
    os.environ['DATABASE_URL'] = 'sqlite:///' + str(tmpdir / 'app.db')
    os.environ['SECRET_KEY'] = 'test-secret'
    app = create_app()
    logging.getLogger().handlers = []
    logging.basicConfig(level=logging.INFO)
    with app.app_context():
        db.create_all()
    return app


def test_api_convert_returns_task_id(tmp_path, monkeypatch):
    app = _setup_app(tmp_path)
    client = app.test_client()

    client.post('/api/register', json={'username': 'alice', 'password': 'pw'})
    token = client.post('/api/login', json={'username': 'alice', 'password': 'pw'}).get_json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    mock_apply = MagicMock()
    monkeypatch.setattr(routes.convert_pdf_to_epub, 'apply_async', mock_apply)

    pdf_path = _create_pdf()
    with open(pdf_path, 'rb') as f:
        response = client.post('/api/convert', headers=headers, data={'file': (f, 'sample.pdf'), 'pipeline_id': 'rapid'})

    assert response.status_code == 202
    task_id = response.get_json().get('task_id')
    assert task_id
    mock_apply.assert_called_once()
    assert mock_apply.call_args.kwargs.get('task_id') == task_id
    assert mock_apply.call_args.kwargs['queue'] == 'conversions'
    assert mock_apply.call_args.kwargs['args'][3] == 'rapid'
    assert response.get_json()['queue'] == 'conversions'
    os.remove(pdf_path)


def test_rejects_invalid_mime_and_logs(tmp_path, caplog):
    app = _setup_app(tmp_path)
    client = app.test_client()

    fake_file = io.BytesIO(b"not a pdf")
    with caplog.at_level('WARNING'):
        response = client.post('/api/convert', data={'file': (fake_file, 'fake.pdf')})

    assert response.status_code == 400


def test_rejects_large_file(tmp_path, monkeypatch):
    app = _setup_app(tmp_path)
    client = app.test_client()

    monkeypatch.setattr(routes, 'MAX_FILE_SIZE', 10)
    pdf_path = _create_pdf()
    with open(pdf_path, 'rb') as f:
        response = client.post('/api/convert', data={'file': (f, 'big.pdf')})

    assert response.status_code == 400
    assert response.get_json()['error'] == 'File too large'
    os.remove(pdf_path)


def test_sanitizes_filename(tmp_path, monkeypatch):
    app = _setup_app(tmp_path)
    client = app.test_client()

    monkeypatch.setattr(routes.convert_pdf_to_epub, 'apply_async', lambda *a, **k: None)

    pdf_path = _create_pdf()
    with open(pdf_path, 'rb') as f:
        response = client.post('/api/convert', data={'file': (f, '../evil.pdf')})

    assert response.status_code == 202
    saved_files = list((tmp_path / 'uploads').iterdir())
    assert len(saved_files) == 1
    assert saved_files[0].name.endswith('evil.pdf')
    assert '..' not in saved_files[0].name
    os.remove(pdf_path)


def test_api_status_returns_result(tmp_path, monkeypatch):
    app = _setup_app(tmp_path)
    client = app.test_client()

    client.post('/api/register', json={'username': 'alice', 'password': 'pw'})
    token = client.post('/api/login', json={'username': 'alice', 'password': 'pw'}).get_json()['token']
    headers = {'Authorization': f'Bearer {token}'}

    class Dummy:
        state = 'SUCCESS'
        result = {'ok': True}

    monkeypatch.setattr(routes, 'AsyncResult', lambda tid, app: Dummy())

    response = client.get('/api/status/test-id', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'SUCCESS'
    assert data['result'] == {'ok': True}


def test_metrics_endpoint(tmp_path):
    app = _setup_app(tmp_path)
    client = app.test_client()
    response = client.get('/metrics')
    assert response.status_code == 200
    assert b'http_requests_total' in response.data


def test_analyze_returns_options(tmp_path):
    app = _setup_app(tmp_path)
    client = app.test_client()

    pdf_path = _create_pdf()
    with open(pdf_path, 'rb') as f:
        response = client.post('/api/analyze', data={'file': (f, 'sample.pdf')})

    assert response.status_code == 200
    data = response.get_json()
    assert 'recommended' in data
    assert len(data['options']) == 3
    os.remove(pdf_path)


def test_invalid_pipeline_id(tmp_path, monkeypatch):
    app = _setup_app(tmp_path)
    client = app.test_client()
    monkeypatch.setattr(routes.convert_pdf_to_epub, 'apply_async', lambda *a, **k: None)

    pdf_path = _create_pdf()
    with open(pdf_path, 'rb') as f:
        res = client.post('/api/convert', data={'file': (f, 'sample.pdf'), 'pipeline_id': 'unknown'})

    assert res.status_code == 400
    assert res.get_json()['error'] == 'Invalid pipeline_id'
    os.remove(pdf_path)


def test_health_endpoint(tmp_path, monkeypatch):
    app = _setup_app(tmp_path)
    client = app.test_client()

    class DummyInspect:
        def ping(self):
            return {'worker@localhost': 'pong'}

    class DummyControl:
        def inspect(self):
            return DummyInspect()

    class DummyCelery:
        control = DummyControl()

    monkeypatch.setattr(routes, 'celery_app', DummyCelery())

    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] in ('ok', 'degraded')
    assert set(data['directories'].keys()) == {'uploads', 'results', 'thumbnails'}
