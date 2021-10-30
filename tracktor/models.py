"""
Module for all models
"""
import uuid
from datetime import datetime
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import SQLModel, Field
from werkzeug.security import generate_password_hash

from tracktor.error import ItemConflictException


class UserCreate(SQLModel):  # pylint: disable=too-few-public-methods
    """
    Incoming model to create a user
    """
    name: str
    password: str


class UserUpdate(SQLModel):  # pylint: disable=too-few-public-methods
    """
    Incoming model to update a user
    """
    name: str
    admin: bool


class UserResponse(SQLModel):  # pylint: disable=too-few-public-methods
    """
    Cleaned user model suitable for a response
    """
    entity_id: str
    name: str
    created_at: datetime
    last_login: Optional[datetime]
    admin: bool


class User(UserResponse, table=True):
    """
    Full populated user model
    """
    id: int = Field(default=None, primary_key=True)
    entity_id: str = Field(default=str(uuid.uuid1()), nullable=False)
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    password: str

    async def update(self, session: AsyncSession,   # pylint: disable=too-many-arguments
                     name: Optional[str] = None, password: Optional[str] = None,
                     last_login: Optional[datetime] = None,
                     admin: Optional[bool] = None):
        """
        Updates the values of a user in the database
        """
        changed = False
        if name:
            check_user: User = (await session.execute(select(User).where(User.name == name)))\
                .scalars().first()
            if check_user and check_user.id != self.id:
                raise ItemConflictException(message="Invalid username")
            self.name = name
            changed = True
        if password:
            self.password = generate_password_hash(password)
            changed = True
        if last_login:
            self.last_login = last_login
            changed = True
        if admin is not None:
            self.admin = admin
            changed = True

        if changed:
            session.add(self)
            await session.commit()
            await session.refresh(self)

        return self

    async def delete(self, session: AsyncSession):
        """
        Removes a user from the database
        """
        await session.delete(self)
        await session.commit()

    @staticmethod
    async def create(session: AsyncSession,
                     name: str, password="", admin=False) -> Optional[UserResponse]:
        """
        Creates a new user, saves it to the database and returns a UserResponse model
        """
        user = User(
            name=name,
            password=generate_password_hash(password) if password else None,
            admin=admin
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return UserResponse(**user.__dict__)


class CategoryResponse(SQLModel):  # pylint: disable=too-few-public-methods
    """
    Cleaned category model suitable for a response
    """
    name: str
    playlists: List[str]


class Category(CategoryResponse, table=True):
    """
    Full populated category model
    """
    id: int = Field(default=None, primary_key=True)


class VersionModel(SQLModel):  # pylint: disable=too-few-public-methods
    """
    Version response model
    """
    version: str
    changelog: str


class Token(SQLModel):  # pylint: disable=too-few-public-methods
    """
    Token response model
    """
    access_token: str
    token_type: str
