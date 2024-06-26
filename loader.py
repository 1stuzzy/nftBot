from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data.config import load_config


config = load_config(".env")
storage = MemoryStorage()
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
control_bot = Bot(token=config.tg_bot.control_token, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)

bot['config'] = config
