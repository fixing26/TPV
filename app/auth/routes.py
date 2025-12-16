"""
Authentication routes module.

Handles user registration and login endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .models import User
from .schemas import UserCreate, UserOut, Token
from .security import get_password_hash, verify_password, create_access_token
from ..db import get_session

router = APIRouter()

@router.post("/register", response_model=UserOut)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_session)):
    """
    Register a new user.

    Args:
        user_in (UserCreate): User registration data (username, password).
        db (AsyncSession): Database session.

    Returns:
        UserOut: The created user.

    Raises:
        HTTPException: If the username already exists.
    """
    try:
        result = await db.execute(select(User).where(User.username == user_in.username))
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail="Usuario ya existe")

        user = User(
            username=user_in.username,
            hashed_password=get_password_hash(user_in.password),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e

@router.post("/login", response_model=Token)
async def login(user_in: UserCreate, db: AsyncSession = Depends(get_session)):
    """
    Authenticate a user and return a JWT token.

    Args:
        user_in (UserCreate): Login credentials.
        db (AsyncSession): Database session.

    Returns:
        Token: Access token.

    Raises:
        HTTPException: If credentials are invalid.
    """
    result = await db.execute(select(User).where(User.username == user_in.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )
    access_token = create_access_token({"sub": str(user.id)})
    return Token(access_token=access_token)
