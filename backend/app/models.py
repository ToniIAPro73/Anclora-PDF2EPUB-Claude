from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from .database import Base


class Conversion(Base):
    __tablename__ = 'conversions'

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(36), unique=True, nullable=False, index=True)
    status = Column(String(50), nullable=False, default='PENDING')
    output_path = Column(String(255))
    thumbnail_path = Column(String(255))
    metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

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


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


