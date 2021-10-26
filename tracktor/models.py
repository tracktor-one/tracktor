"""
Module for all models
"""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel  # pylint: disable=no-name-in-module
from werkzeug.security import generate_password_hash

from tracktor import sql
from tracktor.error import ItemConflictException


class UserCreate(BaseModel):  # pylint: disable=too-few-public-methods
    """
    Incoming model to create a user
    """
    name: str
    password: str


class UserUpdate(BaseModel):  # pylint: disable=too-few-public-methods
    """
    Incoming model to update a user
    """
    name: str
    admin: bool


class UserResponse(BaseModel):  # pylint: disable=too-few-public-methods
    """
    Cleaned user model suitable for a response
    """
    entity_id: str
    name: str
    created_at: datetime
    last_login: Optional[datetime]
    admin: bool


class User(UserResponse):
    """
    Full populated user model
    """
    id: int
    password: str

    async def update(self, name: Optional[str] = None, password: Optional[str] = None,
                     last_login: Optional[datetime] = None,
                     admin: Optional[bool] = None):
        """
        Updates the values of a user in the database
        """
        changed = False
        if name:
            check_user = await sql.database.fetch_one(
                sql.users.select().where(sql.users.c.name == name))
            if check_user and check_user.get("id") != self.id:
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
            query = sql.users.update().where(sql.users.c.id == self.id).values(**self.__dict__)
            await sql.database.execute(query)

    async def delete(self):
        """
        Removes a user from the database
        """
        await sql.database.execute(sql.users.delete().where(sql.users.c.id == self.id))

    @staticmethod
    async def create(name: str, password="", admin=False) -> Optional[UserResponse]:
        """
        Creates a new user, saves it to the database and returns a UserResponse model
        """
        user_uuid = str(uuid.uuid1())
        user = User(
            id=-1,
            entity_id=user_uuid,
            name=name,
            password=generate_password_hash(password) if password else None,
            created_at=datetime.utcnow(),
            last_login=None,
            admin=admin
        )
        query = sql.users.insert().values(
            entity_id=user.entity_id,
            name=user.name,
            password=user.password,
            created_at=user.created_at,
            last_login=user.last_login,
            admin=user.admin
        )
        created_id = await sql.database.execute(query)
        return UserResponse(**user.__dict__) if created_id else None


class VersionModel(BaseModel):  # pylint: disable=too-few-public-methods
    """
    Version response model
    """
    version: str
    changelog: str


class Token(BaseModel):  # pylint: disable=too-few-public-methods
    """
    Token response model
    """
    access_token: str
    token_type: str
