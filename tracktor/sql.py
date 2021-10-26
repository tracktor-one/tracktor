from datetime import datetime

import sqlalchemy

from tracktor import metadata

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
