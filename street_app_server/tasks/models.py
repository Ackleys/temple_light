#!/usr/bin/env python3
# coding: utf8
# 20170825 anChaOs

import json, logging
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Integer, Float, DateTime, Date, Text, ForeignKey

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.ext.declarative import declarative_base

import setting

# try:
#     logging.info(u"初始化 sqlalchemy ...")
#     engine      = create_engine(setting.MYSQL_URI,pool_size=100, pool_recycle=3600, echo=False)
#     DBSession   = sessionmaker(bind=engine)
#     # db_session  = DBSession()
#     Base        = declarative_base()
# except Exception as e:
#     logging.exception(e)
#     logging.error(u"初始化 sqlalchemy 失败 ...")
#     sys.exit()

Base = declarative_base()

def reconnect_mysql():
    pass
    # try:
    #     global engine
    #     global db_session
    #     logging.info(u"重连 mysql sqlalchemy ...")
    #     db_session.close()
    #     engine      = create_engine(setting.MYSQL_URI, pool_size=512, max_overflow=0, pool_timeout=0, pool_recycle=5)
    #     DBSession   = sessionmaker(bind=engine)
    #     db_session  = DBSession()
    # except:
    #     logging.exception(e)
    #     logging.error("重连 mysql sqlalchemy 失败 ...")
    #     sys.exit()


def get_db_session():
    try:
        logging.info(u"初始化 sqlalchemy ...")
        engine      = create_engine(setting.MYSQL_URI,pool_size=100, pool_recycle=3600, echo=False)
        return Session(bind=engine)
    except Exception as e:
        logging.exception(e)
        logging.error(u"初始化 sqlalchemy 失败 ...")
        sys.exit()


class Pay(Base):
    __tablename__ = 'pay'

    id          = Column(Integer, primary_key=True)
    user_id     = Column(ForeignKey(u'user.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    agent_id    = Column(Integer, nullable=False)
    imei        = Column(String(32), nullable=False)
    pay_mode    = Column(Integer, nullable=False, server_default="1")
    trade_no    = Column(String(24), nullable=False, unique=True, index=True)
    product_id  = Column(ForeignKey(u'product.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    title       = Column(String(64), nullable=False)
    body        = Column(String(128), nullable=False)
    cat         = Column(Integer, nullable=False, server_default='0')
    total_fee   = Column(Integer, nullable=False, server_default='1')
    prepay_id   = Column(String(64), nullable=False, server_default="")
    qrcode      = Column(String(128), nullable=False, server_default="")
    nofity_res  = Column(Text, nullable=False)
    cash_fee    = Column(Integer, nullable=False, server_default="0")

    ctime       = Column(DateTime, nullable=False)
    utime       = Column(DateTime, nullable=False)

    status      = Column(Integer, nullable=False, server_default="0")

    def __init__(self, user_id, agent_id, imei, trade_no, product_id, title, body, cat, total_fee, prepay_id, qrcode, pay_mode=1):
        self.user_id = user_id
        self.agent_id = agent_id
        self.imei = imei
        self.trade_no = trade_no
        self.pay_mode = pay_mode
        self.product_id = product_id
        self.title = title
        self.body = body
        self.cat = cat
        self.total_fee = total_fee
        self.prepay_id = prepay_id
        self.qrcode = qrcode
        self.nofity_res = ''
        self.cash_fee = 0

        now = datetime.now()
        self.ctime = now
        self.utime = now
        self.status = 0

    def __repr__(self):
        return '<Pay %r>' % self.trade_no


class DailyIncome(Base):
    __tablename__ = 'daily_income'

    id          = Column(Integer, primary_key=True)
    agent_id    = Column(Integer, nullable=False)
    online_income = Column(Integer, nullable=False)
    offline_income = Column(Integer, nullable=False)
    total_consume = Column(Integer, nullable=False)
    total_balance = Column(Integer, nullable=False)
    date        = Column(Date, nullable=False)

    ctime       = Column(DateTime, nullable=False)
    utime       = Column(DateTime, nullable=False)

    status      = Column(Integer, nullable=False, server_default="0")

    def __init__(self, agent_id, online_income, offline_income, total_consume, total_balance, date):
        self.agent_id = agent_id
        self.online_income = online_income
        self.offline_income = offline_income
        self.total_consume = total_consume
        self.total_balance = total_balance
        self.date = date

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<DailyIncome: %r>' % self.id


"""
    线下投币记录表
        time    投币时间
        coin    投币金额，单位分
"""
class OfflineCoin(Base):
    __tablename__ = 'offline_coin'

    id          = Column(Integer, primary_key=True)
    imei        = Column(String(32), nullable=False, index=True)
    time        = Column(DateTime, nullable=False)
    coin        = Column(Integer, nullable=False)

    ctime       = Column(DateTime, nullable=False)
    utime       = Column(DateTime, nullable=False)

    status      = Column(Integer, nullable=False, server_default="0")

    def __init__(self, imei, time, coin):
        self.imei = imei
        self.time = time
        self.coin = coin

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<OfflineCoin: %r>' % self.id


"""
    @ 钱包交易收据表

    role 钱包所有者的角色
        0表示普通微信用户   1表示代理商用户

    trade_type      交易类型(奇数收入，偶数支出)
        1.  提成收入
        2.  微信取现
        3.  充值
        4.  消费
        5.  转账转入
        6.  转账转出
        7.  退款
        8.  代理提成退款

    payment_no      微信取现单号
        默认为'--'，当trade_type为2时，该值为微信返回值
"""
WALLET_TRADE_TYPE_TICHENG = 1
WALLET_TRADE_TYPE_WECHAT_WITHDRAW = 2
WALLET_TRADE_TYPE_DEPOSIT = 3
WALLET_TRADE_TYPE_EXPENDITURE = 4
WALLET_TRADE_TYPE_TRANSFER_IN = 5
WALLET_TRADE_TYPE_TRANSFER_OUT = 6
WALLET_TRADE_TYPE_REFUND = 7
WALLET_TRADE_TYPE_REFUND_TICHENG = 8
class WalletReceipt(Base):
    __tablename__ = 'wallet_receipt'

    id          = Column(Integer, primary_key=True)
    role        = Column(Integer, nullable=False, server_default='0')
    user_id     = Column(Integer, nullable=False)
    agent_id    = Column(Integer, nullable=False)
    wallet_id   = Column(ForeignKey(u'wallet.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    trade_type  = Column(Integer, nullable=False)
    receipt     = Column(Float, nullable=False)
    payment_no  = Column(String(64), nullable=False)
    remark      = Column(String(128), nullable=False)

    ctime       = Column(DateTime, nullable=False)
    utime       = Column(DateTime, nullable=False)

    status      = Column(Integer, nullable=False, server_default="0")

    def __init__(self, role, user_id, agent_id, wallet_id, trade_type, receipt, remark, payment_no):
        self.role = role
        self.user_id = user_id
        self.agent_id = agent_id
        self.wallet_id = wallet_id
        self.trade_type = trade_type
        self.receipt = receipt
        self.remark = remark
        self.payment_no = payment_no

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<WalletReceipt: %r>' % self.receipt


"""
    @ 钱包表

    role 钱包所有者的角色
        0表示普通微信用户   1表示代理商用户
"""
class Wallet(Base):
    __tablename__ = 'wallet'

    id      = Column(Integer, primary_key=True)
    role    = Column(Integer, nullable=False, server_default='0')
    user_id = Column(Integer, nullable=False)
    agent_id = Column(Integer, nullable=False)
    balance = Column(Float, nullable=False, server_default='0')

    ctime   = Column(DateTime, nullable=False)
    utime   = Column(DateTime, nullable=False)

    status  = Column(Integer, nullable=False, server_default="0")

    def __init__(self, user_id, role, agent_id):
        self.user_id = user_id
        self.role = role
        self.agent_id = agent_id

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<Wallet: %r>' % self.id
