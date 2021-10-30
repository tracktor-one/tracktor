"""
Module that contains authorisation functions
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from tracktor.config import config
from tracktor.error import UnauthorizedException, ForbiddenException
from tracktor.models import User
from tracktor.utils.database import get_session


async def get_user(username: str, session: AsyncSession) -> Optional[User]:
    """
    Returns a user with the given username
    """
    return (await session.execute(select(User).where(User.name == username))).scalars().first()


async def get_user_by_entity_id(entity_id: str, session: AsyncSession) -> Optional[User]:
    """
    Returns a user with the given entity_id
    """
    return (await session.execute(select(User).where(User.entity_id == entity_id)))\
        .scalars().first()


async def get_super_admin(session: AsyncSession):
    """
    Returns the admin user with id 1
    """
    return (await session.execute(select(User).where(User.id == 1))).scalars().first()


async def decode_token(token, session: AsyncSession):
    """
    Decodes a given JWT token to return the correct user
    """
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if user_id := payload.get("sub"):
            if user := await get_user_by_entity_id(user_id, session):
                return user
        raise UnauthorizedException(message="Could not validate credentials",
                                    headers={"WWW-Authenticate": "Bearer"})
    except JWTError as err:
        raise UnauthorizedException(message="Could not validate credentials",
                                    headers={"WWW-Authenticate": "Bearer"}) from err


async def current_user(token: str = Depends(config.OAUTH2_SCHEME),
                       session: AsyncSession = Depends(get_session)):
    """
    Returns the current user
    """
    return await decode_token(token, session)


def create_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Creates the JWT token used for authentication
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


async def admin_required(user: User = Depends(current_user)):
    """
    Check if user has admin privileges
    """
    if not user.admin:
        raise ForbiddenException(message="Operation not permitted")
