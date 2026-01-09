

from pydantic import BaseModel



class CategoryBase(BaseModel):

    name: str


class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):

    name: str

class CategoryOut(CategoryBase):
    id: int

    class Config:
        from_attributes = True



class ProductBase(BaseModel): 
    name: str
    price: float
    tax: float = 0.0
    active: bool = True
    category_id: int | None = None
    sku: str | None = None


class ProductCreate(ProductBase):
  
    category_id: int 


class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    tax: float | None = None
    active: bool | None = None
    category_id: int | None = None
    sku: str | None = None


class ProductOut(ProductBase):

    id: int
    category: CategoryOut | None = None

    class Config:
        from_attributes = True  
