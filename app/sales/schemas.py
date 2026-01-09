
from pydantic import BaseModel
from typing import List

# --------- INPUT (lo que envías al crear venta) --------- #

class SaleLineCreate(BaseModel):
    product_id: int
    quantity: int


class SaleCreate(BaseModel):
    payment_method: str = "cash"
    lines: List[SaleLineCreate]


class SaleOpen(BaseModel):
    table_id: int | None = None
    name: str | None = None


class SaleUpdate(BaseModel):
    lines: List[SaleLineCreate] = []
    payment_method: str | None = None
    status: str | None = None



# --------- OUTPUT (lo que responde la API) --------- #

from ..products.schemas import ProductOut

class SaleLineOut(BaseModel):
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
