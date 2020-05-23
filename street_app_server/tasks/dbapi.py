#!/usr/bin/env python3
# coding: utf8
# 20170825 anChaOs

import sys, json, logging, threading
from functools import wraps
from datetime import datetime
from sqlalchemy import func

from models import *


def catch_except(func):
    @wraps(func)
    def wrapper(*args, **kws):
        try:
            return func(*args, **kws)
        except Exception as e:
            logging.exception(e)
            try:
                # reconnect_mysql()
                return func(*args, **kws)
            except:
                logging.exception(e)
                return None
    return wrapper


# def connect_mysql():
#     logging.info('开始连接Mysql 数据库...')
#     reconnect_mysql()


# def disconnect_mysql():
#     db_session.close()
#     logging.info('断开连接Mysql 数据库...')


@catch_except
def get_sum_total_fee(db_session, start, end):
    logging.info((start, end))
    query = db_session.query(Pay.agent_id, func.sum(Pay.total_fee).label("online_income")).\
        filter(Pay.status==1).filter(Pay.pay_mode!=3).filter(Pay.ctime>start).filter(Pay.ctime<end).\
        group_by(Pay.agent_id)
    return query.all()


@catch_except
def get_sum_wallet_receipt(db_session, start, end):
    query = db_session.query(WalletReceipt.wallet_id, func.sum(WalletReceipt.receipt).label("wallet_income"))
    query = query.filter(WalletReceipt.ctime>start).filter(WalletReceipt.ctime<end).\
        filter(WalletReceipt.role==1).filter(WalletReceipt.trade_type!=WALLET_TRADE_TYPE_WECHAT_WITHDRAW).\
        group_by(WalletReceipt.wallet_id)
    return query.all()


@catch_except
def make_new_daily_income(agent_id, online_income, offline_income, total_consume, total_balance, date):
    daily_income = DailyIncome(agent_id, online_income, offline_income, total_consume, total_balance, date)
    return daily_income


@catch_except
def get_daily_income(db_session, agent_id, date):
    query = db_session.query(DailyIncome).filter(DailyIncome.agent_id==agent_id).\
        filter(DailyIncome.date==date)
    return query.first()


@catch_except
def get_wallet_receipt(db_session, wallet_id):
    return db_session.query(Wallet).filter(Wallet.id==wallet_id).first()