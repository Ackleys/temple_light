#!/usr/bin/env python3
# coding: utf8
# 20170706 anChaOs

import os, sys, time, logging
from datetime import date, datetime, timedelta
from logging.handlers import RotatingFileHandler

import redis

# 第一步，创建一个logger  
logger = logging.getLogger()
logger.setLevel(logging.INFO)    # Log等级总开关

# 第二步，创建一个RotatingFileHandler，用于写入日志文件
logfile = 'log.log'
rh = RotatingFileHandler(logfile, mode='w', maxBytes=10*1024*1024, backupCount=5)
rh.setLevel(logging.INFO)   # 输出到file的log等级的开关

# 第三步，再创建一个handler，用于输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)   # 输出到console的log等级的开关

# 第四步，定义handler的输出格式
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
rh.setFormatter(formatter)
ch.setFormatter(formatter)

# 第五步，将logger添加到handler里面
logger.addHandler(rh)
logger.addHandler(ch)

import setting
import dbapi as dbapi

R    = redis.Redis(host='127.0.0.1', port=6379, db=0)
NAME = setting.REDIS_NAME
KEY  = setting.REDIS_HASH_KEY

LASTDAY = setting.LASTDAY
WORKING = setting.WORKING
COMPLETE = setting.COMPLETE


def get_yesterday_start_end():
    start = date.today() - timedelta(days=LASTDAY)
    end   = start + timedelta(days=LASTDAY)
    return start, end


def insert_daily_wallet_income(last_date):
    db_session = dbapi.get_db_session()
    logging.info('resis, %s--%s: %s' % (NAME, KEY, R.hget(NAME, KEY)))
    start = last_date
    end   = last_date + timedelta(days=1)
    result = dbapi.get_sum_wallet_receipt(db_session, start, end)
    if not result:
        logging.warning('%s, no record found' % last_date )
        return

    daily_incomes = []
    for res in result:
        wallet_id, wallet_income = res
        wallet = dbapi.get_wallet_receipt(db_session, wallet_id)
        if not wallet:
            logging.warning('%s, no wallet found' % wallet_id )
            continue
        agent_id = wallet.agent_id
        daily_income = dbapi.get_daily_income(db_session, agent_id, last_date)
        if daily_income:
            logging.warning('重复插入, agent_id: %s--%s' % (agent_id, last_date))
            continue
        wallet_income = int(wallet_income)
        offline_income = 0
        total_consume = wallet_income
        total_balance = 0
        logging.info((last_date, agent_id, wallet_income,
            offline_income, total_consume, total_balance))
        daily_income = dbapi.make_new_daily_income(agent_id, wallet_income,
            offline_income, total_consume, total_balance, last_date)
        daily_incomes.append(daily_income)
    db_session.add_all(daily_incomes)
    try:
        db_session.commit()
    except Exception as e:
        logging.exception(e)
        db_session.rollback()
    finally:
        db_session.close()
    
    logging.info('resis, %s--%s: %s' % (NAME, KEY, R.hget(NAME, KEY)))


def insert_daily_income(last_date):
    db_session = dbapi.get_db_session()
    logging.info('resis, %s--%s: %s' % (NAME, KEY, R.hget(NAME, KEY)))
    start = last_date
    end   = last_date + timedelta(days=1)
    result = dbapi.get_sum_total_fee(db_session, start, end)
    if not result:
        logging.warning('%s, no record found' % last_date )
        return

    daily_incomes = []
    for res in result:
        agent_id, online_income = res
        daily_income = dbapi.get_daily_income(db_session, agent_id, last_date)
        if daily_income:
            logging.warning('重复插入, agent_id: %s--%s' % (agent_id, last_date))
            continue
        online_income = int(online_income)
        offline_income = 0
        total_consume = online_income
        total_balance = 0
        logging.info((agent_id, online_income,
            offline_income, total_consume, total_balance))
        daily_income = dbapi.make_new_daily_income(agent_id, online_income,
            offline_income, total_consume, total_balance, last_date)
        daily_incomes.append(daily_income)
    db_session.add_all(daily_incomes)
    try:
        db_session.commit()
    except Exception as e:
        logging.exception(e)
        db_session.rollback()
    finally:
        db_session.close()
    
    logging.info('resis, %s--%s: %s' % (NAME, KEY, R.hget(NAME, KEY)))


def settle_accounts(last_date):
    # redis中写入正在结算，以提醒其他相关的业务，暂时无法使用
    # R.hset(NAME, KEY, WORKING)

    # 开始任务
    # dbapi.connect_mysql()

    # insert_daily_income(last_date)
    insert_daily_wallet_income(last_date)

    # dbapi.disconnect_mysql()

    # redis中，写入任务已完成
    # R.hset(NAME, KEY, COMPLETE)


def keep_mysql_connect():
    db_session = dbapi.get_db_session()
    # print('keep_mysql_connect')
    db_session.query(dbapi.DailyIncome).first()
    db_session.close()


def main():
    # 每日0点5分0秒到5秒之间，开始任务
    start_second = 5*60
    end_second   = 5*60+5
    # counter = 12
    while True:
        dt = datetime.now()
        # 每日0点5分0秒到5秒之间，开始任务
        second_pass = dt.hour*60*60 + dt.minute*60 + dt.second
        if start_second <= second_pass <= end_second:
            # 开始任务
            last_date = date.today() - timedelta(days=1)
            last_date = datetime(last_date.year, last_date.month, last_date.day)
            settle_accounts(last_date)

        # if counter == 12:
        #     # 每1分钟，连接一次
        #     keep_mysql_connect()
        #     counter = 0

        # counter += 1
        time.sleep(5)


def test():
    last_date = datetime(2017, 9, 30)
    while last_date < datetime(2017, 11, 13):
        settle_accounts(last_date)
        last_date = last_date + timedelta(days=1)


def test_last_date():
    keep_mysql_connect()
    last_date = date.today() - timedelta(days=1)
    settle_accounts(last_date)


if __name__ == '__main__':
    logging.info('======================================================')
    logging.info('======================================================')
    logging.info('======================================================')
    logging.info('======================================================')
    logging.info('======================================================')
    logging.info('===================settle_accounts====================')
    logging.info('===================settle_accounts====================')
    logging.info('===================settle_accounts====================')
    logging.info('======================================================')
    logging.info('======================================================')
    logging.info('======================================================')
    logging.info('======================================================')
    logging.info('======================================================')
    main()
    # test()