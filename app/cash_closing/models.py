
from sqlalchemy import Column, Integer, Float, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime

from ..db import Base

class CashClosing(Base):

    __tablename__ = "cash_closings"

    id = Column(Integer, primary_key=True, index=True)
    closing_type = Column(String(1), nullable=False)
    user_id = Column(Integer, nullable=True) # Making nullable for now as auth might not be strict
    tenant_id = Column(String, nullable=False, index=True)

    # Timestamps
    date = Column(Float, default=lambda: datetime.now().timestamp())
    
    # Range of dates covered
    from_date = Column(Float, nullable=True)
    to_date = Column(Float, nullable=True)

    # Range of sale IDs
    from_sales = Column(Integer, nullable=True)
    to_sales = Column(Integer, nullable=True)

    # Stats
    total_sales = Column(Integer, default=0) # Count of sales
    total_cash = Column(Float, default=0.0)
    total_card = Column(Float, default=0.0)
    total_total = Column(Float, default=0.0)