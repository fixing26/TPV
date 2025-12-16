"""
Security utilities module.

Handles password hashing (using bcrypt) and JWT token generation.
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import hashlib
import base64

from ..config import settings

import bcrypt

ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password (str): The plain text password.
        hashed_password (str): The bcrypt hash.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    # Pre-hash con SHA-256 (digest) + Base64 para reducir longitud
    password_bytes = plain_password.encode('utf-8')
    password_hash_bytes = hashlib.sha256(password_bytes).digest()
    password_hash_b64 = base64.b64encode(password_hash_bytes) # bcrypt expects bytes
    
    # hashed_password viene como str de la DB, bcrypt necesita bytes
    return bcrypt.checkpw(password_hash_b64, hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password (str): The plain text password.

    Returns:
        str: The hashed password.
    """
    # Pre-hash con SHA-256 (digest) + Base64
    password_bytes = password.encode('utf-8')
    password_hash_bytes = hashlib.sha256(password_bytes).digest()
    password_hash_b64 = base64.b64encode(password_hash_bytes) # bcrypt expects bytes
    
    # Generar salt y hash
    hashed = bcrypt.hashpw(password_hash_b64, bcrypt.gensalt())
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: int | None = None):
    """
    Create a JWT access token.

    Args:
        data (dict): Payload data to encode in the token.
        expires_delta (int | None): Optional expiration time in minutes.

    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=expires_delta or settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt
