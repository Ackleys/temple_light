#!/usr/bin/env python3
#coding: utf8

import os

from flask.ext.script import Manager, Shell
import sqlalchemy

from config import config

from app import create_app, db
from app.database.model import *

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
dbg(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db)
manager.add_command("shell", Shell(make_context=make_shell_context))

def init_database_and_tables():
    engine = sqlalchemy.create_engine('mysql+mysqlconnector://%s:%s@%s' % (config.MYSQL_USER, config.MYSQL_PASSWORD, config.MYSQL_IP))
    dbs = ('openluat_user', 'street_machine', 'CWS_APP')
    for database in dbs:
        sql = 'create database %s default character set utf8mb4 collate utf8mb4_unicode_ci' % database
        try:
            engine.execute(sql)
        except sqlalchemy.exc.DatabaseError as e:
            if e.orig.errno == 1007:
                print('%s exists' % database)
            else:
                raise

    db.create_all()


def make_admin_user():

    phone = '15300002713'
    name  = 'acac'
    email = 'acac@airm2m.com'
    password = '888888'
    role = '111112000000'

    # 检查初始化
    god = db.session.query(God).filter(God.phone==phone).first()
    if god:
        print('already init')
        return 

    # 创建openluat_user
    now = datetime.now()
    openluat_user = OpenLuatUser(name=name, email=email, password=password,
        phone=phone, role=role, creation_time=now, last_login_time=now)
    db.session.add(openluat_user)
    db.session.commit()

    # 创建super_god
    role = 2
    remark = '超级管理员'
    super_god = God(openluat_user.id, role, name, phone, email, remark)
    db.session.add(super_god)
    db.session.commit()


@manager.command
def init():

    # 1. 创建数据库
    init_database_and_tables()

    # 2. 创建超级管理员用户
    make_admin_user()


@manager.command
def create_db():
    db.create_all()


if __name__ == '__main__':
    manager.run()