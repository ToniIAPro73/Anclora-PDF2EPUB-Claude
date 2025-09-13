import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from test_routes import _setup_app


def test_register_login_and_access(tmp_path):
    app = _setup_app(tmp_path)
    client = app.test_client()

    res = client.post('/api/auth/register', json={'email': 'alice@example.com', 'password': 'secret'})
    assert res.status_code == 201
    token = res.get_json()['token']

    res = client.get('/api/protected', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200

    res = client.get('/api/protected', headers={'Authorization': 'Bearer wrong'})
    assert res.status_code == 401


def test_history_authorization(tmp_path):
    app = _setup_app(tmp_path)
    client = app.test_client()

    token = client.post('/api/auth/register', json={'email': 'bob@example.com', 'password': 'pw'}).get_json()['token']

    res = client.get('/api/history', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200

    res = client.get('/api/history')
    assert res.status_code == 401
