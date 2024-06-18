from gino import Gino
from loader import bot
db = Gino()


async def create_db():
    await db.set_bind(bot['config'].db.postgres_uri)

    command = input("Delete all DB (y/n):")
    if command == "y":
        await db.gino.drop_all()
    await db.gino.create_all()
