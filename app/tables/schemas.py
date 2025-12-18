"""
Tables schemas module.
"""
from pydantic import BaseModel

class TableBase(BaseModel):
    name: str
    description: str | None = None

class TableCreate(TableBase):
    pass

class TableUpdate(TableBase):
    pass

class TableOut(TableBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
