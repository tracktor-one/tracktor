import databases
import sqlalchemy
from fastapi import FastAPI
from passlib.context import CryptContext

from config import Config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

config = Config()
database = databases.Database(config.SQLALCHEMY_DATABASE_URI)
engine = sqlalchemy.create_engine(
    config.SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}
)
metadata = sqlalchemy.MetaData()
import tracktor.sql

metadata.create_all(engine)

from .routers import *
from .utils.startup import app_startup, app_shutdown

app = FastAPI()
app.include_router(admin_router)
app.include_router(auth_router)
app.include_router(version_router)


@app.on_event("startup")
async def startup():
    await app_startup()


@app.on_event("shutdown")
async def shutdown():
    await app_shutdown()
