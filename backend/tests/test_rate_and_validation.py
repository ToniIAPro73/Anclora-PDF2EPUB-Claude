import os
import io
from test_routes import _create_pdf, _setup_app
import app.routes as routes


def test_rate_limiting(tmp_path, monkeypatch):
    os.environ['RATE_LIMIT'] = '2 per minute'
    app = _setup_app(tmp_path)
    client = app.test_client()
    monkeypatch.setattr(routes, 'create_conversion', lambda task_id: None)
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
