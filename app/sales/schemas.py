"""
Sales schemas module.

Defines Pydantic models for sales validation.
"""
from pydantic import BaseModel
from typing import List

# --------- INPUT (lo que envías al crear venta) --------- #

class SaleLineCreate(BaseModel):
    """Schema for creating a sale line."""
    product_id: int
    quantity: int


class SaleCreate(BaseModel):
    """Schema for creating a new sale."""
    payment_method: str = "cash"
    lines: List[SaleLineCreate]


# --------- OUTPUT (lo que responde la API) --------- #

class SaleLineOut(BaseModel):
    """Schema for sale line response."""
    id: int
    product_id: int
    quantity: int
    price_unit: float
    line_total: float

    class Config:
        from_attributes = True


class SaleOut(BaseModel):
    """Schema for sale response."""
    id: int
    total: float
    payment_method: str
    created_at: float
    lines: List[SaleLineOut]

    class Config:
        from_attributes = True
