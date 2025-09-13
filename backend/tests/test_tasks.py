import os
import sys
import json
import sqlite3
import importlib
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(scope="module")
def task_env(tmp_path_factory):
    tmpdir = tmp_path_factory.mktemp("db")
    db_path = str(tmpdir / "conv.db")
    os.environ["CONVERSION_DB"] = db_path
    os.environ["DATABASE_URL"] = "sqlite:///" + db_path
    models = importlib.import_module("app.models")
    models.db.Model.metadata.clear()
    importlib.reload(models)
    models.init_db()
    tasks = importlib.import_module("app.tasks")
    return tasks, models


def test_convert_pdf_to_epub_success(task_env):
    tasks, models = task_env
    models.create_conversion("t1")

    class DummyConverter:
        def convert(self, input_path, output_path=None, engine=None):
            return {
                "success": True,
                "output_path": "out.epub",
                "message": "ok",
                "quality_metrics": {"score": 1},
                "engine_used": "rapid",
                "analysis": {"pages": 1},
            }

    tasks.converter = DummyConverter()
    result = tasks.convert_pdf_to_epub("t1", "input.pdf")
    assert result["success"] is True

    with sqlite3.connect(os.environ["CONVERSION_DB"]) as conn:
        row = conn.execute(
            "SELECT status, output_path, metrics FROM conversions WHERE task_id=?",
            ("t1",),
        ).fetchone()
    assert row[0] == "SUCCESS"
    assert row[1] == "out.epub"
    metrics = json.loads(row[2])
    assert metrics["engine_used"] == "rapid"
    assert "duration" in metrics


def test_convert_pdf_to_epub_failure(task_env):
    tasks, models = task_env
    models.create_conversion("t2")

    class DummyConverter:
        def convert(self, input_path, output_path=None, engine=None):
            raise RuntimeError("boom")

    tasks.converter = DummyConverter()
    result = tasks.convert_pdf_to_epub("t2", "input.pdf")
    assert result["success"] is False

    with sqlite3.connect(os.environ["CONVERSION_DB"]) as conn:
        row = conn.execute(
            "SELECT status, output_path, metrics FROM conversions WHERE task_id=?",
            ("t2",),
        ).fetchone()
    assert row[0] == "FAILURE"
    assert row[1] is None
    metrics = json.loads(row[2])
    assert metrics["error"] == "boom"
    assert "duration" in metrics
