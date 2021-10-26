"""
Module that contains authorisation functions
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends
from jose import jwt, JWTError

from tracktor.config import config
from tracktor.error import UnauthorizedException, ForbiddenException
from tracktor.models import User
from tracktor.sql import users, database


async def get_user(username: str) -> Optional[User]:
    """
    Returns a user with the given username
    """
    if check_user := await database.fetch_one(users.select().where(users.c.name == username)):
        return User(**check_user)


async def get_user_by_entity_id(entity_id: str) -> Optional[User]:
    """
    Returns a user with the given entity_id
    """
    if check_user := await database.fetch_one(users.select().where(users.c.entity_id == entity_id)):
        return User(**check_user)


async def get_super_admin():
    """
    Returns the admin user with id 1
    """
    return User(**await database.fetch_one(users.select().where(users.c.id == 1)))


async def decode_token(token):
    """
    Decodes a given JWT token to return the correct user
    """
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if user_id := payload.get("sub"):
            if user := await get_user_by_entity_id(user_id):
                return user
        raise UnauthorizedException(message="Could not validate credentials",
                                    headers={"WWW-Authenticate": "Bearer"})
    except JWTError as err:
        raise UnauthorizedException(message="Could not validate credentials",
                                    headers={"WWW-Authenticate": "Bearer"}) from err


async def current_user(token: str = Depends(config.OAUTH2_SCHEME)):
    """
    Returns the current user
    """
    return await decode_token(token)


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
