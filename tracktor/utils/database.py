"""
Module for database connections
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine, Session

from tracktor.config import config

engine = create_async_engine(
    config.SQLALCHEMY_DATABASE_URI, echo=config.SQL_DEBUG, future=True
)


async def get_session() -> AsyncSession:
    """
    Return a AsyncSession suitable for `Depends()`
    """
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


def get_sync_session():
    """
    Return a sync session suitable for database calls
    where a `Depends()` is not possible
    """
    sync_engine = create_engine(
        config.SQLALCHEMY_DATABASE_URI.replace("+aiosqlite", "")
        .replace("+asyncmy", "")
        .replace("+asyncpg", ""),
        echo=config.SQL_DEBUG,
    )
    with Session(sync_engine) as session:
        yield session
