"""Encryption/decryption utilities for securing .env profiles."""

import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet


SALT_SIZE = 16
ITERATIONS = 390000


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt(data: str, password: str) -> bytes:
    """Encrypt plaintext data with a password. Returns salt + ciphertext."""
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    token = Fernet(key).encrypt(data.encode())
    return salt + token


def decrypt(payload: bytes, password: str) -> str:
    """Decrypt payload (salt + ciphertext) with a password."""
    salt = payload[:SALT_SIZE]
    token = payload[SALT_SIZE:]
    key = derive_key(password, salt)
    return Fernet(key).decrypt(token).decode()
