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

from uuid import uuid4

# ...

@router.post("/register", response_model=UserOut)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_session)):
    """
    Register a new user (Creates a NEW TENANT).
    """
    try:
        result = await db.execute(select(User).where(User.username == user_in.username))
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail="Usuario ya existe")

        new_tenant_id = str(uuid4()) # Generate new UUID for the company

        user = User(
            username=user_in.username,
            hashed_password=get_password_hash(user_in.password),
            role="admin", # First user is always admin
            tenant_id=new_tenant_id
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
    """
    result = await db.execute(select(User).where(User.username == user_in.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )
    access_token = create_access_token({"sub": str(user.id), "role": user.role, "tenant_id": user.tenant_id})
    return Token(access_token=access_token, role=user.role, tenant_id=user.tenant_id)

from .dependencies import get_current_user
# ...

@router.post("/create_user", response_model=UserOut)
async def create_user(
    user_in: UserCreate, 
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new user within the SAME TENANT (Internal use by Admin).
    """
    if current_user.role != "admin":
         raise HTTPException(status_code=403, detail="Solo administradores pueden crear usuarios")

    # Check existence
    result = await db.execute(select(User).where(User.username == user_in.username))
    if result.scalar_one_or_none():
         raise HTTPException(status_code=400, detail="Usuario ya existe")

    new_user = User(
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role, # Can be cashier or admin
        tenant_id=current_user.tenant_id # Inherit Tenant ID
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.get("/", response_model=list[UserOut])
async def get_users(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """List all users of the current tenant."""
    result = await db.execute(select(User).where(User.tenant_id == current_user.tenant_id))
    return result.scalars().all()

from sqlalchemy import update
from app.sales.models import Sale

# ... (existing imports)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_session)):
    """Delete a user."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Unlink user from sales (set user_id = NULL)
    await db.execute(update(Sale).where(Sale.user_id == user_id).values(user_id=None))
    
    await db.delete(user)
    await db.commit()
