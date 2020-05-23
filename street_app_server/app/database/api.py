#!/usr/bin/env python3
# coding: utf8
# 20170220 anChaOs

import json, time, traceback
from functools import wraps
import sqlalchemy
from sqlalchemy import func, text, create_engine

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import or_

from pymongo import DESCENDING

from app import db, mongodb, mongodb_wst
from .model import *

from app.tool import dbg                    # for print
from app.tool import print_exception_info   # for traceback

# error
import app.error as error
ApiError = error.ApiError

engine     = create_engine(config.USER_MYSQL_URI, convert_unicode=True, pool_size=100, pool_recycle=5)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


"""
    @ 最新变动
    1. 所有的db.session将统一在view中commit

"""


class DatabaseError(Exception):
    def __init__(self, msg="", error_no=0):
        self.msg = msg
        self.error_no = error_no
        
    def __str__(self):
        return repr(self.msg)


def catch_except(func):
    @wraps(func)
    def wrapper(*args, **kws):
        try:
            return func(*args, **kws)
        except ApiError as e:
            raise e
        except sqlalchemy.exc.DatabaseError as e:
            db.session.rollback()
            print_exception_info()
            if 'page' in kws and 'psize' in kws:
                return 0, None
            return None
        except:
            print_exception_info()
            if 'page' in kws and 'psize' in kws:
                return 0, None
            return None
    return wrapper

#  =============== mongodb =================


def mongo_dict_filter(d):
    if "_id" in d:
        d.pop("_id")
    for k in d:
        if isinstance(d[k], datetime):
            d[k] = int(d[k].timestamp())
    return d


@catch_except
def get_cws_device_status(imei):
    return mongodb.cws.device_status.find_one({'imei': imei})


@catch_except
def get_cws_device_status_numbers(imeis, online):
    # online 0离线 1在线 4关机
    query = {'imei': {'$in': imeis}, 'online': online}
    return mongodb.cws.device_status.find(query).count()


@catch_except
def insert_datagram(data):
    data['time'] = datetime.now()
    mongodb.mafu.datagram.insert_one(data)


@catch_except
def fetch_datagram(dbtype, imei, page=1, psize=10, **kwargs):
    query = {'imei': imei}
    if 'start' in kwargs and 'end' in kwargs:
        query['time'] = {"$gte": kwargs['start'], "$lte": kwargs['end']}
    if 'datagram_type' in kwargs:
        query['datagram_type'] = kwargs['datagram_type']

    if dbtype == 1:
        mdb = mongodb
    elif dbtype == 2:
        mdb = mongodb_wst
    else:
        dbg('unkown db type: %d' % dbtype)
        return 0, []

    page = int(page)
    psize = int(psize)

    count = mdb.mafu.datagram.find(query).count()
    datagrams = mdb.mafu.datagram.find(query).skip(psize*(page-1)).limit(psize).sort("time", DESCENDING)
    datagrams = list(map(mongo_dict_filter, list(datagrams)))

    return count, datagrams


@catch_except
def update_access_token(appid, access_token, expires_in):
    query  = {"appid": appid}
    update = {
        "$set": {
            'access_token': {
                'access_token': access_token,
                'expires_in'  : expires_in,
                'utime'       : int(time.time())
            }
        }
    }
    mongodb.wechat.cache.find_one_and_update(query, update, upsert=True)
    return True


@catch_except
def get_access_token(appid):
    data = mongodb.wechat.cache.find_one({"appid": appid})
    if data and 'access_token' in data:
        return data['access_token']
    return None


@catch_except
def update_jsapi_ticket(appid, jsapi_ticket, expires_in):
    query  = {"appid": appid}
    update = {
        "$set": {
            'jsapi_ticket': {
                'jsapi_ticket': jsapi_ticket,
                'expires_in'  : expires_in,
                'utime'       : int(time.time())
            }
        }
    }
    mongodb.wechat.cache.find_one_and_update(query, update, upsert=True)
    return True


def get_jsapi_ticket(appid):
    data = mongodb.wechat.cache.find_one({"appid": appid})
    if data and 'jsapi_ticket' in data:
        return data['jsapi_ticket']
    return None


#  =============== mongodb end =================


@catch_except
def make_new_openluat_user(name='', email='', phone='',
    password=config.DEFAULT_PASSWORD, role='000000000000'):
    user = get_openluat_user(name=name)
    if user:
        raise ApiError('ERROR_NAME_EXISTS', error.ERROR_NAME_EXISTS)
    user = get_openluat_user(email=email)
    if user:
        raise ApiError('ERROR_EMAIL_EXISTS', error.ERROR_EMAIL_EXISTS)
    user = get_openluat_user(phone=phone)
    if user:
        raise ApiError('ERROR_PHONE_EXISTS', error.ERROR_PHONE_EXISTS)
    now = datetime.now()
    user = OpenLuatUser(name=name, email=email, password=password,
        phone=phone, role=role, creation_time=now, last_login_time=now)
    db.session.add(user)
    return user


@catch_except
def get_openluat_user(**kwargs):
    query = db.session.query(OpenLuatUser)
    if 'id' in kwargs:
        return query.filter(OpenLuatUser.id==kwargs['id']).first()
    if 'phone' in kwargs:
        phone = kwargs['phone']
        return query.filter(OpenLuatUser.phone==phone).first()
    if 'name' in kwargs:
        name = kwargs['name']
        return query.filter(OpenLuatUser.name==name).first()
    if 'email' in kwargs:
        email = kwargs['email']
        return query.filter(OpenLuatUser.email==email).first()


@catch_except
def update_openluat_user(openluat_user, **kwargs):
    if 'password' in kwargs:
        openluat_user.password = kwargs['password']
        db.session.add(openluat_user)
    return openluat_user


@catch_except
def make_new_user(name='', phone='', email='', password=config.DEFAULT_PASSWORD,
        roll=0, wechat_body=None):
    user = User(name, phone, email, password, roll, wechat_body)
    db.session.add(user)
    return user


@catch_except
def get_user(**kwargs):
    query = db.session.query(User)
    if 'user_id' in kwargs:
        return query.filter(User.id==kwargs['user_id']).first()
    if 'phone' in kwargs:
        return query.filter(User.phone==kwargs['phone']).first()
    if 'name' in kwargs:
        return query.filter(User.name==kwargs['name']).first()
    # 其他的查询待添加


@catch_except
def update_user(user, **kwargs):
    updated = False
    if 'nickname' in kwargs:
        user.nickname = kwargs['nickname']
        updated = True
    if 'headimgurl' in kwargs:
        user.headimgurl = kwargs['headimgurl']
        updated = True
    if 'password' in kwargs:
        user.password = kwargs['password']
        updated = True
    if 'wechat_body' in kwargs:
        updated = True
        body = kwargs['wechat_body']
        user.nickname = body.get('nickname', '')
        user.sex = body.get('sex', '')
        user.province = body.get('province', '')
        user.city = body.get('city', '')
        user.country = body.get('country', '')
        user.headimgurl = body.get('headimgurl', '')
    if updated:
        user.utime = datetime.now()
    return user


@catch_except
def make_new_wechat_user(body):
    wechat_user = WechatUser(body)
    db.session.add(wechat_user)
    return wechat_user


@catch_except
def get_wechat_user(**kwargs):
    query = db.session.query(WechatUser)
    if 'user_id' in kwargs:
        return query.filter(WechatUser.user_id==kwargs['user_id']).first()
    if 'openid' in kwargs:
        return query.filter(WechatUser.openid==kwargs['openid']).first()
    if 'admin_uid' in kwargs:
        return query.filter(WechatUser.admin_uid==kwargs['admin_uid']).first()


@catch_except
def update_wechat_user(wechat_user, **kwargs):
    updated = False
    if 'admin_uid' in kwargs:
        wechat_user.admin_uid = kwargs['admin_uid']
        updated = True
    if 'wechat_body' in kwargs:
        updated = True
        body = kwargs['wechat_body']
        wechat_user.nickname = body.get('nickname', '')
        wechat_user.sex = body.get('sex', '')
        wechat_user.province = body.get('province', '')
        wechat_user.city = body.get('city', '')
        wechat_user.country = body.get('country', '')
        wechat_user.headimgurl = body.get('headimgurl', '')
        if isinstance(body.get('privilege', ''), list):
            body['privilege'] = json.dumps(body['privilege'])
        wechat_user.privilege = body.get('privilege', '')
    if 'headimgurl' in kwargs:
        wechat_user.headimgurl = kwargs['headimgurl']
        updated = True
    if updated:
        wechat_user.utime = datetime.now()
    return wechat_user


@catch_except
def make_new_aply_agent(user_id, hookid, name, phone, desc):
    aply_agent = AplyAgent(user_id, hookid, name, phone, desc)
    db.session.add(aply_agent)
    return aply_agent

@catch_except
def get_aply_agent(**kwargs):
    query = db.session.query(AplyAgent)
    if 'aply_agent_id' in kwargs:
        return query.filter(AplyAgent.id==kwargs['aply_agent_id']).first()


@catch_except
def update_aply_agent(aply_agent, **kwargs):
    updated = False
    if 'status' in kwargs:
        aply_agent.status = kwargs['status']
        updated = True
    if updated:
        aply_agent.utime = datetime.now()
    return aply_agent


@catch_except
def make_new_agent(salesman, user_id, hook_agent_id, level, slevel, expandable, withdrawable, name, phone, email, address, remark, desc=""):
    agent = Agent(salesman, user_id, hook_agent_id, level, slevel, expandable, withdrawable, name, phone, email, desc, address, remark)
    db.session.add(agent)
    return agent


@catch_except
def get_agent(**kwargs):
    query = db.session.query(Agent)

    # 筛选
    if 'fuzzy_name' in kwargs:
        query = query.filter(Agent.name.like("%%%s%%" % kwargs['fuzzy_name']))
    if 'fuzzy_phone' in kwargs:
        query = query.filter(Agent.phone.like("%%%s%%" % kwargs['fuzzy_phone']))

    # 单条数据查询
    if 'id' in kwargs:
        return query.filter(Agent.id==kwargs['id']).first()
    if 'user_id' in kwargs:
        return query.filter(Agent.openluat_user_id==kwargs['user_id']).first()
    if 'phone' in kwargs:
        return query.filter(Agent.phone==kwargs['phone']).first()
    if 'email' in kwargs:
        return query.filter(Agent.email==kwargs['email']).first()

    # 特殊查询
    if 'hook_agent_id' in kwargs and 'salesman' in kwargs and 'name_id_only' in kwargs:
        hook_agent_id = kwargs['hook_agent_id']
        salesman = kwargs['salesman']
        return db.session.query(Agent.id, Agent.name).filter(Agent.hook_agent_id==hook_agent_id).\
            filter(Agent.salesman==salesman)

    # 多条数据查询
    if 'hook_agent_id' in kwargs and 'salesman' in kwargs:
        hook_agent_id = kwargs['hook_agent_id']
        salesman = kwargs['salesman']
        query = query.filter(Agent.hook_agent_id==hook_agent_id).filter(Agent.salesman==salesman)
    if 'hook_agent_id' in kwargs:
        hook_agent_id = kwargs['hook_agent_id']
        query = query.filter(Agent.hook_agent_id==hook_agent_id)

    # 是否分页
    if 'page' in kwargs and 'psize' in kwargs:
        page = kwargs['page']
        psize = kwargs['psize']
        return query.count(), query.slice(psize*(page-1), psize*page).all()
    else:
        return query.all()


@catch_except
def update_agent(agent, **kwargs):
    updated = False
    if 'name' in kwargs:
        agent.name = kwargs['name']
        updated = True
    if 'phone' in kwargs:
        agent.phone = kwargs['phone']
        updated = True
    if 'desc' in kwargs:
        agent.desc = kwargs['desc']
        updated = True
    if 'address' in kwargs:
        agent.address = kwargs['address']
        updated = True
    if 'remark' in kwargs:
        agent.remark = kwargs['remark']
        updated = True
    if 'expandable' in kwargs:
        agent.expandable = kwargs['expandable']
        updated = True
    if 'withdrawable' in kwargs:
        agent.withdrawable = kwargs['withdrawable']
        updated = True
    if updated:
        agent.utime = datetime.now()
        db.session.add(agent)
    return agent


@catch_except
def make_new_product(agent_id, title, body, value, cat, price, inventory=99999):
    product = Product(agent_id, title, body, value, cat, price, inventory)
    db.session.add(product)
    return product


@catch_except
def get_product(**kwargs):
    query = db.session.query(Product)
    if 'product_id' in kwargs:
        return query.filter(Product.id==kwargs['product_id']).first()
    if 'agent_id' in kwargs and 'cat' in kwargs:
        return query.filter(Product.agent_id==kwargs['agent_id']).\
            filter(Product.cat==kwargs['cat']).\
            filter(Product.deleted==0).all()
    if 'agent_id' in kwargs:
        return query.filter(Product.agent_id==kwargs['agent_id']).\
            filter(Product.deleted==0).all()


@catch_except
def update_product(product, **kwargs):
    updated = False
    if 'title' in kwargs:
        product.title = kwargs['title']
        updated = True
    if 'body' in kwargs:
        product.body = kwargs['body']
        updated = True
    if 'value' in kwargs:
        product.value = kwargs['value']
        updated = True
    if 'price' in kwargs:
        product.price = kwargs['price']
        updated = True
    if 'inventory' in kwargs:
        product.inventory = kwargs['inventory']
        updated = True
    if 'deleted' in kwargs:
        product.deleted = kwargs['deleted']
        updated = True
    if updated:
        product.utime = datetime.now()
    return product


@catch_except
def make_new_pay(user_id, agent_id, imei, trade_no, product_id, title, body, cat, total_fee, pay_mode=1, prepay_id='', qrcode=''):
    pay = Pay(user_id, agent_id, imei, trade_no, product_id, title, body, cat, total_fee, prepay_id, qrcode, pay_mode)
    db.session.add(pay)
    return pay


@catch_except
def get_pay(**kwargs):
    query = db.session.query(Pay)
    if 'pay_id' in kwargs:
        return query.filter(Pay.id==kwargs['pay_id']).first()
    if 'trade_no' in kwargs:
        return query.filter(Pay.trade_no==kwargs['trade_no']).first()

    if 'product_id' in kwargs:
        return query.filter(Pay.product_id==kwargs['product_id']).all()


@catch_except
def get_last_pay(imei, not_include_pay_id=None):
    query = db.session.query(Pay).filter(Pay.imei==imei).filter(Pay.status==1).filter(Pay.cat==0)
    if not_include_pay_id:
        query = query.filter(Pay.id!=not_include_pay_id)
    return query.order_by(Pay.id.desc()).first()


@catch_except
def get_max_pay_id():
    res = db.session.query(Pay.id).order_by(Pay.id.desc()).first()
    if res and isinstance(res, tuple):
        return res[0]
    return 1


@catch_except
def update_pay(pay, **kwargs):
    updated = False
    if 'imei' in kwargs:
        pay.imei = kwargs['imei']
        updated = True
    if 'transaction_id' in kwargs:
        pay.transaction_id = kwargs['transaction_id']
        updated = True
    if 'nofity_res' in kwargs:
        pay.nofity_res = kwargs['nofity_res']
        updated = True
    if 'cash_fee' in kwargs:
        pay.cash_fee = kwargs['cash_fee']
        updated = True
    if 'status' in kwargs:
        pay.status = kwargs['status']
        updated = True
    if 'ali_trade_no' in kwargs:
        pay.ali_trade_no = kwargs['ali_trade_no']
        updated = True
    if 'user_id' in kwargs:
        pay.user_id = kwargs['user_id']
        updated = True
    if 'prepay_id' in kwargs:
        pay.prepay_id = kwargs['prepay_id']
        updated = True
    if 'qrcode' in kwargs:
        pay.qrcode = kwargs['qrcode']
        updated = True
    if updated:
        pay.utime = datetime.now()
    return pay


@catch_except
def delete_pays_and_records(imei):
    pays = db.session.query(Pay).filter(Pay.imei==imei)
    count = 0
    for pay in pays:
        pay.deleted = 1
        pay.utime = datetime.now()
        db.session.add(pay)
        record = db.session.query(Record).filter(Record.pay_id==pay.id).first()
        if record:
            db.session.delete(record)
        count += 1
    return count


@catch_except
def make_new_record(pay_id, pay_way, user_id, agent_id, product_id, stime, etime):
    record = Record(pay_id, pay_way, user_id, agent_id, product_id, stime, etime)
    db.session.add(record)
    return record


@catch_except
def get_record(**kwargs):
    query = db.session.query(Record)
    if 'pay_id' in kwargs:
        return query.filter(Record.pay_id==kwargs['pay_id']).first()
    if 'record_id' in kwargs:
        return query.filter(Record.id==kwargs['record_id']).first()
    if 'imei' in kwargs and 'recent' in kwargs:
        query = query.join(Pay, Record.pay_id==Pay.id).filter(
            Pay.imei==kwargs['imei']).order_by(Record.id.desc())
        return query.first()


@catch_except
def update_record(record, **kwargs):
    if 'status' in kwargs:
        record.status = kwargs['status']
        record.utime = datetime.now()
    db.session.add(record)
    return record


@catch_except
def make_new_record_no_pay(imei, user_id, agent_id, stime, etime):
    record = RecordNoPay(imei, user_id, agent_id, stime, etime)
    db.session.add(record)
    return record


@catch_except
def get_record_no_pay(**kwargs):
    query = db.session.query(RecordNoPay)

    # 单条查询
    if 'id' in kwargs:
        return query.filter(RecordNoPay.id==kwargs['id']).first()

    # 特殊查询
    if 'count' in kwargs and 'imei' in kwargs: 
        return int(query.filter(RecordNoPay.imei==kwargs['imei']).count())

    # 多条查询
    if 'imei' in kwargs:
        query = query.filter(RecordNoPay.imei==kwargs['imei'])

    # 是否分页
    if 'page' in kwargs and 'psize' in kwargs:
        page = kwargs['page']
        psize = kwargs['psize']
        return query.count(), query.slice(psize*(page-1), psize*page).all()
    else:
        return query.all()


@catch_except
def make_new_record_coupon_no_pay(imei, user_id, agent_id, stime, etime):
    record = RecordCouponNopay(imei, user_id, agent_id, stime, etime)
    db.session.add(record)
    return record


@catch_except
def get_record_coupon_no_pay(**kwargs):
    query = db.session.query(RecordCouponNopay)
    if 'id' in kwargs:
        return query.filter(RecordCouponNopay.id==kwargs['id']).first()


@catch_except
def make_new_game_coin(user_id):
    game_coin = GameCoin(user_id)
    db.session.add(game_coin)
    return game_coin


@catch_except
def get_game_coin(**kwargs):
    query = db.session.query(GameCoin)
    if 'id' in kwargs:
        return query.filter(GameCoin.id==kwargs['id']).first()
    if 'user_id' in kwargs:
        return query.filter(GameCoin.user_id==kwargs['user_id']).first()


@catch_except
def update_game_coin(game_coin, **kwargs):
    updated = False
    if 'coin' in kwargs:
        game_coin.coin = kwargs['coin']
        updated = True
    if updated:
        game_coin.utime = datetime.now()
        db.session.add(game_coin)
    return game_coin


@catch_except
def maka_new_coin_record(user_id, in_out, coin):
    coin_record = CoinRecord(user_id, in_out, coin)
    db.session.add(coin_record)
    return coin_record


@catch_except
def make_new_refund(user_id, pay_id, refund_no, total_fee, refund_fee, status=0):
    refund = Refund(user_id, pay_id, refund_no, total_fee, refund_fee, status)
    db.session.add(refund)
    return refund


@catch_except
def get_refund(**kwargs):
    query = db.session.query(Refund)
    if 'refund_id' in kwargs:
        return query.filter(Refund).filter(Refund.id==kwargs['refund_id']).first()
    if 'refund_no' in kwargs:
        return query.filter(Refund).filter(Refund.refund_no==kwargs['refund_no']).first()


@catch_except
def get_max_refund_id():
    res = db.session.query(Refund.id).order_by(Refund.id.desc()).first()
    if res and isinstance(res, tuple):
        return res[0]
    return 1


@catch_except
def update_refund(refund, **kwargs):
    updated = False
    if 'nofity_res' in kwargs:
        refund.nofity_res = kwargs['nofity_res']
        updated = True
    if 'status' in kwargs:
        refund.status = kwargs['status']
        updated = True
    if updated:
        refund.utime = datetime.now()
        db.session.add(refund)
    return refund


@catch_except
def make_new_device(imei, cat, agent_id, address_id):
    owner_agent_id = agent_id
    device = Device(imei, cat, agent_id, owner_agent_id, address_id)
    db.session.add(device)
    return device


@catch_except
def make_new_devices(imeis, cat, agent_id, address_id):
    devices = []
    owner_agent_id = agent_id
    for imei in imeis:
        device = Device(imei, cat, agent_id, owner_agent_id, address_id)
        devices.append(device)
    db.session.add_all(devices)
    return devices


@catch_except
def get_device(**kwargs):
    query = db.session.query(Device)

    # 筛选
    if 'coupon' in kwargs:
        query = query.filter(Device.coupon==kwargs['coupon'])
    if 'address_id' in kwargs:
        address_id = kwargs['address_id']
        if address_id:
            query = query.filter(Device.address_id==address_id)
    if 'nopay' in kwargs:
        if kwargs['nopay']:
            query = query.filter(Device.nopay>0)
        else:
            query = query.filter(Device.nopay==0)

    # 单条数据查询
    if 'id' in kwargs:
        return query.filter(Device.id==kwargs['id']).first()
    if 'device_id' in kwargs:
        return query.filter(Device.id==kwargs['device_id']).first()
    if 'imei' in kwargs:
        return query.filter(Device.imei==kwargs['imei']).first()

    # 特殊查询
    if 'agent_id' in kwargs and 'salesman' in kwargs and 'count' in kwargs and kwargs['count'] == True:
        to_agent = kwargs['agent_id']
        query = query.join(DeviceDistributionSalesman, Device.id==DeviceDistributionSalesman.device_id)\
                .filter(DeviceDistributionSalesman.to_agent==to_agent).order_by(Device.id)
        return query.count(), query.all()
    if 'agent_id' in kwargs and 'count' in kwargs and kwargs['count'] == True:
        to_agent = kwargs['agent_id']
        query = query.join(DeviceDistribution, Device.id==DeviceDistribution.device_id)\
            .filter(DeviceDistribution.to_agent==to_agent).order_by(Device.id)
        return query.count(), query.all()

    # 多条数据查询
    if 'agent_id' in kwargs and 'salesman' in kwargs:
        to_agent = kwargs['agent_id']
        salesman = kwargs['salesman']
        if salesman == 0:
            query = query.filter(Device.owner_agent_id==to_agent).order_by(Device.id)
        elif salesman == 1:
            query = query.join(DeviceDistributionSalesman, Device.id==DeviceDistributionSalesman.device_id)\
                .filter(DeviceDistributionSalesman.to_agent==to_agent).order_by(Device.id)
    elif 'agent_id' in kwargs:
        to_agent = kwargs['agent_id']
        query = query.join(DeviceDistribution, Device.id==DeviceDistribution.device_id)\
            .filter(DeviceDistribution.to_agent==to_agent).order_by(Device.id)
    elif 'owner_agent_id' in kwargs:
        query = query.filter(Device.owner_agent_id==kwargs['owner_agent_id']).order_by(Device.id)

    # 是否分页
    if 'page' in kwargs and 'psize' in kwargs:
        page = kwargs['page']
        psize = kwargs['psize']
        return query.count(), query.slice(psize*(page-1), psize*page).all()
    else:
        return query.all()


@catch_except
def update_device(device, **kwargs):
    updated = False
    if 'address_id' in kwargs:
        device.address_id = kwargs['address_id']
        updated = True
    if 'cat' in kwargs:
        device.cat = kwargs['cat']
        updated = True
    if 'map_display' in kwargs:
        device.map_display = kwargs['map_display']
        updated = True
    if 'l1' in kwargs:
        device.l1 = kwargs['l1']
        updated = True
    if 'l2' in kwargs:
        device.l2 = kwargs['l2']
        updated = True
    if 'l3' in kwargs:
        device.l3 = kwargs['l3']
        updated = True
    if 'l4' in kwargs:
        device.l4 = kwargs['l4']
        updated = True
    if 'sl1' in kwargs:
        device.sl1 = kwargs['sl1']
        updated = True
    if 'sl2' in kwargs:
        device.sl2 = kwargs['sl2']
        updated = True
    if 'sl3' in kwargs:
        device.sl3 = kwargs['sl3']
        updated = True
    if 'agent_id' in kwargs:
        device.owner_agent_id = kwargs['agent_id']
        if kwargs['agent_id'] == 0:
            device.agent_id = kwargs['agent_id']
        updated = True
    if 'salesman_agent_id' in kwargs:
        device.salesman_agent_id = kwargs['salesman_agent_id']
        updated = True
    if 'remark' in kwargs:
        device.remark = kwargs['remark']
        updated = True
    if 'nopay' in kwargs:
        device.nopay = kwargs['nopay']
        if device.nopay:
            device.coupon = 0
        updated = True
    if 'coupon' in kwargs:
        device.coupon = kwargs['coupon']
        if device.coupon:
            device.nopay = 0
        updated = True
    if 'product_unit_price' in kwargs:
        device.product_unit_price = kwargs['product_unit_price']
        updated = True
    if 'product_min_money' in kwargs:
        device.product_min_money = kwargs['product_min_money']
        updated = True
    if 'product_unit' in kwargs:
        device.product_unit = kwargs['product_unit']
        updated = True
    if 'product_unit_pluse' in kwargs:
        device.product_unit_pluse = kwargs['product_unit_pluse']
        updated = True
    if 'low' in kwargs:
        device.low = kwargs['low']
        updated = True
    if 'high' in kwargs:
        device.high = kwargs['high']
        updated = True
    if updated:
        device.utime = datetime.now()
        db.session.add(device)
    return device


@catch_except
def make_new_device_distribution(device_id, imei, from_agent, to_agent, rate=0.0):
    device_distribution = DeviceDistribution(device_id, imei, from_agent, to_agent, rate)
    db.session.add(device_distribution)
    return device_distribution


@catch_except
def get_device_distribution(**kwargs):
    query = db.session.query(DeviceDistribution)
    if 'imei' in kwargs and 'from_agent' in kwargs:
        imei = kwargs['imei']
        from_agent = kwargs['from_agent']
        return query.filter(DeviceDistribution.imei==imei).\
            filter(DeviceDistribution.from_agent==from_agent).first()
    if 'imei' in kwargs and 'to_agent' in kwargs:
        imei = kwargs['imei']
        to_agent = kwargs['to_agent']
        return query.filter(DeviceDistribution.imei==imei).\
            filter(DeviceDistribution.to_agent==to_agent).first()
    if 'device_id' in kwargs:
        device_id = kwargs['device_id']
        return query.filter(DeviceDistribution.device_id==device_id).all()
    if 'imei' in kwargs:
        imei = kwargs['imei']
        return query.filter(DeviceDistribution.imei==imei).all()


@catch_except
def update_device_distribution(device_distribution, **kwargs):
    if 'rate' in kwargs:
        print('update: %s rate: %f' % (device_distribution.imei, kwargs['rate']))
        device_distribution.rate = kwargs['rate']
        device_distribution.utime = datetime.now()
        db.session.add(device_distribution)
    return device_distribution


@catch_except
def delete_device_distribution(imei):
    query = db.session.query(DeviceDistribution).filter(DeviceDistribution.imei==imei).\
        filter(DeviceDistribution.from_agent!=0)
    return query.delete()


@catch_except
def delete_device_distribution_total(imei):
    query = db.session.query(DeviceDistribution).filter(DeviceDistribution.imei==imei)
    return query.delete()


@catch_except
def make_new_device_distribution_salesman(device_id, imei, from_agent, to_agent):
    device_distribution_salesman = DeviceDistributionSalesman(device_id, imei, from_agent, to_agent)
    db.session.add(device_distribution_salesman)
    return device_distribution_salesman


@catch_except
def get_device_distribution_salesman(**kwargs):
    query = db.session.query(DeviceDistributionSalesman)
    if 'imei' in kwargs and 'from_agent' in kwargs:
        imei = kwargs['imei']
        from_agent = kwargs['from_agent']
        return query.filter(DeviceDistributionSalesman.imei==imei).\
            filter(DeviceDistributionSalesman.from_agent==from_agent).first()
    if 'imei' in kwargs and 'to_agent' in kwargs:
        imei = kwargs['imei']
        to_agent = kwargs['to_agent']
        return query.filter(DeviceDistributionSalesman.imei==imei).\
            filter(DeviceDistributionSalesman.to_agent==to_agent).first()
    if 'device_id' in kwargs:
        device_id = kwargs['device_id']
        return query.filter(DeviceDistributionSalesman.device_id==device_id).all()
    if 'imei' in kwargs:
        imei = kwargs['imei']
        return query.filter(DeviceDistributionSalesman.imei==imei).all()


@catch_except
def delete_device_distribution_salesman(imei):
    query = db.session.query(DeviceDistributionSalesman).filter(DeviceDistributionSalesman.imei==imei).\
        filter(DeviceDistributionSalesman.from_agent!=0)
    return query.delete()


@catch_except
def delete_device_distribution_salesman_total(imei):
    query = db.session.query(DeviceDistributionSalesman).filter(DeviceDistributionSalesman.imei==imei)
    return query.delete()


@catch_except
def make_new_device_address(agent_id, region, address):
    device_address = DeviceAddress(agent_id, region, address)
    db.session.add(device_address)
    return device_address


@catch_except
def get_device_address(**kwargs):
    query = db.session.query(DeviceAddress)
    if 'id' in kwargs:
        return query.filter(DeviceAddress.id==kwargs['id']).first()
    if 'agent_id' in kwargs:
        return query.filter(DeviceAddress.agent_id==kwargs['agent_id']).all()


@catch_except
def update_device_address(device_address, **kwargs):
    updated = False
    if 'region' in kwargs:
        device_address.region = kwargs['region']
        updated = True
    if 'address' in kwargs:
        device_address.address = kwargs['address']
        updated = True
    if updated:
        device_address.utime = datetime.now()
        db.session.add(device_address)
    return device_address


@catch_except
def make_new_device_product(device_id, product_id):
    device_product = DeviceProduct(device_id, product_id)
    db.session.add(device_product)
    return device_product


@catch_except
def delete_device_product(device_id):
    query = db.session.query(DeviceProduct).filter(DeviceProduct.device_id==device_id)
    # return delect count
    count = query.delete()
    dbg('delete_device_product: %d' % count)
    return count


@catch_except
def get_device_product(**kwargs):
    query = db.session.query(DeviceProduct)
    if 'id' in kwargs:
        return query.filter(DeviceProduct.id==kwargs['id']).first()
    if 'device_id' in kwargs:
        return query.filter(DeviceProduct.device_id==kwargs['device_id'])\
            .join(Product).filter(Product.deleted==0).all()


@catch_except
def update_device_product(device_product, **kwargs):
    updated = False
    if 'product_id' in kwargs:
        device_product.product_id = kwargs['product_id']
        updated = True
    if updated:
        device_product.utime = datetime.now()
        db.session.add(device_product)
    return device_product


@catch_except
def query_orders(start, end, psize, page, agent_id, status=None, address=None, imei=None, pay_mode=None):
    query = db.session.query(Pay, Device, DeviceAddress).join(Device, Pay.imei==Device.imei).\
        outerjoin(DeviceAddress, Device.address_id==DeviceAddress.id).\
        join(DeviceDistribution, Device.id==DeviceDistribution.device_id).\
        filter(Pay.ctime>start).filter(Pay.ctime<end).\
        filter(DeviceDistribution.to_agent==agent_id).\
        filter(Pay.deleted==0)
    if status is not None:
        # 只查成功的支付订单（微信或支付宝）
        query = query.filter(Pay.status==status).filter(Pay.pay_mode!=3)
    if address is not None:
        query = query.filter(DeviceAddress.address.like("%%%s%%" % address))
    if imei is not None:
        query = query.filter(Device.imei==imei)
    if pay_mode is not None:
        query = query.filter(Pay.pay_mode==pay_mode)
    query = query.order_by(Pay.ctime.desc())
    return query.count(), query.slice(psize*(page-1), psize*page).all()


@catch_except
def query_orders_salesman(start, end, psize, page, agent_id, status=None, address=None, imei=None, pay_mode=None):
    query = db.session.query(Pay, Device, DeviceAddress).join(Device, Pay.imei==Device.imei).\
        outerjoin(DeviceAddress, Device.address_id==DeviceAddress.id).\
        join(DeviceDistributionSalesman, Device.id==DeviceDistributionSalesman.device_id).\
        filter(Pay.ctime>start).filter(Pay.ctime<end).\
        filter(DeviceDistributionSalesman.to_agent==agent_id).\
        filter(Pay.deleted==0)
    if status is not None:
        # 只查成功的支付订单（微信或支付宝）
        query = query.filter(Pay.status==status).filter(Pay.pay_mode!=3)
    if address is not None:
        query = query.filter(DeviceAddress.address.like("%%%s%%" % address))
    if imei is not None:
        query = query.filter(Device.imei==imei)
    if pay_mode is not None:
        query = query.filter(Pay.pay_mode==pay_mode)
    query = query.order_by(Pay.ctime.desc())
    return query.count(), query.slice(psize*(page-1), psize*page).all()


@catch_except
def query_devices(start, end, psize, page, agent_id, address=None, imei=None):
    query = db.session.query(Pay.imei, Device, DeviceAddress, func.sum(Pay.total_fee).label("online_income")).\
        join(Device, Pay.imei==Device.imei).\
        join(DeviceAddress, Device.address_id==DeviceAddress.id).\
        join(DeviceDistribution, Device.id==DeviceDistribution.device_id).\
        filter(Pay.ctime>start).filter(Pay.ctime<end).\
        filter(Pay.status==1).\
        filter(Pay.deleted==0).\
        filter(DeviceDistribution.to_agent==agent_id)
    if address is not None:
        query = query.filter(DeviceAddress.address.like("%%%s%%" % address))
    if imei is not None:
        query = query.filter(Device.imei==imei)
    query = query.group_by(Pay.imei)
    return query.count(), query.slice(psize*(page-1), psize*page).all()


@catch_except
def query_devices_online_income(start, end, psize, page, agent_id, address=None, imei=None):
    query = db.session.query(Device, DeviceAddress, func.sum(Pay.total_fee).label("online_income"))
    query = query.join(DeviceAddress, Device.address_id==DeviceAddress.id).\
        join(DeviceDistribution, Device.id==DeviceDistribution.device_id).\
        filter(DeviceDistribution.to_agent==agent_id).\
        join(Pay, Device.imei==Pay.imei).\
        filter(Pay.ctime>start).filter(Pay.ctime<end).\
        filter(Pay.status==1).\
        filter(Pay.deleted==0)
    if address is not None:
        query = query.filter(DeviceAddress.address.like("%%%s%%" % address))
    if imei is not None:
        query = query.filter(Device.imei==imei)
    query = query.group_by(Device.imei)
    return query.count(), query.slice(psize*(page-1), psize*page).all()


@catch_except
def query_devices_offline_income(start, end, psize, page, agent_id, address=None, imei=None):
    query = db.session.query(Device, DeviceAddress, func.sum(OfflineCoin.coin).label("offline_coin"))
    query = query.join(DeviceAddress, Device.address_id==DeviceAddress.id).\
        join(DeviceDistribution, Device.id==DeviceDistribution.device_id).\
        filter(DeviceDistribution.to_agent==agent_id).\
        join(OfflineCoin, Device.imei==OfflineCoin.imei).\
        filter(OfflineCoin.ctime>start).filter(OfflineCoin.ctime<end)
    if address is not None:
        query = query.filter(DeviceAddress.address.like("%%%s%%" % address))
    if imei is not None:
        query = query.filter(Device.imei==imei)
    query = query.group_by(Device.imei)
    return query.count(), query.slice(psize*(page-1), psize*page).all()


# TODO 此方法极慢，需要优化！！！！
@catch_except
def query_devices_income_with_sql(start, end, page, psize, agent_id, address=None, imei=None):
    cond   = "dd.to_agent = %d" % agent_id
    p_cond = "%s and p.ctime > '%s' and p.ctime < '%s' and p.status=1 and p.deleted=0" % (cond, start, end)
    o_cond = "%s and o.ctime > '%s' and o.ctime < '%s' and d.cat=1" % (cond, start, end)
    order_sql = "order by id"
    if address is not None:
        p_cond += " and da.address like '%%%s%%'" % address
        o_cond += " and da.address like '%%%s%%'" % address
    if imei is not None:
        p_cond += " and d.imei = '%s'" % imei
        o_cond += " and d.imei = '%s'" % imei
    sql = """
        select d.id as id, d.imei as imei, d.owner_agent_id as owner_agent_id,
            d.product_min_money as product_min_money, da.address as address,
            sum(p.total_fee) as online_income, 0 as offline_coins from device d
        join device_distribution dd on d.imei=dd.imei
        left join device_address da on d.address_id=da.id
        left join pay p on d.imei=p.imei
        where %s
        group by d.imei

        union all

        select d.id as id, d.imei as imei, d.owner_agent_id as owner_agent_id,
            d.product_min_money as product_min_money, da.address as address,
            0, sum(o.coin) as offline_coins from device d
        join device_distribution dd on d.imei=dd.imei
        left join device_address da on d.address_id=da.id
        left join offline_coin o on d.imei=o.imei
        where %s
        group by d.imei
    """ % (p_cond, o_cond)

    count_sql = "select count(id) from (%s) sub" % sql
    query_sql = "%s \n %s limit %d, %d" % (sql, order_sql, psize*(page-1), psize)
    count = db.session.execute(text(count_sql)).fetchone()
    data  = db.session.execute(text(query_sql)).fetchall()
    if count:
        return count[0], data
    else:
        return 0, None


@catch_except
def query_devices_income_with_sql_salesman(start, end, page, psize, agent_id, address=None, imei=None):
    cond   = "dd.to_agent = %d" % agent_id
    p_cond = "%s and p.ctime > '%s' and p.ctime < '%s' and p.status=1 and p.deleted=0" % (cond, start, end)
    o_cond = "%s and o.ctime > '%s' and o.ctime < '%s' and d.cat=1" % (cond, start, end)
    order_sql = "order by id"
    if address is not None:
        p_cond += " and da.address like '%%%s%%'" % address
        o_cond += " and da.address like '%%%s%%'" % address
    if imei is not None:
        p_cond += " and d.imei = '%s'" % imei
        o_cond += " and d.imei = '%s'" % imei
    sql = """
        select d.id as id, d.imei as imei, d.owner_agent_id as owner_agent_id,
            d.product_min_money as product_min_money, da.address as address,
            sum(p.total_fee) as online_income, 0 as offline_coins from device d
        join device_distribution_salesman dd on d.imei=dd.imei
        left join device_address da on d.address_id=da.id
        left join pay p on d.imei=p.imei
        where %s
        group by d.imei

        union all

        select d.id as id, d.imei as imei, d.owner_agent_id as owner_agent_id,
            d.product_min_money as product_min_money, da.address as address,
            0, sum(o.coin) as offline_coins from device d
        join device_distribution_salesman dd on d.imei=dd.imei
        left join device_address da on d.address_id=da.id
        left join offline_coin o on d.imei=o.imei
        where %s
        group by d.imei
    """ % (p_cond, o_cond)

    count_sql = "select count(id) from (%s) sub" % sql
    query_sql = "%s \n %s limit %d, %d" % (sql, order_sql, psize*(page-1), psize)
    count = db.session.execute(text(count_sql)).fetchone()
    data  = db.session.execute(text(query_sql)).fetchall()
    if count:
        return count[0], data
    else:
        return 0, None


@catch_except
def fuzzy_query_device(agent_id, **kwargs):
    if 'imei' in kwargs:
        data = db.session.query(Device.imei).\
            join(DeviceDistribution, Device.id==DeviceDistribution.device_id).\
            filter(DeviceDistribution.to_agent==agent_id).\
            filter(Device.imei.like("%%%s%%" % kwargs['imei'])).limit(5).all()
        res = list(map(lambda x: x[0], data))
        return res


@catch_except
def fuzzy_query_all_device(**kwargs):
    if 'imei' in kwargs:
        data = db.session.query(Device.imei).\
            filter(Device.imei.like("%%%s%%" % kwargs['imei'])).limit(5).all()
        print(data)
        res = list(map(lambda x: x[0], data))
        return res


@catch_except
def fuzzy_query_device_address(agent_id, **kwargs):
    if 'address' in kwargs:
        data = db.session.query(DeviceAddress.address).filter(DeviceAddress.agent_id==agent_id).\
            filter(DeviceAddress.address.like("%s%%" % kwargs['address'])).limit(5).all()
        res = list(map(lambda x: x[0], data))
        return res


@catch_except
def get_daily_income(**kwargs):
    query = db.session.query(DailyIncome)
    if 'start' in kwargs and 'end' in kwargs and 'agent_id' in kwargs:
        start = kwargs['start']
        end   = kwargs['end']
        agent_id = kwargs['agent_id']
        return query.filter(DailyIncome.date>=start).\
            filter(DailyIncome.date<=end).\
            filter(DailyIncome.agent_id==agent_id).all()


@catch_except
def get_today_online_income(agent_id):
    end = datetime.now()
    start = datetime(end.year, end.month, end.day)
    query = db.session.query(func.sum(Pay.total_fee).label("online_income"))
    query = query.filter(Pay.ctime>start).filter(Pay.ctime<end).filter(Pay.agent_id==agent_id).filter(Pay.deleted==0)
    res = query.filter(Pay.status==1).filter(Pay.pay_mode!=3).first()
    online_income = res[0]
    if online_income:
        return int(online_income)
    return 0


# @catch_except
def get_today_offline_coin(agent_id):
    try:
        end = datetime.now()
        start = datetime(end.year, end.month, end.day)
        devices = db.session.query(Device).filter(Device.owner_agent_id==agent_id).\
            filter(Device.cat==1)
        coins = 0
        offline_income = 0
        for device in devices:
            offline_coin = get_offline_coin_sum(imei=device.imei, start=start, end=end)
            coins += offline_coin
            offline_income += offline_coin * device.product_min_money
        return coins, offline_income
    except:
        print_exception_info()
        return 0, 0


@catch_except
def get_today_wallet_income(user_id, role=1):
    end = datetime.now()
    start = datetime(end.year, end.month, end.day)
    query = db.session.query(func.sum(WalletReceipt.receipt).label("wallet_income"))
    query = query.filter(WalletReceipt.ctime>start).filter(WalletReceipt.ctime<end).\
        filter(WalletReceipt.user_id==user_id).filter(WalletReceipt.role==role).\
        filter(WalletReceipt.trade_type!=WALLET_TRADE_TYPE_WECHAT_WITHDRAW)
    res = query.first()
    wallet_income = res[0]
    if wallet_income:
        return int(wallet_income)
    return 0


@catch_except
def make_new_agent_setting(agent_id, min_withdraw=config.MIN_WTIHDRAW, l1=config.L1,
        l2=config.L2, l3=config.L3, withdraw_fee=config.WITHDRAW_FEE, wallet_pay_enable=1):
    agent_setting = AgentSetting(agent_id, min_withdraw, l1, l2, l3, withdraw_fee, wallet_pay_enable)
    db.session.add(agent_setting)
    return agent_setting


@catch_except
def get_agent_setting(**kwargs):
    query = db.session.query(AgentSetting)
    if 'id' in kwargs:
        return query.filter(AgentSetting.id==kwargs['id']).first()
    if 'agent_id' in kwargs:
        return query.filter(AgentSetting.agent_id==kwargs['agent_id']).first()


@catch_except
def update_agent_setting(agent_setting, **kwargs):
    updated = False
    if 'min_withdraw' in kwargs:
        agent_setting.min_withdraw = kwargs['min_withdraw']
        updated = True
    if 'l1' in kwargs:
        agent_setting.l1 = kwargs['l1']
        updated = True
    if 'l2' in kwargs:
        agent_setting.l2 = kwargs['l2']
        updated = True
    if 'l3' in kwargs:
        agent_setting.l3 = kwargs['l3']
        updated = True
    if 'withdraw_fee' in kwargs:
        agent_setting.withdraw_fee = kwargs['withdraw_fee']
        updated = True
    if 'wallet_pay_enable' in kwargs:
        agent_setting.wallet_pay_enable = kwargs['wallet_pay_enable']
        updated = True
    if 'trans_url' in kwargs:
        agent_setting.trans_url = kwargs['trans_url']
        updated = True
    if updated:
        agent_setting.utime = datetime.now()
        db.session.add(agent_setting)
    return agent_setting


@catch_except
def make_new_wallet(user_id, role, agent_id):
    wallet = Wallet(user_id, role, agent_id)
    db.session.add(wallet)
    return wallet


@catch_except
def update_wallet(wallet, **kwargs):
    updated = False
    if 'balance' in kwargs:
        wallet.balance = kwargs['balance']
        updated = True
    if 'withdrawable_balance' in kwargs:
        wallet.withdrawable_balance = kwargs['withdrawable_balance']
        updated = True
    if updated:
        wallet.utime = datetime.now()
        db.session.add(wallet)
    return wallet


@catch_except
def get_wallet(role=1, **kwargs):
    kwargs['role'] = role
    query = db.session.query(Wallet)
    if 'id' in kwargs:
            return query.filter(Wallet.id==kwargs['id']).first()
    if role == 0:
        if 'user_id' in kwargs and 'agent_id' in kwargs and role is not None:
            user_id = kwargs['user_id']
            agent_id = kwargs['agent_id']
            role = kwargs['role']
            wallet = query.filter(Wallet.user_id==user_id).\
                filter(Wallet.role==role).\
                filter(Wallet.agent_id==agent_id).first()
            if not wallet:
                wallet = make_new_wallet(user_id, role, agent_id)
                db.session.commit()
            return wallet
    elif role == 1:
        if 'user_id' in kwargs:
            user_id = kwargs['user_id']
            agent_id = kwargs.get('agent_id') or 0  # agent_id在代理钱包里，暂时没有作用
            wallet = query.filter(Wallet.user_id==user_id).\
                filter(Wallet.role==role).first()
            if not wallet:
                wallet = make_new_wallet(user_id, role, agent_id)
                db.session.commit()
            return wallet


@catch_except
def make_new_wallet_receipt(user_id, agent_id, wallet_id, trade_type, receipt,
        withdrawable_receipt, remark, payment_no='--', role=1):
    wallet_receipt = WalletReceipt(role, user_id, agent_id, wallet_id, trade_type,
        receipt, withdrawable_receipt, remark, payment_no)
    db.session.add(wallet_receipt)
    return wallet_receipt


@catch_except
def get_wallet_receipt(role=1, **kwargs):
    kwargs['role'] = role
    query = db.session.query(WalletReceipt)
    if 'no_zero' in kwargs:
        query = query.filter(or_(WalletReceipt.receipt>=1, WalletReceipt.receipt<=-1))
    if 'trade_type' in kwargs:
        query = query.filter(WalletReceipt.trade_type==trade_type)
    if 'id' in kwargs:
        return query.filter(WalletReceipt.id==kwargs['id']).first()
    if 'user_id' in kwargs and 'agent_id' in kwargs and 'page' in kwargs and 'psize' in kwargs:
        user_id = kwargs['user_id']
        agent_id = kwargs['agent_id']
        role = kwargs['role']
        page = kwargs['page']
        psize = kwargs['psize']
        query = query.filter(WalletReceipt.user_id==user_id).\
            filter(WalletReceipt.role==role).filter(WalletReceipt.agent_id==agent_id).order_by(WalletReceipt.id.desc())
        return query.count(), query.slice(psize*(page-1), psize*page).all()


@catch_except
def get_agent_wallet_receipt_sum(wallet_id):
    type_list = (WALLET_TRADE_TYPE_TICHENG, WALLET_TRADE_TYPE_REFUND_TICHENG)
    query = db.session.query(func.sum(WalletReceipt.receipt).label("receipt_sum")).\
        filter(WalletReceipt.wallet_id==wallet_id).filter(WalletReceipt.trade_type.in_(type_list))
    receipt_sum = query.first()
    if receipt_sum:
        return int(receipt_sum[0])
    else:
        return 0


@catch_except
def make_new_pay_to_user(wechat_agent_id, user_id, to_openid, to_nickname, trade_no,
        total_fee, desc, remark):
    pay_to_user = PayToUser(wechat_agent_id, user_id, to_openid, to_nickname, trade_no,
        total_fee, desc, remark)
    db.session.add(pay_to_user)
    return pay_to_user


@catch_except
def update_pay_to_user(pay_to_user, **kwargs):
    updated = False
    if 'payment_no' in kwargs:
        pay_to_user.payment_no = kwargs['payment_no']
        updated = True
    if 'notify_res' in kwargs:
        pay_to_user.notify_res = kwargs['notify_res']
        updated = True
    if 'status' in kwargs:
        pay_to_user.status = kwargs['status']
        updated = True
    if updated:
        pay_to_user.utime = datetime.now()
        db.session.add(pay_to_user)
    return pay_to_user


@catch_except
def get_max_pay_to_user_id():
    res = db.session.query(PayToUser.id).order_by(PayToUser.id.desc()).first()
    if res and isinstance(res, tuple):
        return res[0]
    return 1


@catch_except
def get_pay_to_user(**kwargs):
    query = db.session.query(PayToUser).filter(PayToUser.status==1)

    # 筛选
    if 'status' in kwargs:
        query = query.filter(PayToUser.status==status)

    # 单条查询
    if 'id' in kwargs:
        return query.filter(PayToUser.id==kwargs['id']).first()

    # 特殊查询
    if 'total' in kwargs and 'user_id' in kwargs:
        user_id = kwargs['user_id']
        query = db.session.query(func.sum(PayToUser.total_fee).label("total_fee_sum")).\
            filter(PayToUser.openluat_user_id==user_id).filter(PayToUser.status==1)
        total_fee_sum = query.first()
        if total_fee_sum and total_fee_sum[0]:
            return int(total_fee_sum[0])
        else:
            return 0

    # 多条查询
    if 'user_id' in kwargs:
        user_id = kwargs['user_id']
        query = query.filter(PayToUser.openluat_user_id==user_id).order_by(PayToUser.id.desc())
    if 'wechat_agent_id' in kwargs:
        wechat_agent_id = kwargs['wechat_agent_id']
        query = query.filter(PayToUser.wechat_agent_id==wechat_agent_id).order_by(PayToUser.id.desc())

    # 是否分页
    if 'page' in kwargs and 'psize' in kwargs:
        page = kwargs['page']
        psize = kwargs['psize']
        return query.count(), query.slice(psize*(page-1), psize*page).all()
    else:
        return query.all()


@catch_except
def make_new_offline_coin(imei, coin_time, coin):
    offline_coin = OfflineCoin(imei, coin_time, coin)
    db.session.add(offline_coin)
    return offline_coin


@catch_except
def get_offline_coin(**kwargs):
    query = db.session.query(OfflineCoin)
    if 'start' in kwargs:
        query = query.filter(OfflineCoin.time>=kwargs['start'])
    if 'end' in kwargs:
        query = query.filter(OfflineCoin.time<=kwargs['end'])
    if 'id' in kwargs:
        return query.filter(OfflineCoin.id==kwargs['id']).first()
    if 'imei' in kwargs and 'page' in kwargs and 'psize' in kwargs:
        imei = kwargs['imei']
        page = kwargs['page']
        psize = kwargs['psize']
        query = query.filter(OfflineCoin.imei==imei)
        return query.count(), query.slice(psize*(page-1), psize*page).all()


@catch_except
def get_offline_coin_sum(**kwargs):
    query = db.session.query(func.sum(OfflineCoin.coin).label("offline_coin"))
    if 'start' in kwargs:
        query = query.filter(OfflineCoin.time>=kwargs['start'])
    if 'end' in kwargs:
        query = query.filter(OfflineCoin.time<=kwargs['end'])
    if 'imei' in kwargs:
        query = query.filter(OfflineCoin.imei==kwargs['imei'])
    if 'agent_id' in kwargs:
        agent_id = kwargs['agent_id']
        query = query.join(Device, OfflineCoin.imei==Device.imei).\
        join(DeviceDistribution, Device.id==DeviceDistribution.device_id).\
        filter(DeviceDistribution.to_agent==agent_id)
    res = query.first()
    offline_coin = res[0]
    if offline_coin:
        return int(offline_coin)
    return 0


@catch_except
def make_new_mqtt_async(greenlet_id, http_url):
    mqtt_async = MqttAsync(int(greenlet_id), http_url)
    db.session.add(mqtt_async)
    return mqtt_async


@catch_except
def get_mqtt_async(**kwargs):
    query = db.session.query(MqttAsync)
    if 'id' in kwargs:
        return query.filter(MqttAsync.id==kwargs['id']).first()
    if 'greenlet_id' in kwargs:
        return query.filter(MqttAsync.greenlet_id==kwargs['greenlet_id']).first()


@catch_except
def update_mqtt_async(mqtt_async, **kwargs):
    updated = False
    if 'mqtt_res' in kwargs:
        mqtt_async.mqtt_res = kwargs['mqtt_res']
        updated = True
    if 'http_res' in kwargs:
        mqtt_async.http_res = kwargs['http_res']
        updated = True
    if 'status' in kwargs:
        mqtt_async.status = kwargs['status']
        updated = True
    if updated:
        mqtt_async.utime = datetime.now()
        db.session.add(mqtt_async)
    return mqtt_async


@catch_except
def get_device_latestreport(imei):
    try:
        fields = 'a.imei, a.lng, a.lat, a.`signal`, a.satellites, a.time'
        sql = """SELECT %s FROM latestreport a where imei = '%s'
            AND a.`time` = (select max(`time`) from latestreport where imei = a.imei)""" % (fields, imei)
        res = db_session.execute(text(sql)).fetchone()
        keys = ('imei', 'lng', 'lat', 'signal', 'satellites', 'time')
        if res:
            values = res
            dic = dict(zip(keys, values))
            return dic
        else:
            return {}
    except:
        raise
    finally:
        db_session.remove()


@catch_except
def get_cws_device_iccid(imei):
    try:
        fields = 'imei, iccid'
        sql = """SELECT %s FROM devices where imei = '%s' """ % (fields, imei)
        res = db_session.execute(text(sql)).fetchone()
        keys = ('imei', 'iccid')
        if res:
            values = res
            dic = dict(zip(keys, values))
            return dic
        else:
            return {}
    except:
        raise
    finally:
        db_session.remove()


@catch_except
def make_new_god(openluat_user_id, name, phone, email, remark, role=1):
    god = God(openluat_user_id, role, name, phone, email, remark)
    db.session.add(god)
    return god


@catch_except
def get_god(**kwargs):
    query = db.session.query(God)
    if 'super' in kwargs:
        return query.first()
    if 'id' in kwargs:
        return query.filter(God.id==kwargs['id']).first()
    if 'openluat_user_id' in kwargs:
        return query.filter(God.openluat_user_id==kwargs['openluat_user_id']).first()
    if 'phone' in kwargs:
        return query.filter(God.phone==kwargs['phone']).first()
    if 'email' in kwargs:
        return query.filter(God.email==kwargs['email']).first()
    if 'role' in kwargs and 'page' in kwargs and 'psize' in kwargs:
        role = kwargs['role']
        page = kwargs['page']
        psize = kwargs['psize']
        query = query.filter(God.role==role)
        return query.count(), query.slice(psize*(page-1), psize*page).all()


@catch_except
def make_new_god_agent(god_id, agent_id):
    god_agent = GodAgent(god_id, agent_id)
    db.session.add(god_agent)
    return god_agent


@catch_except
def get_god_agent(**kwargs):
    query = db.session.query(GodAgent)

    # 单条查询
    if 'agent_id' in kwargs:
        return query.filter(GodAgent.agent_id==kwargs['agent_id']).first()

    # 多条查询
    if 'god_id' in kwargs:
        god_id = kwargs['god_id']
        query = query.filter(GodAgent.god_id==god_id)

    # 是否分页
    if 'page' in kwargs and 'psize' in kwargs:
        page = kwargs['page']
        psize = kwargs['psize']
        return query.count(), query.slice(psize*(page-1), psize*page).all()
    else:
        return query.all()


@catch_except
def make_new_agent_wechat(agent_id, wechat_config_id=1):
    agent_wechat = AgentWechat(agent_id, wechat_config_id)
    db.session.add(agent_wechat)
    return agent_wechat


@catch_except
def get_agent_wechat(**kwargs):
    query = db.session.query(AgentWechat)
    if 'id' in kwargs:
        return query.filter(AgentWechat.id==kwargs['id']).first()
    if 'agent_id' in kwargs:
        return query.filter(AgentWechat.agent_id==kwargs['agent_id']).first()
    if 'wechat_config_id' in kwargs and 'min' in kwargs:
        return query.filter(AgentWechat.wechat_config_id==kwargs['wechat_config_id']).\
            order_by(AgentWechat.agent_id).first()


@catch_except
def update_agent_wechat(agent_id, wechat_config_id):
    agent_wechat = get_agent_wechat(agent_id=agent_id)
    if not agent_wechat:
        agent_wechat = make_new_agent_wechat(agent_id, wechat_config_id)
    else:
        agent_wechat.wechat_config_id = wechat_config_id
        agent_wechat.utime = datetime.now()
        db.session.add(agent_wechat)
    return agent_wechat


@catch_except
def make_new_wechat_config(name, appid, appsecret, mchid, mchkey,
    redirecturl, redirect_bind_url, key_path, qrcode_img):
    wechat_config = WechatConfig(name, appid, appsecret, mchid, mchkey,
        redirecturl, redirect_bind_url, key_path, qrcode_img)
    db.session.add(wechat_config)
    return wechat_config


@catch_except
def get_wechat_config(**kwargs):
    query = db.session.query(WechatConfig)
    if 'id' in kwargs:
        wechat_config = query.filter(WechatConfig.id==kwargs['id']).first()
    if 'appid' in kwargs:
        wechat_config = query.filter(WechatConfig.appid==kwargs['appid']).first()
    if 'agent_id' in kwargs:
        agent_id = kwargs['agent_id']
        agent_wechat = get_agent_wechat(agent_id=agent_id)
        if not agent_wechat:
            agent_wechat = make_new_agent_wechat(agent_id)
        wechat_config = query.filter(WechatConfig.id==agent_wechat.wechat_config_id).first()
    if 'imei' in kwargs:
        imei = kwargs['imei']
        device = get_device(imei=imei)
        if not device:
            return None
        agent_id = device.agent_id
        agent_wechat = get_agent_wechat(agent_id=agent_id)
        if not agent_wechat:
            agent_wechat = make_new_agent_wechat(agent_id)
        wechat_config = query.filter(WechatConfig.id==agent_wechat.wechat_config_id).first()

    return wechat_config


@catch_except
def make_new_wechat_bind(admin_uid, expires_at):
    wechat_bind = WechatBind(admin_uid, expires_at)
    db.session.add(wechat_bind)
    return wechat_bind


@catch_except
def get_wechat_bind(**kwargs):
    query = db.session.query(WechatBind)
    if 'id' in kwargs:
        return query.filter(WechatBind.id==kwargs['id']).first()
    if 'admin_uid' in kwargs:
        admin_uid = kwargs['admin_uid']
        return query.filter(WechatBind.admin_uid==admin_uid).first()


@catch_except
def update_wechat_bind(wechat_bind, **kwargs):
    updated = False
    if 'expires_at' in kwargs:
        wechat_bind.expires_at = kwargs['expires_at']
        updated = True
    if 'status' in kwargs:
        wechat_bind.status = kwargs['status']
        updated = True
    if updated:
        wechat_bind.utime = datetime.now()
    db.session.add(wechat_bind)
    return wechat_bind


@catch_except
def make_new_ali_user(user_id, user_id_a, ali_user_id):
    ali_user = AliUser(user_id, user_id_a, ali_user_id)
    db.session.add(ali_user)
    return ali_user


@catch_except
def get_ali_user(**kwargs):
    query = db.session.query(AliUser)
    if 'id' in kwargs:
        return query.filter(AliUser.id==kwargs['id']).first()
    if 'user_id' in kwargs:
        return query.filter(AliUser.user_id==kwargs['user_id']).first()
    if 'ali_user_id' in kwargs:
        return query.filter(AliUser.ali_user_id==kwargs['ali_user_id']).first()


@catch_except
def make_new_ali_config(name, appid, priv_path, pub_path):
    ali_config = AliConfig(name, appid, priv_path, pub_path)
    db.session.add(ali_config)
    return ali_config


@catch_except
def get_ali_config(**kwargs):
    query = db.session.query(AliConfig)
    if 'id' in kwargs:
        return query.filter(AliConfig.id==kwargs['id']).first()
    if 'appid' in kwargs:
        return query.filter(AliConfig.appid==kwargs['appid']).first()
    if 'agent_id' in kwargs:
        agent_id = kwargs['agent_id']
        agent_ali = get_agent_ali(agent_id=agent_id)
        if not agent_ali:
            agent_ali = make_new_agent_ali(agent_id)
        return query.filter(AliConfig.id==agent_ali.ali_config_id).first()
    if 'imei' in kwargs:
        imei = kwargs['imei']
        device = get_device(imei=imei)
        if not device:
            return None
        agent_id = device.agent_id
        agent_ali = get_agent_ali(agent_id=agent_id)
        if not agent_ali:
            agent_ali = make_new_agent_ali(agent_id)
        return query.filter(AliConfig.id==agent_ali.ali_config_id).first()


@catch_except
def make_new_agent_ali(agent_id, ali_config_id=1):
    agent_ali = AgentAli(agent_id, ali_config_id)
    db.session.add(agent_ali)
    return agent_ali


@catch_except
def get_agent_ali(**kwargs):
    query = db.session.query(AgentAli)
    if 'id' in kwargs:
        return query.filter(AgentAli.id==kwargs['id']).first()
    if 'agent_id' in kwargs:
        return query.filter(AgentAli.agent_id==kwargs['agent_id']).first()
    if 'ali_config_id' in kwargs and 'min' in kwargs:
        return query.filter(AgentAli.ali_config_id==kwargs['ali_config_id']).\
            order_by(AgentAli.agent_id).first()


@catch_except
def update_agent_ali(agent_id, ali_config_id):
    agent_ali = get_agent_ali(agent_id=agent_id)
    if not agent_ali:
        agent_ali = make_new_agent_ali(agent_id, ali_config_id)
    else:
        agent_ali.ali_config_id = ali_config_id
        agent_ali.utime = datetime.now()
        db.session.add(agent_ali)
    return agent_ali


@catch_except
def make_new_user_start_counter(user_id, imei):
    user_start_counter = UserStartCounter(user_id, imei)
    db.session.add(user_start_counter)
    return user_start_counter


@catch_except
def get_user_start_counter(**kwargs):
    query = db.session.query(UserStartCounter)
    if 'id' in kwargs:
        return query.filter(UserStartCounter.id==kwargs['id']).first()
    if 'user_id' in kwargs and 'imei' in kwargs:
        user_id = kwargs['user_id']
        imei    = kwargs['imei']
        return query.filter(UserStartCounter.user_id==user_id).\
            filter(UserStartCounter.imei==imei).first()

    if 'user_id' in kwargs and 'address_id' in kwargs:
        user_id = kwargs['user_id']
        address_id = kwargs['address_id']
        return query.filter(UserStartCounter.user_id==user_id).\
            join(Device, Device.imei==UserStartCounter.imei).\
            filter(Device.address_id==address_id).all()


@catch_except
def update_user_counter(user_start_counter, **kwargs):
    if 'count' in kwargs:
        user_start_counter.count = kwargs['count']
        user_start_counter.utime = datetime.now()
        db.session.add(user_start_counter)
    return user_start_counter


@catch_except
def make_new_ad(agent_id, name, desc, img, url):
    ad = Advertisement(agent_id, name, desc, img, url)
    db.session.add(ad)
    return ad


@catch_except
def get_ad(**kwargs):
    query = db.session.query(Advertisement).filter(Advertisement.deleted==0)
    if 'using' in kwargs:
        query = query.filter(Advertisement.using==1)
    if 'id' in kwargs:
        return query.filter(Advertisement.id==kwargs['id']).first()
    if 'agent_id' in kwargs:
        agent_id = kwargs['agent_id']
        return query.filter(Advertisement.agent_id==agent_id).all()
    if 'imei' in kwargs:
        imei = kwargs['imei']
        return query.join(DeviceAd).join(Device).\
            filter(Device.imei==imei).all()


@catch_except
def update_ad(ad, **kwargs):
    updated = False
    if 'name' in kwargs:
        ad.name = kwargs['name']
        updated = True
    if 'desc' in kwargs:
        ad.desc = kwargs['desc']
        updated = True
    if 'img' in kwargs:
        ad.img = kwargs['img']
        updated = True
    if 'url' in kwargs:
        ad.url = kwargs['url']
        updated = True
    if 'using' in kwargs:
        ad.using = kwargs['using']
        updated = True
    if 'deleted' in kwargs:
        ad.deleted = kwargs['deleted']
        updated = True
    if updated:
        ad.utime = datetime.now()
        db.session.add(ad)
    return ad


@catch_except
def make_new_device_ad(device_id, ad_id):
    device_ad = DeviceAd(device_id, ad_id)
    db.session.add(device_ad)
    return device_ad


@catch_except
def delete_device_ad(device_id):
    query = db.session.query(DeviceAd).filter(DeviceAd.device_id==device_id)
    # return delect count
    return query.delete()


@catch_except
def make_new_advertiser(openluat_user_id, hook_agent_id, name, phone, email, desc, address, remark):
    advertiser = Advertiser(openluat_user_id, hook_agent_id, name, phone, email, desc, address, remark)
    db.session.add(advertiser)
    return advertiser


@catch_except
def get_advertiser(**kwargs):
    query = db.session.query(Advertiser)

    # 单挑查询
    if 'id' in kwargs:
        return query.filter(Advertiser.id==kwargs['id']).first()
    if 'user_id' in kwargs:
        return query.filter(Advertiser.openluat_user_id==kwargs['user_id']).first()
    if 'phone' in kwargs:
        return query.filter(Advertiser.phone==kwargs['phone']).first()

    # 多条查询
    if 'hook_agent_id' in kwargs:
        query = query.filter(Advertiser.hook_agent_id==kwargs['hook_agent_id'])

    # 是否分页
    if 'page' in kwargs and 'psize' in kwargs:
        page = kwargs['page']
        psize = kwargs['psize']
        return query.count(), query.slice(psize*(page-1), psize*page).all()
    else:
        return query.all()


@catch_except
def update_advertiser(advertiser, **kwargs):
    if 'desc' in kwargs:
        advertiser.desc = kwargs['desc']
    if 'address' in kwargs:
        advertiser.address = kwargs['address']
    if 'remark' in kwargs:
        advertiser.remark = kwargs['remark']

    db.session.add(advertiser)
    return advertiser


@catch_except
def make_new_coupon(agent_id, advertiser_id, product_id, pay_id, title, desc, prefix, total, img):
    coupon = Coupon(agent_id, advertiser_id, product_id, pay_id, title, desc, prefix, total, img)
    db.session.add(coupon)
    return coupon


@catch_except
def get_coupon(**kwargs):
    query = db.session.query(Coupon)

    # 筛选
    if 'paid' in kwargs:
        query = query.filter(Coupon.paid==kwargs['paid'])
    if 'inventory' in kwargs:
        query = query.join(Product).filter(Product.inventory>0)

    # 单条数据查询
    if 'id' in kwargs:
        return query.filter(Coupon.id==kwargs['id']).first()
    if 'prefix' in kwargs:
        return query.filter(Coupon.prefix==kwargs['prefix']).first()
    if 'pay_id' in kwargs:
        return query.filter(Coupon.pay_id==kwargs['pay_id']).first()

    # 多条数据查询
    if 'agent_id' in kwargs:
        query = query.filter(Coupon.agent_id==kwargs['agent_id'])
    if 'advertiser_id' in kwargs:
        query = query.filter(Coupon.advertiser_id==kwargs['advertiser_id'])
    if 'device_id' in kwargs:
        query = query.join(DeviceCoupon).filter(DeviceCoupon.device_id==kwargs['device_id'])

    # 是否分页
    if 'page' in kwargs and 'psize' in kwargs:
        page = kwargs['page']
        psize = kwargs['psize']
        return query.count(), query.slice(psize*(page-1), psize*page).all()
    else:
        return query.all()


@catch_except
def update_coupon(coupon, **kwargs):
    if 'paid' in kwargs:
        coupon.paid = kwargs['paid']
    if 'title' in kwargs:
        coupon.title = kwargs['title']
    if 'desc' in kwargs:
        coupon.desc = kwargs['desc']
    if 'img' in kwargs:
        coupon.img = kwargs['img']

    db.session.add(coupon)
    return coupon


@catch_except
def make_new_coupon_receipt(coupon_id, user_id, code):
    coupon_receipt = CouponReceipt(coupon_id, user_id, code)
    db.session.add(coupon_receipt)
    return coupon_receipt


@catch_except
def get_coupon_receipt(**kwargs):
    query = db.session.query(CouponReceipt)

    # 单条数据查询
    if 'id' in kwargs:
        return query.filter(CouponReceipt.id==kwargs['id']).first()
    if 'code' in kwargs:
        return query.filter(CouponReceipt.code==kwargs['code']).first()

    # 多条数据查询
    if 'coupon_id' in kwargs:
        query = query.filter(CouponReceipt.coupon_id==kwargs['coupon_id'])
    if 'user_id' in kwargs and 'device_id' in kwargs:
        query = query.join(DeviceCoupon, DeviceCoupon.coupon_id==CouponReceipt.coupon_id).\
            filter(DeviceCoupon.device_id==kwargs['device_id']).\
            filter(CouponReceipt.user_id==kwargs['user_id'])

    # 是否分页
    if 'page' in kwargs and 'psize' in kwargs:
        page = kwargs['page']
        psize = kwargs['psize']
        return query.count(), query.slice(psize*(page-1), psize*page).all()
    else:
        return query.all()


@catch_except
def update_coupon_receipt(coupon_receipt, **kwargs):
    if 'started' in kwargs:
        coupon_receipt.started = kwargs['started']
    if 'used' in kwargs:
        coupon_receipt.used = kwargs['used']
    db.session.add(coupon_receipt)
    return coupon_receipt


@catch_except
def make_new_device_coupon(coupon_id, device_id):
    device_coupon = DeviceCoupon(coupon_id, device_id)
    db.session.add(device_coupon)
    return device_coupon


@catch_except
def get_device_coupon(**kwargs):
    query = db.session.query(DeviceCoupon)

    # 单条数据查询
    if 'id' in kwargs:
        return query.filter(DeviceCoupon.id==kwargs['id']).first()
    if 'coupon_id' in kwargs and 'device_id' in kwargs:
        return query.filter(DeviceCoupon.coupon_id==kwargs['coupon_id']).\
            filter(DeviceCoupon.device_id==kwargs['device_id']).first()

    # 多条数据查询
    if 'coupon_id' in kwargs:
        query = query.filter(DeviceCoupon.coupon_id==kwargs['coupon_id'])
    if 'device_id' in kwargs:
        query = query.filter(DeviceCoupon.device_id==kwargs['device_id'])

    # 是否分页
    if 'page' in kwargs and 'psize' in kwargs:
        page = kwargs['page']
        psize = kwargs['psize']
        return query.count(), query.slice(psize*(page-1), psize*page).all()
    else:
        return query.all()


@catch_except
def make_new_god_info(god_id, logo=config.DEFAULT_LOGO, title=config.DEFAULT_TITLE):
    god_info = GodInfo(god_id, logo, title)
    db.session.add(god_info)
    return god_info


@catch_except
def get_god_info(**kwargs):
    query = db.session.query(GodInfo)

    # 单条查询
    if 'id' in kwargs:
        return query.filter(GodInfo.id==kwargs['id']).first()
    if 'god_id' in kwargs:
        return query.filter(GodInfo.god_id==kwargs['god_id']).first()


@catch_except
def update_god_info(god_info, **kwargs):
    if 'logo' in kwargs:
        god_info.logo = kwargs['logo']
    if 'title' in kwargs:
        god_info.title = kwargs['title']
    db.session.add(god_info)
    return god_info


@catch_except
def make_new_agent_info(agent_id, logo=config.DEFAULT_LOGO, title=config.DEFAULT_TITLE):
    agent_info = AgentInfo(agent_id, logo, title)
    db.session.add(agent_info)
    return agent_info


@catch_except
def get_agent_info(**kwargs):
    query = db.session.query(AgentInfo)

    # 单条查询
    if 'id' in kwargs:
        return query.filter(AgentInfo.id==kwargs['id']).first()
    if 'agent_id' in kwargs:
        return query.filter(AgentInfo.agent_id==kwargs['agent_id']).first()


@catch_except
def update_agent_info(agent_info, **kwargs):
    if 'logo' in kwargs:
        agent_info.logo = kwargs['logo']
    if 'title' in kwargs:
        agent_info.title = kwargs['title']
    db.session.add(agent_info)
    return agent_info