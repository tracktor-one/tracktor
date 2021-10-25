import databases
import sqlalchemy
from fastapi import FastAPI

from config import Config

config = Config()

database = databases.Database(config.SQLALCHEMY_DATABASE_URI)

engine = sqlalchemy.create_engine(
    config.SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}
)
from .models import metadata, users, UserModel

metadata.create_all(engine)

app = FastAPI()
from .api import *


@app.on_event("startup")
async def startup():
    await database.connect()
    all_users = await database.fetch_all(users.select())
    if not all_users:
        await UserModel.create(name=config.ADMIN_USER,
                               password=config.ADMIN_PASSWORD,
                               admin=True)


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
