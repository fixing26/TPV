"""
Database configuration module.

This module handles the asynchronous database connection using SQLAlchemy.
It defines the engine, session factory, and a dependency for getting a database session.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

DATABASE_URL = settings.database_url

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_session() -> AsyncSession:
    """
    Dependency to get an asynchronous database session.

    Yields:
        AsyncSession: A SQLAlchemy asynchronous session.
    """
    async with SessionLocal() as session:
        yield session
