"""Database models for Vault API."""

from datetime import datetime
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class VaultItem(Base):
    """Database model for vault items."""

    __tablename__ = "vault_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    encrypted_data = Column(LargeBinary, nullable=False)
    nonce = Column(LargeBinary, nullable=False)
    tag = Column(LargeBinary, nullable=False)
    embedding = Column(Vector(1536), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<VaultItem(id={self.id})>"