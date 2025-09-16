from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Text, Numeric, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from .database import Base


class Conversion(Base):
    __tablename__ = 'conversions'

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(36), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), index=True)  # Agregar user_id
    pipeline_id = Column(String(50), index=True)  # Agregar pipeline usado
    credits_cost = Column(Integer, default=0)  # Costo en créditos
    status = Column(String(50), nullable=False, default='PENDING')
    output_path = Column(String(255))
    thumbnail_path = Column(String(255))
    metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'task_id': self.task_id,
            'user_id': str(self.user_id) if self.user_id else None,
            'pipeline_id': self.pipeline_id,
            'credits_cost': self.credits_cost,
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


class CreditTransaction(Base):
    """Modelo para transacciones de créditos"""
    __tablename__ = 'credit_transactions'

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    amount = Column(Integer, nullable=False)  # Positivo: ganado, Negativo: gastado
    transaction_type = Column(String(50), nullable=False)  # initial_bonus, conversion_cost, referral_bonus, admin_adjustment
    conversion_id = Column(String(255))  # ID de conversión si aplica
    pipeline_id = Column(String(50))  # Pipeline usado
    description = Column(Text)
    meta_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': str(self.user_id),
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'conversion_id': self.conversion_id,
            'pipeline_id': self.pipeline_id,
            'description': self.description,
            'metadata': self.meta_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class PipelineCost(Base):
    """Modelo para configuración de costos de pipelines"""
    __tablename__ = 'pipeline_costs'

    id = Column(BigInteger, primary_key=True, index=True)
    pipeline_id = Column(String(50), unique=True, nullable=False)
    base_cost = Column(Integer, nullable=False)
    cost_per_page = Column(Integer, default=0)
    quality_multiplier = Column(Numeric(3, 2), default=1.0)
    description = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'pipeline_id': self.pipeline_id,
            'base_cost': self.base_cost,
            'cost_per_page': self.cost_per_page,
            'quality_multiplier': float(self.quality_multiplier) if self.quality_multiplier else 1.0,
            'description': self.description,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Referral(Base):
    """Modelo para sistema de referidos"""
    __tablename__ = 'referrals'

    id = Column(BigInteger, primary_key=True, index=True)
    referrer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    referred_id = Column(UUID(as_uuid=True), index=True)
    referral_code = Column(String(20), nullable=False, index=True)
    email_invited = Column(String(255))
    phone_invited = Column(String(20))
    status = Column(String(20), default='pending')  # pending, registered, verified, expired
    credits_awarded_referrer = Column(Integer, default=0)
    credits_awarded_referred = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'referrer_id': str(self.referrer_id),
            'referred_id': str(self.referred_id) if self.referred_id else None,
            'referral_code': self.referral_code,
            'email_invited': self.email_invited,
            'phone_invited': self.phone_invited,
            'status': self.status,
            'credits_awarded_referrer': self.credits_awarded_referrer,
            'credits_awarded_referred': self.credits_awarded_referred,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }


