from datetime import datetime
from . import db


class Conversion(db.Model):
    __tablename__ = 'conversions'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(36), unique=True, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='PENDING')
    output_path = db.Column(db.String(255))
    metrics = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'task_id': self.task_id,
            'status': self.status,
            'output_path': self.output_path,
            'metrics': self.metrics,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
