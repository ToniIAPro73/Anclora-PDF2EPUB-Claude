import os
import tempfile
import os
import sys
from ebooklib import epub

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models import Conversion


def _setup_app(tmpdir):
    os.environ['UPLOAD_FOLDER'] = str(tmpdir / 'uploads')
    os.environ['RESULTS_FOLDER'] = str(tmpdir / 'results')
    os.environ['DATABASE_URL'] = 'sqlite:///' + str(tmpdir / 'app.db')
    os.environ['SECRET_KEY'] = 'test-secret'
    app = create_app()
    with app.app_context():
        db.create_all()
    return app


def _create_epub(path):
    book = epub.EpubBook()
    book.set_identifier('id')
    book.set_title('Title')
    c1 = epub.EpubHtml(title='Intro', file_name='intro.xhtml', content='<h1>hola</h1>')
    book.add_item(c1)
    book.toc = (epub.Link('intro.xhtml', 'Intro', 'intro'),)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ['nav', c1]
    epub.write_epub(path, book)


def test_preview_endpoint_returns_html(tmp_path):
    app = _setup_app(tmp_path)
    client = app.test_client()
    client.post('/api/register', json={'username': 'bob', 'password': 'pw'})
    token = client.post('/api/login', json={'username': 'bob', 'password': 'pw'}).get_json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    epub_path = tmp_path / 'results' / 'book.epub'
    os.makedirs(epub_path.parent, exist_ok=True)
    _create_epub(str(epub_path))
    with app.app_context():
        conv = Conversion(task_id='abc', status='SUCCESS', output_path=str(epub_path))
        db.session.add(conv)
        db.session.commit()
    res = client.get('/api/preview/abc', headers=headers)
    assert res.status_code == 200
    data = res.get_json()
    assert '<h1>hola</h1>' in data['pages'][0]
