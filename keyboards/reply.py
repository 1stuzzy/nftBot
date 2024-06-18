from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import utils.db_commands as db


async def start_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Личный кабинет 📁"))
    markup.add(KeyboardButton("NFT 🎆"))
    markup.add(KeyboardButton("Тех.Поддержка 🌐"),
               KeyboardButton("Информация ℹ"))
    return markup
