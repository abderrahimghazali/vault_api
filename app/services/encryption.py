"""Encryption service for secure data storage."""

import os
from typing import Tuple

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from app.config import settings


class EncryptionService:
    """Service for AES-256-GCM encryption/decryption."""

    def __init__(self):
        self.key = settings.encryption_key_bytes

    def encrypt(self, plaintext: str) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypt plaintext using AES-256-GCM.

        Args:
            plaintext: String to encrypt

        Returns:
            Tuple of (ciphertext, nonce, tag)
        """
        # Generate random nonce
        nonce = os.urandom(12)

        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.GCM(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()

        # Encrypt
        ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()

        return ciphertext, nonce, encryptor.tag

    def decrypt(self, ciphertext: bytes, nonce: bytes, tag: bytes) -> str:
        """
        Decrypt ciphertext using AES-256-GCM.

        Args:
            ciphertext: Encrypted data
            nonce: Nonce used for encryption
            tag: Authentication tag

        Returns:
            Decrypted plaintext
        """
        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.GCM(nonce, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()

        # Decrypt
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        return plaintext.decode()


# Singleton instance
encryption_service = EncryptionService()