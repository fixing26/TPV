"""
Product models module.

Defines the database model for products.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func

from ..db import Base


class Product(Base):
    """
    Product database model.

    Attributes:
        id (int): Primary key.
        name (str): Product name.
        sku (str): Stock Keeping Unit (barcode/reference).
        price (float): Final price (including tax).
        tax (float): Tax percentage (default 0.0).
        stock (int): Current stock quantity.
        active (bool): Whether the product is active/visible.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)  # precio final (con impuestos, de momento)
    tax = Column(Float, default=0.0)       # % de impuesto, por si luego lo usas
    active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
