from aiogram.dispatcher.filters.state import StatesGroup, State


class Nft(StatesGroup):
    InputNum = State()
    EnterSum = State()