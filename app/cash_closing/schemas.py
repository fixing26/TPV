
from pydantic import BaseModel

# --------- INPUT (lo que envías al crear cierre) --------- #

class CashClosingCreate(BaseModel):

    closing_type:str
    user_id: int
    date: float
    from_date: float
    to_date: float
    from_sales: int
    to_sales: int
    total_sales: int
    total_cash: float
    total_card: float
    total_total: float

# --------- OUTPUT (lo que responde la API) --------- #

class CashClosingOut(BaseModel):

    id: int
    closing_type: str
    user_id: int
    date: float
    from_date: float
    to_date: float
    from_sales: int
    to_sales: int
    total_sales: int
    total_cash: float
    total_card: float
    total_total: float

    class Config:
        from_attributes = True

