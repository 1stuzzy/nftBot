from sqlalchemy import (Column, Integer, String, DateTime, BigInteger, ForeignKey, Boolean, Float, Text, Constraint,
                        ARRAY, Sequence, TIMESTAMP)
from utils.database import db
from datetime import datetime


class WorkPayments(db.Model):
    __tablename__ = 'workPayments'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    worker_id = Column(BigInteger)
    user_id = Column(BigInteger, default=0)
    profits = Column(Integer, default=1)
    sum = Column(Integer, default=0)
    date = Column(TIMESTAMP, default=datetime.now())
    name = Column(String)


class Bot(db.Model):
    __tablename__ = 'bots'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    qiwi_key = Column(String(500))
    proxy = Column(String(), default="")
    trade_bot = Column(Integer, default=1)
    casino_bot = Column(Integer, default=0)
    card_number = Column(BigInteger, default=0)
    sum_profit = Column(Integer, default=0)
    count_profit = Column(Integer, default=0)
    status = Column(String(200), default="🌕 FULL-WORK")
    top_worker = Column(String(300), default="-")
    top_worker_sum = Column(Integer, default=0)
    bill_id = Column(Integer, default=0)


class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    user_id = Column(BigInteger)

    is_teacher = Column(Integer, default=0)
    personal_teacher = Column(BigInteger, default=0)
    profits_left = Column(Integer, default=0)

    registration = Column(Integer, default=0)
    trade_profit = Column(Integer, default=0)
    nft_profit = Column(Integer, default=0)
    username = Column(String)
    ban = Column(Integer, default=0)
    profits = Column(Integer, default=0)
    min_dep = Column(Integer, default=1000)

    trade_notification = Column(Integer, default=1)
    casino_notification = Column(Integer, default=1)
    nft_notification = Column(Integer, default=1)

    casino_profit = Column(Integer, default=0)
    all_profit = Column(Integer, default=0)
    referral = Column(BigInteger)
    date = Column(TIMESTAMP, default=datetime.now())



class NftUser(db.Model):
    __tablename__ = "nftusers"
    id = Column(BigInteger, autoincrement=True, primary_key=True, unique=True)
    user_id = Column(BigInteger, unique=True)
    username = Column(String)
    balance = Column(Float, default=0)
    fake_balance = Column(Float, default=0.0)
    worker_id = Column(BigInteger)
    full_name = Column(String)
    notification = Column(Integer, default=1)
    ban = Column(Integer, default=0)
    ban_withdraw = Column(Integer, default=0)
    count_withdraw = Column(Integer, default=0)
    wallet = Column(String, default="не привязан")
    withdraw_balance = Column(Float, default=0)
    file_id = Column(String)
    verification = Column(Boolean, default=False)
    user_collections = Column(ARRAY(BigInteger), default=[])
    user_collection_in_market = Column(ARRAY(BigInteger), default=[])
    user_favourite = Column(ARRAY(BigInteger), default=[])


class Collection(db.Model):
    __tablename__ = "collections"
    id = Column(BigInteger, autoincrement=True, primary_key=True, unique=True)
    name_collection = Column(String)


class Nft(db.Model):
    __tablename__ = "nfts"
    id = Column(BigInteger, autoincrement=True, primary_key=True, unique=True)
    name = Column(String)
    img = Column(String)
    collection_name = Column(String)
    price = Column(Float)
    history_price = Column(ARRAY(Float))
    description = Column(String)
    blockchain = Column(String)
    favourite_count = Column(BigInteger)
