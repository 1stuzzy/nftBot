from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware


class TechMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def on_process_message(self, message: types.Message, _):
        if message.from_user.id != 947353888:
            await message.answer("Technical works are ongoing. The service will be unavailable for some time.")
            raise CancelHandler()
