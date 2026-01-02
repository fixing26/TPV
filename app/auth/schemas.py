"""
Authentication schemas module.

Defines Pydantic models for request and response validation in authentication endpoints.
"""

from pydantic import BaseModel

class UserBase(BaseModel):
    """Base schema for User data."""
    username: str

class UserCreate(UserBase):
    """Schema for user creation (registration)."""
    password: str
    role: str = "cashier"

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    tenant_id: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"
    role: str
    tenant_id: str | None = None
