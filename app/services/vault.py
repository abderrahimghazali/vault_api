"""Vault service for managing encrypted data with embeddings."""

import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.database import VaultItem
from app.models.vault import TextInput, SearchRequest, SearchResult
from app.services.embedding import embedding_service
from app.services.encryption import encryption_service

logger = logging.getLogger(__name__)


class VaultService:
    """Service for vault operations."""

    async def create_item(self, db: Session, text_input: TextInput) -> VaultItem:
        """Create a new vault item with encrypted text and embedding."""
        # Encrypt text
        ciphertext, nonce, tag = encryption_service.encrypt(text_input.text)

        # Generate embedding
        embedding = await embedding_service.generate_embedding(text_input.text)
        if not embedding:
            raise ValueError("Failed to generate embedding")

        # Create database item
        db_item = VaultItem(
            encrypted_data=ciphertext,
            nonce=nonce,
            tag=tag,
            embedding=embedding
        )

        db.add(db_item)
        db.commit()
        db.refresh(db_item)

        return db_item

    def get_item(self, db: Session, item_id: UUID) -> Optional[VaultItem]:
        """Get vault item by ID."""
        return db.query(VaultItem).filter(VaultItem.id == item_id).first()

    def decrypt_item(self, item: VaultItem) -> str:
        """Decrypt vault item data."""
        return encryption_service.decrypt(
            item.encrypted_data,
            item.nonce,
            item.tag
        )

    async def search_items(
        self,
        db: Session,
        search_request: SearchRequest
    ) -> List[SearchResult]:
        """Search vault items by similarity."""
        # Generate embedding for query
        query_embedding = await embedding_service.generate_embedding(search_request.text)
        if not query_embedding:
            return []

        # Convert embedding to the proper format for database query
        # Format as a vector string that PostgreSQL can understand
        vector_str = '[' + ','.join(map(str, query_embedding)) + ']'

        # Use raw SQL for vector similarity search without ORDER BY due to pgvector issues
        # We'll get all results and sort them in Python
        from sqlalchemy import text
        query_sql = f"""
            SELECT 
                id, encrypted_data, nonce, tag, created_at,
                embedding <=> '{vector_str}'::vector as distance
            FROM vault_items
        """
        
        all_results = db.execute(text(query_sql)).fetchall()
        # Sort by distance in Python and limit
        sorted_results = sorted(all_results, key=lambda x: x.distance)
        results = sorted_results[:search_request.limit]

        # Convert to response models with decrypted text
        search_results = []
        for row in results:
            try:
                # Ensure binary fields are properly converted to bytes
                encrypted_data = bytes(row.encrypted_data) if not isinstance(row.encrypted_data, bytes) else row.encrypted_data
                nonce = bytes(row.nonce) if not isinstance(row.nonce, bytes) else row.nonce
                tag = bytes(row.tag) if not isinstance(row.tag, bytes) else row.tag
                
                decrypted_text = encryption_service.decrypt(
                    encrypted_data, 
                    nonce, 
                    tag
                )
                similarity = 1 - row.distance

                search_results.append(
                    SearchResult(
                        id=row.id,
                        text=decrypted_text,
                        similarity=similarity,
                        created_at=row.created_at
                    )
                )
            except Exception as e:
                logger.error(f"Failed to decrypt item {row.id}: {e}")
                continue

        return search_results


# Singleton instance
vault_service = VaultService()