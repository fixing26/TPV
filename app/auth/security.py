
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import hashlib
import base64

from ..config import settings

import bcrypt

ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Pre-hash con SHA-256 (digest) + Base64 para reducir longitud
    password_bytes = plain_password.encode('utf-8')
    password_hash_bytes = hashlib.sha256(password_bytes).digest()
    password_hash_b64 = base64.b64encode(password_hash_bytes) # bcrypt expects bytes
    
    # hashed_password viene como str de la DB, bcrypt necesita bytes
    return bcrypt.checkpw(password_hash_b64, hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    # Pre-hash con SHA-256 (digest) + Base64
    password_bytes = password.encode('utf-8')
    password_hash_bytes = hashlib.sha256(password_bytes).digest()
    password_hash_b64 = base64.b64encode(password_hash_bytes) # bcrypt expects bytes
    
    # Generar salt y hash
    hashed = bcrypt.hashpw(password_hash_b64, bcrypt.gensalt())
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: int | None = None):

    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=expires_delta or settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt
