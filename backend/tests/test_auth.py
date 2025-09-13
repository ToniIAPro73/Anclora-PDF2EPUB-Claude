import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app


def _setup_app(tmpdir):
    os.environ['UPLOAD_FOLDER'] = str(tmpdir / 'uploads')
    os.environ['RESULTS_FOLDER'] = str(tmpdir / 'results')
    os.environ['CONVERSION_DB'] = str(tmpdir / 'conv.db')
    os.environ['DATABASE_URL'] = 'sqlite:///' + str(tmpdir / 'app.db')
    os.environ['JWT_SECRET'] = 'test-secret'
    return create_app()


def test_register_and_login(tmp_path):
    app = _setup_app(tmp_path)
    client = app.test_client()

    resp = client.post('/api/auth/register', json={'email': 'a@a.com', 'password': 'pw'})
    assert resp.status_code == 201
    token = resp.get_json().get('token')
    assert token

    resp = client.post('/api/auth/login', json={'email': 'a@a.com', 'password': 'pw'})
    assert resp.status_code == 200
    assert resp.get_json().get('token')
