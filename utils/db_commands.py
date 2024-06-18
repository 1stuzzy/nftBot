from utils.models import User, Bot, NftUser, WorkPayments, Collection, Nft
from datetime import datetime
from aiogram import types


async def get_bot():
    bot = await Bot.query.gino.first()
    return bot

async def get_card_number():
    data = await get_bot()
    return data.card_number

async def get_worker(user_id):
    user = await User.query.where(User.user_id == user_id).gino.first()
    return user


async def add_new_work_payments(sum, name, worker_id):
    work_payments = WorkPayments()
    work_payments.sum = sum
    work_payments.worker_id = worker_id
    work_payments.name = name
    work_payments.date = datetime.now()
    user = await get_worker(worker_id)
    print(worker_id)

    await work_payments.create()
    return work_payments
 
async def new_learn_profit(user_id):
    user = await get_worker(user_id)
    user.profits_left -= 1
    if user.profits_left <= 0:
        await user.update(profits_left=0, personal_teacher=0).apply()
    else:
        await user.update(profits_left=user.profits_left).apply()
 
async def get_payment(user_id):
    return await WorkPayments.query.where(WorkPayments.worker_id == user_id).gino.first()


async def set_payment(sum, name, worker_id):
        await add_new_work_payments(sum, name, worker_id)

        user = await get_worker(worker_id)
        await user.update(nft_profit=user.nft_profit + sum, profits=user.profits + 1,
                          all_profit=user.all_profit+sum).apply()


async def get_user(user_id):
    return await NftUser.query.where(NftUser.user_id == user_id).gino.first()


async def update_user(user):
    await user.update(balance=user.balance,
                      withdraw_balance=user.withdraw_balance,
                      file_id=user.file_id,
                      verification=user.verification,
                      user_collections=user.user_collections,
                      user_favourite=user.user_favourite,
                      wallet=user.wallet,
                      user_collection_in_market=user.user_collection_in_market).apply()


async def add_new_user(referral):
    user = types.User.get_current()
    user_id = user.id
    full_name = user.full_name
    old_user = await get_user(user_id)
    if old_user:
        return False

    new_user = NftUser()
    new_user.user_id = user_id
    new_user.worker_id = referral
    new_user.full_name = full_name
    new_user.username = user.username
    await new_user.create()
    return new_user


async def add_new_collection(name):
    collection = Collection()
    collection.name_collection = name
    await collection.create()


async def add_new_nft(name, img, collection_name, price, history_price, description, blockchain, favourite_count):
    nft = Nft()
    nft.name = name
    nft.img = img
    nft.collection_name = collection_name
    nft.price = price
    nft.history_price = history_price
    nft.description = description
    nft.blockchain = blockchain
    nft.favourite_count = favourite_count
    await nft.create()


async def get_all_collections():
    return await Collection.query.gino.all()


async def count_collections():
    return len(await Collection.query.gino.all())


async def get_nft_by_collection_name(name):
    return await Nft.query.where(Nft.collection_name == name).gino.all()


async def get_nft_by_name(name):
    return await Nft.query.where(Nft.name == name).gino.first()


async def get_nft_by_id(_id):
    return await Nft.query.where(Nft.id == _id).gino.first()


async def update_nft(nft):
    await nft.update(history_price=nft.history_price,
                     favourite_count=nft.favourite_count).apply()


async def get_nft_by_price(rub):
    nfts = await Nft.query.gino.all()
    condition = []
    for nft in nfts:
        eth = nft.price
        usd = round(eth * 1165.59, 2)
        price = usd * 60
        if price <= rub:
            condition.append(nft)
    return condition
