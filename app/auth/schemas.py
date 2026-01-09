"""
Authentication schemas module.

Defines Pydantic models for request and response validation in authentication endpoints.
"""

from pydantic import BaseModel, field_validator

class UserBase(BaseModel):
    """Base schema for User data."""
    username: str

class UserCreate(UserBase):
    """Schema for user creation (registration)."""
    password: str
    role: str = "cashier"

    @field_validator('username')
    @classmethod
    def validate_email(cls, v: str) -> str:
        # Simple email regex
        import re
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, v):
            raise ValueError('El nombre de usuario debe ser un email válido')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        import re
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r"[A-Z]", v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not re.search(r"\d", v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not re.search(r"[!@#$%^&*]", v):
            raise ValueError('La contraseña debe contener al menos un carácter especial (!@#$%^&*)')
        return v

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
