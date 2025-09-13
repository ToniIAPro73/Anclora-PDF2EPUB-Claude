import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from test_routes import _setup_app


def test_register_login_and_access(tmp_path):
    app = _setup_app(tmp_path)
    client = app.test_client()

    res = client.post('/api/register', json={'username': 'alice', 'password': 'secret'})
    assert res.status_code == 201

    res = client.post('/api/login', json={'username': 'alice', 'password': 'secret'})
    assert res.status_code == 200
    token = res.get_json()['token']

    res = client.get('/api/protected', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 200

    res = client.get('/api/protected', headers={'Authorization': 'Bearer wrong'})
    assert res.status_code == 401
