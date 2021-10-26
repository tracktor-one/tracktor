import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from werkzeug.security import generate_password_hash

from tracktor import database
from tracktor.error import ItemConflictException
from tracktor.sql import users


class UserCreate(BaseModel):
    name: str
    password: str


class UserUpdate(BaseModel):
    name: str
    admin: bool


class UserResponse(BaseModel):
    entity_id: str
    name: str
    created_at: datetime
    last_login: Optional[datetime]
    admin: bool


class User(UserResponse):
    id: int
    password: str

    async def update(self, name: Optional[str] = None, password: Optional[str] = None,
                     last_login: Optional[datetime] = None,
                     admin: Optional[bool] = None):
        changed = False
        if name:
            check_user = await database.fetch_one(users.select().where(users.c.name == name))
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
            query = users.update().where(users.c.id == self.id).values(**self.__dict__)
            await database.execute(query)

    async def delete(self):
        await database.execute(users.delete().where(users.c.id == self.id))

    @staticmethod
    async def create(name: str, password="", admin=False) -> Optional[UserResponse]:
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
        query = users.insert().values(
            entity_id=user.entity_id,
            name=user.name,
            password=user.password,
            created_at=user.created_at,
            last_login=user.last_login,
            admin=user.admin
        )
        created_id = await database.execute(query)
        return UserResponse(**user.__dict__) if created_id else None


class VersionModel(BaseModel):
    version: str
    changelog: str


class Token(BaseModel):
    access_token: str
    token_type: str
