"""Database migrations and initialization."""

import logging

from sqlalchemy import text

from app.db.connection import engine
from app.models.database import Base

logger = logging.getLogger(__name__)


def init_database():
    """Initialize database with required extensions and tables."""
    logger.info("Initializing database...")

    # Create pgvector extension
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            logger.info("pgvector extension created/verified")
        except Exception as e:
            logger.error(f"Failed to create pgvector extension: {e}")
            raise

    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")


def create_indexes():
    """Create database indexes for better performance."""
    with engine.connect() as conn:
        try:
            # Create vector similarity search index
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_vault_items_embedding "
                    "ON vault_items USING ivfflat (embedding vector_cosine_ops) "
                    "WITH (lists = 100)"
                )
            )
            conn.commit()
            logger.info("Database indexes created/verified")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise