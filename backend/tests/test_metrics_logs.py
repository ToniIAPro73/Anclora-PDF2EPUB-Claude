import os
import logging
from test_routes import _create_pdf, _setup_app
import app.routes as routes


def test_metrics_and_logs(tmp_path, monkeypatch, caplog):
    app = _setup_app(tmp_path)
    client = app.test_client()
    monkeypatch.setattr(routes, 'create_conversion', lambda task_id: None)
    monkeypatch.setattr(routes.convert_pdf_to_epub, 'apply_async', lambda *a, **k: None)

    pdf_path = _create_pdf()
    caplog.set_level(logging.INFO)
    with open(pdf_path, 'rb') as f:
        client.post('/api/convert', data={'file': (f, 'sample.pdf')})
    assert any('Conversion requested' in r.message for r in caplog.records)

    resp = client.get('/metrics')
    assert resp.status_code == 200
    assert 'pdf_conversions_total' in resp.get_data(as_text=True)
    os.remove(pdf_path)
