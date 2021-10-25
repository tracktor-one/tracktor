import uuid
from datetime import datetime
from typing import Optional

import sqlalchemy
from pydantic import BaseModel
from werkzeug.security import generate_password_hash

from tracktor import database
from tracktor.error.error import ItemConflict

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("entity_id", sqlalchemy.String(50), unique=True),
    sqlalchemy.Column("name", sqlalchemy.String(50), unique=True),
    sqlalchemy.Column("password", sqlalchemy.String(80)),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, default=datetime.utcnow()),
    sqlalchemy.Column("last_login", sqlalchemy.DateTime, default=None),
    sqlalchemy.Column("admin", sqlalchemy.Boolean(), default=False)
)


class UserModel(BaseModel):
    id: int
    entity_id: str
    name: str
    password: str
    created_at: datetime
    last_login: Optional[datetime]
    admin: bool

    def update(self, name: Optional[str] = None, password: Optional[str] = None, last_login: Optional[datetime] = None,
               admin: Optional[bool] = None):
        changed = False
        if name:
            check_user = database.fetch_one(users.select().where(users.c.name == name))
            if check_user and check_user.get("id") != self.id:
                raise ItemConflict(message="Invalid username")
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
            query = users.update().where(users.c.id == self.id).values(
                name=self.name,
                password=self.password,
                created_at=self.created_at,
                last_login=self.last_login,
                admin=self.admin
            )
            database.execute(query)

    @staticmethod
    async def create(name: str, password="", admin=False):
        user_uuid = str(uuid.uuid1())
        user = UserModel(
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
        user.id = created_id
        return user


class VersionModel(BaseModel):
    version: str
    changelog: str
