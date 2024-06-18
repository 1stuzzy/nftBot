import math

from aiogram.types import KeyboardButton, InlineKeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
import utils.db_commands as db
from loader import config

withdraw = CallbackData("withdraw", "type")
check_payment = CallbackData("payment", "bill_id")
make_payment = CallbackData("make", "action", "user_id", "sum")
put_nft = CallbackData("put_nft", "user_id", "nft_id", "sum")

take_payment = CallbackData("take", "action", "user_id", "status", "sum")
outdraw = CallbackData("outdraw", "type")

link_wallet = CallbackData("link_wallet", "name")

collection_markup = CallbackData("collection_markup", "name")
nft_markup = CallbackData("nft_markup", "name")

page = CallbackData("page", "name", "action")
my_nft = CallbackData("my_nft", "id", "action")


async def info_markup():
    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton("📝 Верификация", callback_data="verification"))
    markup.add(InlineKeyboardButton(text="📄 Соглашение", url=config.links.rules),
               InlineKeyboardButton(text="👨‍💻 Поддержка", url=config.links.support))
    return markup


async def support_markup():
    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton(text="👨‍💻 Поддержка", url=config.links.support))
    return markup


async def profile_markup():
    markup = InlineKeyboardMarkup()

    markup.add(InlineKeyboardButton(text="📥 Пополнить", callback_data="top_up"),
               InlineKeyboardButton(text="📤 Вывести", callback_data="withdrawMarkup"))
    markup.add(InlineKeyboardButton(text="🌌 Мои NFT", callback_data="my_nft"))
    markup.add(InlineKeyboardButton(text="❤️Избранное", callback_data="favourite"))
    markup.add(InlineKeyboardButton(text="📝 Привязать кошелек", callback_data="link"))

    return markup


async def top_up_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton('💷 Пополнить с помощью QIWI-кошелька', callback_data=withdraw.new("qiwi")))
    # markup.add(InlineKeyboardButton('💳 Пополнить через банковскую карту', callback_data=withdraw.new("bank")))
    markup.add(InlineKeyboardButton('💳 Пополнить через банковскую карту', callback_data=withdraw.new("p2p")))

    return markup


async def bank_check():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton('Проверить платеж ', callback_data=check_payment.new(1)))
    markup.add(InlineKeyboardButton('Тех. поддержка', url=config.links.support))
    markup.add(InlineKeyboardButton('Отменить пополнение', callback_data="menu"))
    return markup


async def qiwi_check(link, id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton('Перейти к оплате', url=link))
    markup.add(InlineKeyboardButton('Проверить платеж ', callback_data=check_payment.new(id)))
    markup.add(InlineKeyboardButton('Отменить пополнение', callback_data="menu"))
    return markup


async def put_nft_markup(_id, _nft_id, _sum):
    print(f"{_id} - {_nft_id} - {_sum}")
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton('💰Купить', callback_data=put_nft.new(_id, _nft_id, _sum)))
    return markup


async def get_money(_sum, _id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton('💰Оплатить', callback_data=make_payment.new("nft", _id, _sum)))
    return markup


async def take_money_markup(_id, _sum):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton('Вывести', callback_data=take_payment.new("nft", _id, 1, _sum)),
               InlineKeyboardButton('Отменить', callback_data=take_payment.new("nft", _id, 0, _sum)))
    return markup


async def support_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton('Обратиться в поддержку', url="https://t.me/Blockparty_Support"))


async def outdraw_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton('💳 Вывести на банковскую карту', callback_data=outdraw.new(1)))
    markup.add(InlineKeyboardButton('💰 Вывести на QIWI-кошелек', callback_data=outdraw.new(0)))
    return markup


async def link_markup():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("🛡 Metamask", callback_data=link_wallet.new("Metamask")),
               InlineKeyboardButton("🛡 Fantom", callback_data=link_wallet.new("Fantom")))
    markup.add(InlineKeyboardButton("🛡 Coinbase", callback_data=link_wallet.new("Coinbase")),
               InlineKeyboardButton("🛡 TrustWallet", callback_data=link_wallet.new("TrustWallet")))
    markup.add(InlineKeyboardButton("↩️Вернуться", callback_data="menu"))
    return markup


async def go_back_markup():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("↩️Вернуться", callback_data="menu"))
    return markup


async def get_list_of_collection_markup(page=0):
    collections = await db.get_all_collections()
    markup = InlineKeyboardMarkup(row_width=3)

    started_index_point = (page * 8) - 1
    count_in_the_page = 8
    count_items = 0

    count_collections = await db.count_collections()
    page_count = math.ceil(count_collections / count_in_the_page)
    for i in range(started_index_point, count_collections):
        if count_items >= count_in_the_page:
            break

        count_items += 1

        markup.add(InlineKeyboardButton(collections[i].name_collection,
                                        callback_data=collection_markup.new(collections[i].name_collection)))

    markup.add(InlineKeyboardButton("⬅", callback_data=f"next_{page-1}"),
               InlineKeyboardButton(f"{page+1}/{page_count}", callback_data="page_info"),
               InlineKeyboardButton("➡", callback_data=f"next_{page+1}"))
    markup.add(InlineKeyboardButton("🔍 Найти NFT по заданной цене", callback_data="by_price"))
    return markup


async def get_all_nfts_by_collection_name(name=None, nfts=None):
    markup = InlineKeyboardMarkup(row_width=3)

    if not nfts:
        nfts = await db.get_nft_by_collection_name(name)

    for nft in nfts:
        markup.insert(InlineKeyboardButton(nft.name, callback_data=nft_markup.new(nft.name)))

    markup.add(InlineKeyboardButton("↩️Вернуться", callback_data="go_collection"))
    return markup


async def get_one_nft(name):
    markup = InlineKeyboardMarkup(row_width=3)

    markup.insert(InlineKeyboardButton("↩️Вернуться", callback_data=nft_markup.new(name)))

    return markup


async def nft_page_markup(nft, user):
    markup = InlineKeyboardMarkup(row_width=1)
    is_like = 1
    if nft.id in user.user_favourite:
        is_like = 0
    heart_type = ["❤", "🤍"]
    markup.add(InlineKeyboardButton("✅ Купить", callback_data=page.new(nft.name, "buy")))
    markup.add(InlineKeyboardButton("📊 Колебание цен", callback_data=page.new(nft.name, "price_change")))
    markup.add(InlineKeyboardButton(f"{heart_type[is_like]} ({nft.favourite_count})",
                                    callback_data=page.new(nft.name, "like")))
    markup.add(InlineKeyboardButton("↩️Вернуться", callback_data=f"go_nft_{nft.collection_name}"))

    return markup


async def go_back_to_collection_markup():
    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(InlineKeyboardButton("↩️Вернуться", callback_data="go_collection"))
    return markup


async def get_list_of_favorites(ids_nft):
    markup = InlineKeyboardMarkup(row_width=1)

    for nft_id in ids_nft:
        nft = await db.get_nft_by_id(nft_id)
        markup.add(InlineKeyboardButton(nft.name, callback_data=nft_markup.new(nft.name)))

    markup.add(InlineKeyboardButton("↩️Вернуться", callback_data="go_menu"))
    return markup


async def get_list_of_my_nft(user):
    items = user.user_collections

    icons_list = ["🔹", "◾"]
    markup = InlineKeyboardMarkup(row_width=1)
    for item in items:
        nft = await db.get_nft_by_id(item)
        markup.add(InlineKeyboardButton(f"{icons_list[item in user.user_collection_in_market]} | {nft.name}",
                                        callback_data=my_nft.new(item, "get")))

    markup.add(InlineKeyboardButton("↩️Вернуться", callback_data="go_menu"))

    return markup


async def control_my_nft(user, nft):
    markup = InlineKeyboardMarkup(row_width=1)

    if nft.id in user.user_collection_in_market:
        markup.add(InlineKeyboardButton("Отменить продажу", callback_data=my_nft.new(nft.id, "take")))
    else:
        markup.add(InlineKeyboardButton("Выставить на продажу", callback_data=my_nft.new(nft.id, "put")))

    markup.add(InlineKeyboardButton("↩️Вернуться", callback_data="go_menu"))
    return markup


async def back_to_nft_markup(_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton("↩️Вернуться", callback_data=my_nft.new(_id, "get")))
    return markup
