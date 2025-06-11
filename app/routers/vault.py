"""Vault API endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.models.vault import (
    TextInput,
    TextResponse,
    TextDecrypted,
    SearchRequest,
    SearchResult,
)
from app.services.vault import vault_service

router = APIRouter(prefix="/vault", tags=["vault"])


@router.post("/encrypt", response_model=TextResponse)
async def encrypt_text(
    text_input: TextInput,
    db: Session = Depends(get_db)
):
    """Encrypt and store text with embedding."""
    try:
        db_item = await vault_service.create_item(db, text_input)
        return TextResponse(id=db_item.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/decrypt/{item_id}", response_model=TextDecrypted)
async def decrypt_text(
    item_id: UUID,
    db: Session = Depends(get_db)
):
    """Decrypt and return stored text."""
    item = vault_service.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    try:
        decrypted_text = vault_service.decrypt_item(item)
        return TextDecrypted(
            id=item.id,
            text=decrypted_text,
            created_at=item.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")


@router.post("/search", response_model=List[SearchResult])
async def search_texts(
    search_request: SearchRequest,
    db: Session = Depends(get_db)
):
    """Search encrypted texts by semantic similarity."""
    try:
        results = await vault_service.search_items(db, search_request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))