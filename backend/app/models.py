from datetime import datetime
import sqlite3
import os
from . import db


class Conversion(db.Model):
    __tablename__ = 'conversions'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(36), unique=True, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='PENDING')
    output_path = db.Column(db.String(255))
    thumbnail_path = db.Column(db.String(255))
    metrics = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'task_id': self.task_id,
            'status': self.status,
            'output_path': self.output_path,
            'thumbnail_path': self.thumbnail_path,
            'metrics': self.metrics,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


def init_db():
    db_path = os.environ.get('CONVERSION_DB', 'app.db')
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS conversions ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            " task_id TEXT UNIQUE,"
            " status TEXT,"
            " output_path TEXT,"
            " thumbnail_path TEXT,"
            " metrics TEXT,"
            " created_at TEXT)"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password_hash TEXT)"
        )
        conn.commit()


def create_conversion(task_id):
    db_path = os.environ.get('CONVERSION_DB', 'app.db')
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO conversions (task_id, status, created_at) VALUES (?, ?, ?)",
            (task_id, 'PENDING', datetime.utcnow().isoformat()),
        )
        conn.commit()
