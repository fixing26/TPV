"""
Sales models module.

Defines the database models for sales (tickets) and sale lines.
"""

from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from ..db import Base


class Sale(Base):
    """
    Sale (Ticket) database model.

    Attributes:
        id (int): Primary key.
        total (float): Total amount of the sale.
        payment_method (str): Payment method (e.g., 'cash', 'card').
        created_at (float): Timestamp when the sale was created.
        user_id (int): ID of the user who made the sale (optional).
        lines (List[SaleLine]): List of sale lines associated with this sale.
    """
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    total = Column(Float, nullable=False)
    payment_method = Column(String, default="cash")  # cash / card / etc.
    created_at = Column(Float, default=lambda: datetime.now().timestamp())

    # Opcional: relacionar con usuario si usas auth más adelante
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    lines = relationship(
        "SaleLine",
        back_populates="sale",
        cascade="all, delete-orphan",
    )


class SaleLine(Base):
    """
    Sale Line database model.

    Represents a single product line within a sale.

    Attributes:
        id (int): Primary key.
        sale_id (int): ID of the parent sale.
        product_id (int): ID of the product sold.
        quantity (int): Quantity of the product.
        price_unit (float): Unit price at the time of sale.
        line_total (float): Total price for this line (quantity * price_unit).
    """
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
