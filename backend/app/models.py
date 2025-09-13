import sqlite3
import os
import json
from contextlib import closing

DB_PATH = os.environ.get('CONVERSION_DB', os.path.join(os.path.dirname(__file__), '..', 'conversions.db'))


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    with closing(get_connection()) as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE,
                status TEXT,
                output_path TEXT,
                metrics TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def create_conversion(task_id, status="PENDING"):
    with closing(get_connection()) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO conversions (task_id, status) VALUES (?, ?)",
            (task_id, status),
        )
        conn.commit()


def update_conversion(task_id, status, output_path=None, metrics=None):
    metrics_json = json.dumps(metrics) if metrics is not None else None
    with closing(get_connection()) as conn:
        c = conn.cursor()
        c.execute(
            "UPDATE conversions SET status=?, output_path=?, metrics=? WHERE task_id=?",
            (status, output_path, metrics_json, task_id),
        )
        conn.commit()


def fetch_conversions(page=1, per_page=10):
    offset = (page - 1) * per_page
    with closing(get_connection()) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(
            """
            SELECT id, task_id, status, output_path, metrics, created_at
            FROM conversions
            ORDER BY id DESC
            LIMIT ? OFFSET ?
            """,
            (per_page, offset),
        )
        rows = c.fetchall()
    results = []
    for row in rows:
        data = dict(row)
        if data.get("metrics"):
            data["metrics"] = json.loads(data["metrics"])
        results.append(data)
    return results

