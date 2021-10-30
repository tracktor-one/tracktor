"""
Module that contains all configuration options
"""
import os

from fastapi.security import OAuth2PasswordBearer

from tracktor.error import DatabaseConstructionError

basedir = os.path.abspath(os.path.dirname(__file__))
supported_dbs = {
    "sqlite": "aiosqlite",
    "mysql": "asyncmy",
    "postgresql": "asyncpg",
}


def _get_database_uri():
    db_type = os.environ.get("DATABASE_TYPE", default="sqlite").lower()
    if db_type not in supported_dbs.keys():
        raise DatabaseConstructionError("Unsupported database detected")
    if db_type == "sqlite":
        db_path = "/" + os.environ.get(
            "DATABASE_PATH", default=os.path.join(basedir, "../tracktor.db")
        )
    else:
        user = os.environ.get("DATABASE_USER")
        password = os.environ.get("DATABASE_PASS")
        host = os.environ.get("DATABASE_HOST")
        name = os.environ.get("DATABASE_NAME")
        if not user or not password or not host or not name:
            raise DatabaseConstructionError("One or more Database variables missing")
        db_path = f"{user}:{password}@{host}:{'3306' if db_type == 'mysql' else '5432'}/{name}"

    return f"{db_type}+{supported_dbs[db_type]}" + f"://{db_path}"


class Config:  # pylint: disable=too-few-public-methods
    """
    Config object for tracktor
    """

    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        default="565e1e6d786028a24fb1ff06cbae8f13bc96fdcdeff63fd90321d90ca2839fd7",
    )
    ALGORITHM = "HS256"
    SQLALCHEMY_DATABASE_URI = _get_database_uri()
    SQL_DEBUG = bool(os.environ.get("SQL_DEBUG"))
    ADMIN_USER = os.environ.get("ADMIN_USER", default="admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", default="password")
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="login")
    CORS_DOMAIN = os.environ.get("CORS_DOMAIN", default=None)


config = Config()
