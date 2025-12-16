"""
Product schemas module.

Defines Pydantic models for product validation.
"""

from pydantic import BaseModel



class CategoryBase(BaseModel):
    """Base schema for Category data."""
    name: str


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""
    pass

class CategoryUpdate(BaseModel):
    """Schema for updating a category."""
    name: str

class CategoryOut(CategoryBase):
    """Schema for category response."""
    id: int

    class Config:
        from_attributes = True



class ProductBase(BaseModel):
    """Base schema for Product data."""
    name: str
    price: float
    tax: float = 0.0
    active: bool = True
    category_id: int | None = None
    sku: str | None = None


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    category_id: int 


class ProductUpdate(BaseModel):
    """Schema for updating an existing product (partial update)."""
    name: str | None = None
    price: float | None = None
    tax: float | None = None
    active: bool | None = None
    category_id: int | None = None
    sku: str | None = None


class ProductOut(ProductBase):
    """Schema for product response."""
    id: int
    category: CategoryOut | None = None

    class Config:
        from_attributes = True  # Pydantic v2 (equiv. orm_mode=True)
