"""
Module for database connections
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from tracktor.config import config

engine = create_async_engine(
    config.SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False},
    echo=config.SQL_DEBUG,
    future=True
)


async def get_session() -> AsyncSession:
    """
    Return a AsyncSession suitable for Depends()
    """
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
