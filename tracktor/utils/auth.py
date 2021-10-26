from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends
from jose import jwt, JWTError

from tracktor import database, config
from tracktor.error import UnauthorizedException, ForbiddenException
from tracktor.models import User
from tracktor.sql import users


async def get_user(username: str) -> Optional[User]:
    if check_user := await database.fetch_one(users.select().where(users.c.name == username)):
        return User(**check_user)


async def get_user_by_entity_id(user_id: str) -> Optional[User]:
    if check_user := await database.fetch_one(users.select().where(users.c.entity_id == user_id)):
        return User(**check_user)


async def get_super_admin():
    return User(**await database.fetch_one(users.select().where(users.c.id == 1)))


async def decode_token(token):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if user_id := payload.get("sub"):
            if user := await get_user_by_entity_id(user_id):
                return user
        raise UnauthorizedException(message="Could not validate credentials",
                                    headers={"WWW-Authenticate": "Bearer"})
    except JWTError:
        raise UnauthorizedException(message="Could not validate credentials",
                                    headers={"WWW-Authenticate": "Bearer"})


async def current_user(token: str = Depends(config.OAUTH2_SCHEME)):
    user = await decode_token(token)
    if not user:
        raise UnauthorizedException
    return user


def create_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


class AdminRequired:
    def __call__(self, user: User = Depends(current_user)):
        if not user.admin:
            raise ForbiddenException(message="Operation not permitted")
