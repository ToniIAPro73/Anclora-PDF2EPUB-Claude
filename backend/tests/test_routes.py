import os
import sys
import tempfile
from unittest.mock import MagicMock
import fitz

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
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
    os.environ['CONVERSION_DB'] = str(tmpdir / 'conv.db')
    return create_app()


def test_api_convert_returns_task_id(tmp_path, monkeypatch):
    app = _setup_app(tmp_path)
    client = app.test_client()

    monkeypatch.setattr(routes, 'create_conversion', lambda task_id: None)
    mock_apply = MagicMock()
    monkeypatch.setattr(routes.convert_pdf_to_epub, 'apply_async', mock_apply)

    pdf_path = _create_pdf()
    with open(pdf_path, 'rb') as f:
        response = client.post('/api/convert', data={'file': (f, 'sample.pdf')})

    assert response.status_code == 202
    task_id = response.get_json().get('task_id')
    assert task_id
    mock_apply.assert_called_once()
    assert mock_apply.call_args.kwargs.get('task_id') == task_id
    os.remove(pdf_path)


def test_api_status_returns_result(tmp_path, monkeypatch):
    app = _setup_app(tmp_path)
    client = app.test_client()

    class Dummy:
        state = 'SUCCESS'
        result = {'ok': True}

    monkeypatch.setattr(routes, 'AsyncResult', lambda tid, app: Dummy())

    response = client.get('/api/status/test-id')
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
