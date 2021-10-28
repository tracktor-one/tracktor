"""
Module for startup and shutdown functions
"""
from tracktor.config import config
from tracktor.models import User
from tracktor.sql import users, database


async def app_startup():
    """
    Connect from the database and create admin user if not present
    """
    await database.connect()
    all_users = await database.fetch_all(users.select())
    if not all_users:
        await User.create(name=config.ADMIN_USER,
                          password=config.ADMIN_PASSWORD,
                          admin=True)


async def app_shutdown():
    """
    Disconnect from the database
    """
    await database.disconnect()
