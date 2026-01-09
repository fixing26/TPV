

from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from ..db import Base


class Sale(Base):

    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    total = Column(Float, nullable=False, default=0.0)
    payment_method = Column(String, default="cash")  # cash / card / etc.
    status = Column(String, default="CLOSED", index=True) # OPEN, CLOSED, CANCELLED
    created_at = Column(Float, default=lambda: datetime.now().timestamp())

    # Opcional: relacionar con usuario si usas auth más adelante
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    closed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=True)
    name = Column(String, nullable=True)
    tenant_id = Column(String, nullable=False, index=True)

    lines = relationship(
        "SaleLine",
        back_populates="sale",
        cascade="all, delete-orphan",
    )
    
    table = relationship("app.tables.models.Table")
    creator = relationship("app.auth.models.User", foreign_keys=[user_id])
    closer = relationship("app.auth.models.User", foreign_keys=[closed_by_id])


class SaleLine(Base):

    __tablename__ = "sale_lines"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    quantity = Column(Integer, nullable=False)
    price_unit = Column(Float, nullable=False)
    line_total = Column(Float, nullable=False)

    sale = relationship("Sale", back_populates="lines")
    # relación simple para poder obtener info del producto si luego la necesitas
    product = relationship("Product")
