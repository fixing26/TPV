
from sqlalchemy import Column, Integer, String
from ..db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="cashier")  # admin / cashier
    tenant_id = Column(String, nullable=False, index=True) # UUID for company isolation


