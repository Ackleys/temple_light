#!/usr/bin/env python3
# coding: utf8
# 20170825 anChaOs

import os

MYSQL_USER = 'root'
MYSQL_PASSWORD = 'password'
MYSQL_IP = '127.0.0.1'

if os.environ.get('production'):
    MYSQL_URI = 'mysql+mysqlconnector://%s:%s@%s/street_machine?charset=utf8mb4' % (MYSQL_USER, MYSQL_PASSWORD, MYSQL_IP)
    REDIS_NAME = 'street_machine_pro'
    REDIS_HASH_KEY = 'settling_accounts'
    WORKING = 1
    COMPLETE = 0
    LASTDAY = 1 # 1表示昨天，大于1表示n天前
else:
    MYSQL_URI = 'mysql+mysqlconnector://%s:%s@%s/street_machine?charset=utf8mb4' % (MYSQL_USER, MYSQL_PASSWORD, MYSQL_IP)
    REDIS_NAME = 'street_machine_test'
    REDIS_HASH_KEY = 'settling_accounts'
    WORKING = 1
    COMPLETE = 0
    LASTDAY = 1 # 1表示昨天，大于1表示n天前
