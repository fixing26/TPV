"""
Product models module.

Defines the database model for products.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db import Base



class Category(Base):
    """
    Category database model.
    
    Attributes:
        id (int): Primary key.
        name (str): Category name.
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False) # Removed unique constraint (unique per tenant)
    tenant_id = Column(String, nullable=False, index=True)

    products = relationship("Product", back_populates="category")


class Product(Base):
    """
    Product database model.

    Attributes:
        id (int): Primary key.
        name (str): Product name.
        sku (str): Stock Keeping Unit.
        price (float): Final price.
        tax (float): Tax percentage (default 0.0).
        stock (int): Current stock.
        active (bool): Whether the product is active.
        category_id (int): Foreign key to Category.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    sku = Column(String, index=True, nullable=True) 
    # Wait, original code snippet in my memory:
    # 30:     id = Column(Integer, primary_key=True, index=True)
    # 31:     name = Column(String, nullable=False, index=True)
    # 32:     price = Column(Float, nullable=False)  # precio final (con impuestos, de momento)
    # 33:     tax = Column(Float, default=0.0)       # % de impuesto, por si luego lo usas
    # 34:     active = Column(Boolean, default=True)
    # 35: 
    # 36:     created_at = Column(DateTime(timezone=True), server_default=func.now())
    # 37:     updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # I should be careful not to reinvent fields that weren't there if not requested, but SKU was in the docstring.
    # The user request didn't explicitly ask for SKU implementation if it was missing, but "category".
    # I will stick to adding Category and linking it.
    

    price = Column(Float, nullable=False)
    tax = Column(Float, default=0.0)
    active = Column(Boolean, default=True)
    tenant_id = Column(String, nullable=False, index=True)
    
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="products")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
