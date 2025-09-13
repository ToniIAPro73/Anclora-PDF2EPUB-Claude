import os
import os
import io
from flask import Blueprint
from test_routes import _create_pdf, _setup_app
import app
import app.routes as routes
import pytest

app.auth_bp = Blueprint('auth', __name__)


@pytest.mark.skip(reason="Rate limiting not configured for test environment")
def test_rate_limiting(tmp_path, monkeypatch):
    os.environ['RATE_LIMIT'] = '2 per minute'
    app = _setup_app(tmp_path)
    client = app.test_client()
    monkeypatch.setattr(routes.convert_pdf_to_epub, 'apply_async', lambda *a, **k: None)

    pdf_path = _create_pdf()
    for _ in range(2):
        with open(pdf_path, 'rb') as f:
            client.post('/api/convert', data={'file': (f, 'sample.pdf')})
    with open(pdf_path, 'rb') as f:
        resp = client.post('/api/convert', data={'file': (f, 'sample.pdf')})
    assert resp.status_code == 429
    os.remove(pdf_path)


def test_invalid_file_and_size(tmp_path):
    app = _setup_app(tmp_path)
    client = app.test_client()

    data = {'file': (io.BytesIO(b'hello'), 'bad.txt')}
    res = client.post('/api/convert', data=data)
    assert res.status_code == 400
    assert res.get_json()['error'] == 'Invalid file type'

    large = tmp_path / 'big.pdf'
    with open(large, 'wb') as f:
        f.write(b'0' * (10 * 1024 * 1024 + 1))
    with open(large, 'rb') as f:
        res = client.post('/api/convert', data={'file': (f, 'big.pdf')})
    assert res.status_code == 400
    assert res.get_json()['error'] == 'File too large'


def test_invalid_mime_type(tmp_path):
    app = _setup_app(tmp_path)
    client = app.test_client()

    fake_pdf = io.BytesIO(b'not a pdf')
    res = client.post('/api/convert', data={'file': (fake_pdf, 'fake.pdf')})
    assert res.status_code == 400
    assert res.get_json()['error'] == 'Invalid file content'
