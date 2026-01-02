"""
Tables models module.
"""

from sqlalchemy import Column, Integer, String, Boolean
from ..db import Base

class Table(Base):
    """
    Table database model.
    """
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False) # Removed unique constraint (unique per tenant)
    tenant_id = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
