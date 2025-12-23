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
    """Schema for creating a new sale (immediate close)."""
    payment_method: str = "cash"
    lines: List[SaleLineCreate]


class SaleOpen(BaseModel):
    """Schema for opening a new account/table."""
    table_id: int | None = None
    name: str | None = None


class SaleUpdate(BaseModel):
    """Schema for adding items or updating a sale."""
    lines: List[SaleLineCreate] = []
    payment_method: str | None = None
    status: str | None = None



# --------- OUTPUT (lo que responde la API) --------- #

from ..products.schemas import ProductOut

class SaleLineOut(BaseModel):
    """Schema for sale line response."""
    id: int
    product_id: int
    quantity: int
    price_unit: float
    line_total: float
    product: ProductOut | None = None

    class Config:
        from_attributes = True


from ..auth.schemas import UserOut

class SaleOut(BaseModel):
    """Schema for sale response."""
    id: int
    total: float
    payment_method: str
    status: str
    created_at: float
    table_id: int | None = None
    name: str | None = None
    lines: List[SaleLineOut]
    creator: UserOut | None = None
    closer: UserOut | None = None

    class Config:
        from_attributes = True
