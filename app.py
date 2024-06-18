import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data.config import load_config
from filters.admin import AdminFilter
from handlers.admin import register_admin
from handlers.echo import register_echo
from handlers.user import register_user
from middlewares.environment import EnvironmentMiddleware
from middlewares.tech import TechMiddleware
from loader import bot, config, dp
from utils.database import db, create_db
logger = logging.getLogger(__name__)


def register_all_middlewares(dp, config):
    if config.tg_bot.tech_work:
        dp.setup_middleware(TechMiddleware())
    dp.setup_middleware(EnvironmentMiddleware(config=config))


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):
    register_admin(dp)
    register_user(dp)

   # register_echo(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")

    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)
    await create_db()
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
