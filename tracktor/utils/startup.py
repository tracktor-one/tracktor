from tracktor import database, config
from tracktor.models import User
from tracktor.sql import users


async def app_startup():
    await database.connect()
    all_users = await database.fetch_all(users.select())
    if not all_users:
        await User.create(name=config.ADMIN_USER,
                          password=config.ADMIN_PASSWORD,
                          admin=True)


async def app_shutdown():
    await database.disconnect()
