"""Configuration management for Vault API."""

import base64
import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API Settings
    api_version: str = "v1"
    api_title: str = "Vault API"
    api_description: str = "Secure data storage with embeddings and encryption"
    debug: bool = False

    # OpenAI Settings
    openai_api_key: str
    openai_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # Database Settings
    database_url: str
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # Encryption Settings
    encryption_key: str

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def encryption_key_bytes(self) -> bytes:
        """Get encryption key as bytes."""
        try:
            # Try base64 decoding first
            key = base64.b64decode(self.encryption_key)
            if len(key) != 32:
                raise ValueError("Encryption key must be 32 bytes")
            return key
        except Exception:
            # Fall back to hex decoding
            key = bytes.fromhex(self.encryption_key)
            if len(key) != 32:
                raise ValueError("Encryption key must be 32 bytes")
            return key


settings = Settings()