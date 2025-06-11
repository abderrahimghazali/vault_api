"""Health check endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.connection import get_db

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "service": "vault-api"}


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check including database connectivity."""
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected",
            "service": "vault-api"
        }
    except Exception as e:
        return {
            "status": "not ready",
            "database": "disconnected",
            "error": str(e)
        }