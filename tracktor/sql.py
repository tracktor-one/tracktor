"""
Module for all database operations and tables
"""
from datetime import datetime

import databases
import sqlalchemy

from tracktor.config import config

database = databases.Database(config.SQLALCHEMY_DATABASE_URI)
engine = sqlalchemy.create_engine(
    config.SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}
)
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

metadata.create_all(engine)
