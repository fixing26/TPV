"""
Authentication models module.

Defines the database models related to user authentication and management.
"""

from sqlalchemy import Column, Integer, String
from ..db import Base

class User(Base):
    """
    User database model.

    Attributes:
        id (int): Primary key.
        username (str): Unique username.
        hashed_password (str): Bcrypt hashed password.
        role (str): User role (e.g., 'admin', 'cashier').
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="cashier")  # admin / cashier


