"""
Module that contains all configuration options
"""
import os

from fastapi.security import OAuth2PasswordBearer

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:  # pylint: disable=too-few-public-methods
    """
    Config object for tracktor
    """
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        default="565e1e6d786028a24fb1ff06cbae8f13bc96fdcdeff63fd90321d90ca2839fd7")
    ALGORITHM = "HS256"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        default="sqlite:///" + os.path.join(basedir, "../tracktor.db"))
    ADMIN_USER = os.environ.get("ADMIN_USER", default="admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", default="password")
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="login")
    CORS_DOMAIN = os.environ.get("CORS_DOMAIN", default=None)


config = Config()
