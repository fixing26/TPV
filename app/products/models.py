

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db import Base



class Category(Base):

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False) # Removed unique constraint (unique per tenant)
    tenant_id = Column(String, nullable=False, index=True)

    products = relationship("Product", back_populates="category")


class Product(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    sku = Column(String, index=True, nullable=True) 

    price = Column(Float, nullable=False)
    tax = Column(Float, default=0.0)
    active = Column(Boolean, default=True)
    tenant_id = Column(String, nullable=False, index=True)
    
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="products")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
