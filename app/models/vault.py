"""Pydantic models for API requests and responses."""

from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field


class TextInput(BaseModel):
    """Request model for text input."""

    text: str = Field(..., description="Text to encrypt and store")


class TextResponse(BaseModel):
    """Response model for encrypted text."""

    id: UUID
    message: str = "Text encrypted and stored successfully"


class TextDecrypted(BaseModel):
    """Response model with decrypted text."""

    id: UUID
    text: str
    created_at: datetime


class SearchRequest(BaseModel):
    """Request model for searching texts."""

    text: str = Field(..., description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Maximum results")


class SearchResult(BaseModel):
    """Search result model."""

    id: UUID
    text: str
    similarity: float
    created_at: datetime