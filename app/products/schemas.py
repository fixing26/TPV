"""
Product schemas module.

Defines Pydantic models for product validation.
"""

from pydantic import BaseModel


class ProductBase(BaseModel):
    """Base schema for Product data."""
    name: str
    price: float
    tax: float = 0.0
    active: bool = True


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating an existing product (partial update)."""
    name: str | None = None
    price: float | None = None
    tax: float | None = None
    active: bool | None = None


class ProductOut(ProductBase):
    """Schema for product response."""
    id: int

    class Config:
        from_attributes = True  # Pydantic v2 (equiv. orm_mode=True)
