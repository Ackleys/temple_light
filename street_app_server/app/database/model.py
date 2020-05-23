#!/usr/bin/env python3
# coding: utf8
# 20170220 anChaOs

import json

from datetime import datetime, timedelta
# from sqlalchemy import Column, Integer, String, DateTime, Text

from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

from sqlalchemy.sql import func

from app import db, lm
from config import config

from app.tool import dbg                    # for print
from app.tool import print_exception_info   # for traceback

def to_dict(self):
    return {c.name: getattr(self, c.name, None) for c in self.__table__.db.Columns}
    # d = {}
    # for c in self.__table__.db.Columns:
    #     attr = getattr(self, c.name, None)
    #     d[c.name] = attr
    #     if isinstance(attr, db.DateTime):
    #         d[c.name] = int(attr.timestamp())

    #     # 检查是否是json 字符串
    #     try:
    #         data = json.loads(d[c.name])
    #         if isinstance(data, dict) or isinstance(data, list):
    #             d[c.name[1:]] = data
    #     except:
    #         continue

    # if 'pswd_h' in d:
    #     d.pop('pswd_h')
    # return d


db.Model.to_dict = to_dict


"""
    @ 用户表
    roll    角色：0玩家，1商家，2销售员，3总代理，4总部
    belong  所属：当roll为0时，该字段表示所属的代理，默认值为1。为0表示非玩家
"""
class User(db.Model, UserMixin):
    __tablename__ = 'mafu_user'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(24), nullable=False)
    phone       = db.Column(db.String(24), nullable=False)
    email       = db.Column(db.String(64), nullable=False)
    pswd_h      = db.Column(db.String(128), nullable=False)     # password_hash
    roll        = db.Column(db.Integer, nullable=False, server_default="0")
    nickname    = db.Column(db.String(128), nullable=True, server_default="")
    sex         = db.Column(db.String(1), nullable=False, server_default="0")
    province    = db.Column(db.String(64), nullable=False, server_default="")
    city        = db.Column(db.String(64), nullable=False, server_default="")
    country     = db.Column(db.String(64), nullable=False, server_default="")
    headimgurl  = db.Column(db.String(512), nullable=False, server_default="")
    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, name, phone, email, password, roll, wechat_body=None):
        self.name = name
        self.phone = phone
        self.email = email
        self.pswd_h = generate_password_hash(password)
        self.roll = roll
        if wechat_body and isinstance(wechat_body, dict):
            self.nickname = wechat_body.get('nickname', '')
            self.sex = wechat_body.get('sex', '')
            self.province = wechat_body.get('province', '')
            self.city = wechat_body.get('city', '')
            self.country = wechat_body.get('country', '')
            self.headimgurl = wechat_body.get('headimgurl', '')
        now = datetime.now()
        self.ctime = now
        self.utime = now
        self.status = 0

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.pswd_h = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.pswd_h, password)

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.name


"""
    @ openluat用户表
"""
DEFAULT_ROLE = '000000000000'
class OpenLuatUser(UserMixin, db.Model):
    __tablename__ = 'user'  
    __bind_key__ = 'openluat_users'
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(24), unique = True, index = True, nullable = False)
    phone = db.Column(db.String(24), unique = True, nullable = False)
    email = db.Column(db.String(64), unique = True, index = True, nullable = False)
    role = db.Column(db.String(32), nullable = False)
    password_hash = db.Column(db.String(128), nullable = False)
    creation_time = db.Column(db.DateTime, nullable = False)
    last_login_time = db.Column(db.DateTime, nullable = False)
    creator_id = db.Column(db.Integer, nullable = False, server_default="0")
    nickname = db.Column(db.String(24), nullable = False, server_default="")
    address = db.Column(db.String(32), nullable = False, server_default="")
    gender = db.Column(db.Integer, nullable = False, server_default="0")
    birthday = db.Column(db.DateTime, nullable = False, server_default="2017-01-01 00:00:00")
    
    # sim
    company = db.Column(db.String(24), nullable = False, server_default="")
    qq = db.Column(db.String(12), nullable = False, server_default="")
    wangwang = db.Column(db.String(12), nullable = False, server_default="")
    salesman = db.Column(db.String(12), nullable = False, server_default="")
    
    # imei order
    invoice_company = db.Column(db.String(24), nullable = False, server_default="")
    bank = db.Column(db.String(32), nullable = False, server_default="")
    bank_account = db.Column(db.String(32), nullable = False, server_default="")
    tax_number = db.Column(db.String(32), nullable = False, server_default="")
    fixed_phone = db.Column(db.String(24), nullable = False, server_default="")
    shipping_address = db.Column(db.String(32), nullable = False, server_default="")
    recipient = db.Column(db.String(32), nullable = False, server_default="")
    recipient_phone = db.Column(db.String(24), nullable = False, server_default="")
    
    # @staticmethod
    def __init__(self, **kwargs):
        super(OpenLuatUser, self).__init__(**kwargs)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
        
    def get_id(self):
        return self.id
        
    def get_name(self):
        return self.name

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<OpenLuatUser %r>' % self.name


@lm.user_loader
def load_user(user_id):
    return OpenLuatUser.query.get(int(user_id))


"""
    @ 用户表
    admin_uid   管理员openluat用户id：仅对代理商管理员有效, 0表示不是代理商
"""
class WechatUser(db.Model):
    __tablename__ = 'wechat_user'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.ForeignKey(u'mafu_user.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    admin_uid   = db.Column(db.Integer, nullable=False, server_default='0')
    openid      = db.Column(db.String(256), index=True, nullable=False, server_default="")
    unionid     = db.Column(db.String(256), index=True, nullable=False, server_default="")
    nickname    = db.Column(db.String(128), nullable=True, server_default="")
    sex         = db.Column(db.String(1), nullable=False, server_default="0")
    province    = db.Column(db.String(64), nullable=False, server_default="")
    city        = db.Column(db.String(64), nullable=False, server_default="")
    country     = db.Column(db.String(64), nullable=False, server_default="")
    headimgurl  = db.Column(db.String(512), nullable=False, server_default="")
    privilege   = db.Column(db.Text, nullable=False)
    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, body):
        self.user_id = body['user_id']
        self.admin_uid = body['admin_uid']
        self.openid = body['openid']
        self.unionid = body.get('unionid', '')
        self.nickname = body.get('nickname', '')
        self.sex = body.get('sex', '')
        self.province = body.get('province', '')
        self.city = body.get('city', '')
        self.country = body.get('country', '')
        self.headimgurl = body.get('headimgurl', '')
        if isinstance(body.get('privilege', ''), list):
            body['privilege'] = json.dumps(body['privilege'])
        self.privilege = body.get('privilege', '')
        dt = datetime.now()
        self.utime = dt
        self.ctime = dt
        self.status = 0

    def __repr__(self):
        return '<WechatUser %r>' % self.nickname


class AplyAgent(db.Model):
    __tablename__ = 'aply_agent'

    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey(u'mafu_user.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    hookid  = db.Column(db.ForeignKey(u'agent.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    name    = db.Column(db.String(32), nullable=False)
    phone   = db.Column(db.String(24), nullable=False)
    desc    = db.Column(db.String(128), nullable=False)

    ctime   = db.Column(db.DateTime, nullable=False)
    utime   = db.Column(db.DateTime, nullable=False)

    status  = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, user_id, hookid, name, phone, desc):
        self.user_id = user_id
        self.hookid = hookid
        self.name = name
        self.phone = phone
        self.desc = desc

        now = datetime.now()
        self.ctime = now
        self.utime = now
        self.status = 0

    def __repr__(self):
        return '<AplyAgent %r>' % self.name


"""
    @ 特殊字段说明

    salesman    业务员
        0非业务员   1业务员

    openluat_user_id    openluat总表的user_id
        存储在aliyun-mysql, openluat_user.user

    hook_agent_id   上级代理商的id
        0表示自己是总代理

    level       代理等级
        1商家 2市级代理   3省级代理   4总代理

    slevel      业务员等级
        1一级业务员  2二级业务员  3三级业务员

    expandable  是否可设置下级
        0不可以    1可以

    withdrawable 充值金额是否可直接体现
        0不可以    1可以

"""
class Agent(db.Model):
    __tablename__ = 'agent'

    id      = db.Column(db.Integer, primary_key=True)
    salesman = db.Column(db.Integer, nullable=False, server_default='0')
    openluat_user_id = db.Column(db.Integer, nullable=False)
    hook_agent_id = db.Column(db.Integer, nullable=False, server_default="1")
    level   = db.Column(db.Integer, nullable=False, server_default='0')
    slevel  = db.Column(db.Integer, nullable=False, server_default='0')
    expandable = db.Column(db.Integer, nullable=False, server_default="0")
    withdrawable = db.Column(db.Integer, nullable=False, server_default="0")
    name    = db.Column(db.String(32), nullable=False)
    phone   = db.Column(db.String(24), nullable=False)
    email   = db.Column(db.String(64), nullable=False)
    desc    = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(128), nullable=False)
    remark  = db.Column(db.String(128), nullable=False)

    ctime   = db.Column(db.DateTime, nullable=False)
    utime   = db.Column(db.DateTime, nullable=False)

    status  = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, salesman, user_id, hook_agent_id, level, slevel, expandable, withdrawable, name, phone, email, desc, address, remark):
        self.salesman = salesman
        self.openluat_user_id = user_id
        self.hook_agent_id = hook_agent_id
        self.level = level
        self.slevel = slevel
        self.expandable = expandable
        self.withdrawable = withdrawable
        self.name = name
        self.phone = phone
        self.email = email
        self.desc = desc
        self.address = address
        self.remark = remark

        now = datetime.now()
        self.ctime = now
        self.utime = now
        self.status = 0

    def __repr__(self):
        return '<Agent %r>' % self.name


class AgentInfo(db.Model):
    __tablename__ = 'agent_info'

    id      = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.ForeignKey(u'agent.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    logo    = db.Column(db.String(128), nullable=False, server_default=config.DEFAULT_LOGO)
    title   = db.Column(db.String(32), nullable=False, server_default='码夫支付管理系统')

    ctime   = db.Column(db.DateTime, nullable=False, server_default=func.now())
    utime   = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    status  = db.Column(db.Integer, nullable=False, server_default='0')

    def __init__(self, agent_id, logo, title):
        self.agent_id = agent_id
        self.logo = logo
        self.title = title

    def __repr__(self):
        return '<AgentInfo for agent: %r>' % self.agent_id


"""
    @ 商品表
    cat     类别：0按摩椅，1娃娃机，2洗衣机，99充值套餐, 100广告优惠券
"""
PRODUCT_CAT_RELAY = 0
PRODUCT_CAT_PULSE = 1
PRODUCT_CAT_WASH  = 2
PRODUCT_CAT_RECHARGE = 99
PRODUCT_CAT_COUPON = 100
class Product(db.Model):
    __tablename__ = 'product'

    id      = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.ForeignKey(u'agent.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    title   = db.Column(db.String(64), nullable=False)
    body    = db.Column(db.String(128), nullable=False)
    value   = db.Column(db.Integer, nullable=False, server_default='0')
    cat     = db.Column(db.Integer, nullable=False, server_default='0')
    price   = db.Column(db.Integer, nullable=False, server_default='1')
    inventory = db.Column(db.Integer, nullable=False, server_default='99999')
    deleted = db.Column(db.Integer, nullable=False, server_default="0")

    ctime   = db.Column(db.DateTime, nullable=False)
    utime   = db.Column(db.DateTime, nullable=False)

    status  = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, agent_id, title, body, value, cat, price, inventory):
        self.agent_id = agent_id
        self.title = title
        self.body = body
        self.value = value
        self.cat = cat
        self.price = price
        self.inventory = inventory

        now = datetime.now()
        self.ctime = now
        self.utime = now
        self.status = 0

    def __repr__(self):
        return '<Product %r>' % self.title


class Pay(db.Model):
    __tablename__ = 'pay'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, nullable=False)
    agent_id    = db.Column(db.Integer, nullable=False)
    imei        = db.Column(db.String(32), nullable=False)
    pay_mode    = db.Column(db.Integer, nullable=False, server_default="1")
    trade_no    = db.Column(db.String(24), nullable=False, unique=True, index=True)
    product_id  = db.Column(db.ForeignKey(u'product.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    title       = db.Column(db.String(64), nullable=False)
    body        = db.Column(db.String(128), nullable=False)
    cat         = db.Column(db.Integer, nullable=False, server_default='0')
    total_fee   = db.Column(db.Integer, nullable=False, server_default='1')
    prepay_id   = db.Column(db.String(64), nullable=False, server_default="")
    qrcode      = db.Column(db.String(128), nullable=False, server_default="")
    ali_trade_no = db.Column(db.String(64), nullable=False, server_default="")
    nofity_res  = db.Column(db.Text, nullable=False)
    cash_fee    = db.Column(db.Integer, nullable=False, server_default="0")
    deleted     = db.Column(db.Integer, nullable=False, server_default="0")

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

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
        self.ali_trade_no = ""
        self.qrcode = qrcode
        self.nofity_res = ''
        self.cash_fee = 0

        now = datetime.now()
        self.ctime = now
        self.utime = now
        self.status = 0

    def __repr__(self):
        return '<Pay %r>' % self.trade_no


class Refund(db.Model):
    __tablename__ = 'refund'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, nullable=False)
    pay_id      = db.Column(db.ForeignKey(u'pay.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    refund_no   = db.Column(db.String(24), nullable=False, unique=True)
    total_fee   = db.Column(db.Integer, nullable=False, server_default='1')
    refund_fee  = db.Column(db.Integer, nullable=False, server_default='1')
    nofity_res  = db.Column(db.Text, nullable=False)
    deleted     = db.Column(db.Integer, nullable=False, server_default="0")

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, user_id, pay_id, refund_no, total_fee, refund_fee, status):
        self.user_id = user_id
        self.pay_id  = pay_id
        self.refund_no = refund_no
        self.total_fee = total_fee
        self.refund_fee = refund_fee
        self.nofity_res = ''

        now = datetime.now()
        self.ctime = now
        self.utime = now
        self.status = status

    def __repr__(self):
        return '<Refund %r>' % self.refund_no


class Record(db.Model):
    __tablename__ = 'record'

    id      = db.Column(db.Integer, primary_key=True)
    pay_id  = db.Column(db.ForeignKey(u'pay.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False, unique=True)
    pay_way = db.Column(db.Integer, nullable=False, server_default="0")
    user_id = db.Column(db.Integer, nullable=False)
    agent_id = db.Column(db.ForeignKey(u'agent.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    product_id = db.Column(db.ForeignKey(u'product.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    stime   = db.Column(db.DateTime, nullable=False)
    etime   = db.Column(db.DateTime, nullable=False)

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, pay_id, pay_way, user_id, agent_id, product_id, stime, etime):
        self.pay_id = pay_id
        self.pay_way = pay_way
        self.user_id = user_id
        self.agent_id = agent_id
        self.product_id = product_id
        self.stime = stime
        self.etime = etime

        now = datetime.now()
        self.ctime = now
        self.utime = now
        self.status = 0

    def __repr__(self):
        return '<Record %r>' % self.id


class RecordNoPay(db.Model):
    __tablename__ = 'record_no_pay'

    id      = db.Column(db.Integer, primary_key=True)
    imei    = db.Column(db.String(32), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    agent_id = db.Column(db.ForeignKey(u'agent.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    stime   = db.Column(db.DateTime, nullable=False)
    etime   = db.Column(db.DateTime, nullable=False)

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, imei, user_id, agent_id, stime, etime):
        self.imei = imei
        self.user_id = user_id
        self.agent_id = agent_id
        self.stime = stime
        self.etime = etime

        now = datetime.now()
        self.ctime = now
        self.utime = now
        self.status = 0

    def __repr__(self):
        return '<RecordNoPay %r>' % self.id


class RecordCouponNopay(db.Model):
    __tablename__ = 'record_coupon_no_pay'

    id      = db.Column(db.Integer, primary_key=True)
    imei    = db.Column(db.String(32), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    agent_id = db.Column(db.ForeignKey(u'agent.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    stime   = db.Column(db.DateTime, nullable=False)
    etime   = db.Column(db.DateTime, nullable=False)

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, imei, user_id, agent_id, stime, etime):
        self.imei = imei
        self.user_id = user_id
        self.agent_id = agent_id
        self.stime = stime
        self.etime = etime

        now = datetime.now()
        self.ctime = now
        self.utime = now
        self.status = 0

    def __repr__(self):
        return '<RecordCouponNopay %r>' % self.id


class GameCoin(db.Model):
    __tablename__ = 'game_coin'

    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey(u'mafu_user.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    coin    = db.Column(db.Integer, nullable=False, server_default="0")

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")


    def __init__(self, user_id):
        self.user_id = user_id

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<GameCoin user: %r -- coin: %r>' % (self.user_id, self.coin)


"""
    @ 游戏币消费记录表
    in_out  类别：1收入  2支出
"""
class CoinRecord(db.Model):
    __tablename__ = 'coin_record'

    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey(u'mafu_user.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    in_out  = db.Column(db.Integer, nullable=False, server_default='0')
    coin    = db.Column(db.Integer, nullable=False, server_default="0")

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, user_id, in_out, coin):
        self.user_id = user_id
        self.in_out  = in_out
        self.coin    = coin

        now = datetime.now()
        self.ctime = now
        self.utime = now


class DeviceAddress(db.Model):
    __tablename__ = 'device_address'

    id          = db.Column(db.Integer, primary_key=True)
    agent_id    = db.Column(db.ForeignKey(u'agent.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    region      = db.Column(db.String(128), nullable=False, server_default="")
    address     = db.Column(db.String(128), nullable=False, server_default="")

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, agent_id, region, address):
        self.agent_id = agent_id
        self.region = region
        self.address = address

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<DeviceAddress: %r %r>' % (self.region, self.address)


"""
    @ 设备表
        agent_id            设备的起始代理id
        owner_agent_id      设备此时拥有者的代理id
        salesman_agent_id   设备此时的业务员代理id

        l4  总代理提成比例
        l3  省级代理提成比例
        l2  市级代理提成比例
        l1  经销商提成比例

        sl1 一级业务员提成比例
        sl2 二级业务员提成比例
        sl3 三级业务员提成比例

        nopay       无需支付

        product_unit_price  产品的单位价格
        product_min_money   产品最小投币金额
        product_unit        产品的单位
"""
class Device(db.Model):
    __tablename__ = 'device'

    id          = db.Column(db.Integer, primary_key=True)
    imei        = db.Column(db.String(32), nullable=False, unique=True, index=True)
    cat         = db.Column(db.Integer, nullable=False, server_default="0")
    agent_id    = db.Column(db.Integer, nullable=False, server_default="0")
    owner_agent_id = db.Column(db.Integer, nullable=False)
    salesman_agent_id = db.Column(db.Integer, nullable=False)
    address_id  = db.Column(db.Integer, nullable=False, server_default="0")
    map_display = db.Column(db.Integer, nullable=False, server_default="0")
    l4          = db.Column(db.Float, nullable=False)
    l3          = db.Column(db.Float, nullable=False)
    l2          = db.Column(db.Float, nullable=False)
    l1          = db.Column(db.Float, nullable=False)
    sl1         = db.Column(db.Float, nullable=False)
    sl2         = db.Column(db.Float, nullable=False)
    sl3         = db.Column(db.Float, nullable=False)
    remark      = db.Column(db.String(64), nullable=False, server_default="")
    nopay       = db.Column(db.Integer, nullable=False, server_default="0")
    coupon      = db.Column(db.Integer, nullable=False, server_default="0")
    product_unit_price  = db.Column(db.Integer, nullable=False, server_default="100")
    product_min_money   = db.Column(db.Integer, nullable=False, server_default="100")
    product_unit        = db.Column(db.String(10), nullable=False, server_default="个")
    product_unit_pluse  = db.Column(db.Integer, nullable=False, server_default="1")
    low         = db.Column(db.Integer, nullable=False, server_default='50')
    high         = db.Column(db.Integer, nullable=False, server_default='50')

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, imei, cat, agent_id, owner_agent_id, address_id):
        self.imei = imei
        self.agent_id = agent_id
        self.owner_agent_id = owner_agent_id
        self.salesman_agent_id = 0
        self.address_id = address_id
        self.cat = cat
        self.l1 = 0
        self.l2 = 0
        self.l3 = 0
        self.l4 = 1
        self.sl1 = 0
        self.sl2 = 0
        self.sl3 = 0
        self.remark = ''

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<Device: %r>' % self.imei


class DeviceDistribution(db.Model):
    __tablename__ = 'device_distribution'

    id          = db.Column(db.Integer, primary_key=True)
    device_id   = db.Column(db.Integer, nullable=False)
    imei        = db.Column(db.String(32), nullable=False)
    from_agent  = db.Column(db.Integer, nullable=False)
    to_agent    = db.Column(db.Integer, nullable=False)
    rate        = db.Column(db.Float, nullable=False, server_default='0.0')

    ctime       = db.Column(db.DateTime, nullable=False)
    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, device_id, imei, from_agent, to_agent, rate):
        self.device_id = device_id
        self.imei = imei
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.rate = rate

        now = datetime.now()
        self.ctime = now
        self.status = 0

    def __repr__(self):
        return '<DeviceDistribution: %r>' % self.id


class DeviceDistributionSalesman(db.Model):
    __tablename__ = 'device_distribution_salesman'

    id          = db.Column(db.Integer, primary_key=True)
    device_id   = db.Column(db.Integer, nullable=False)
    imei        = db.Column(db.String(32), nullable=False)
    from_agent  = db.Column(db.Integer, nullable=False)
    to_agent    = db.Column(db.Integer, nullable=False)

    ctime       = db.Column(db.DateTime, nullable=False)
    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, device_id, imei, from_agent, to_agent):
        self.device_id = device_id
        self.imei = imei
        self.from_agent = from_agent
        self.to_agent = to_agent

        now = datetime.now()
        self.ctime = now
        self.status = 0

    def __repr__(self):
        return '<DeviceDistributionSalesman: %r>' % self.id


class DeviceProduct(db.Model):
    __tablename__ = 'device_product'

    id          = db.Column(db.Integer, primary_key=True)
    device_id   = db.Column(db.ForeignKey(u'device.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    product_id  = db.Column(db.ForeignKey(u'product.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, device_id, product_id):
        self.device_id = device_id
        self.product_id = product_id

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<DeviceProduct: %r>' % self.id


class DailyIncome(db.Model):
    __tablename__ = 'daily_income'

    id          = db.Column(db.Integer, primary_key=True)
    agent_id    = db.Column(db.Integer, nullable=False)
    online_income = db.Column(db.Integer, nullable=False)
    offline_income = db.Column(db.Integer, nullable=False)
    total_consume = db.Column(db.Integer, nullable=False)
    total_balance = db.Column(db.Integer, nullable=False)
    date        = db.Column(db.Date, nullable=False)

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

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
    @ 代理设置表
    min_withdraw        最小取现金额
    l1,l2,l3            分别对应一级，二级，三级代理商的提成
    withdraw_fee        取现手续费
    wallet_pay_enable   是否支持钱包支付
    trans_url           透传回调地址
"""
class AgentSetting(db.Model):
    __tablename__ = 'agent_setting'

    id           = db.Column(db.Integer, primary_key=True)
    agent_id     = db.Column(db.ForeignKey(u'agent.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    min_withdraw = db.Column(db.Integer, nullable=False)
    l1           = db.Column(db.Float, nullable=False, server_default="0.0")
    l2           = db.Column(db.Float, nullable=False, server_default="0.0")
    l3           = db.Column(db.Float, nullable=False, server_default="0.0")
    withdraw_fee = db.Column(db.Float, nullable=False, server_default="0.0")
    wallet_pay_enable = db.Column(db.Integer, nullable=False, server_default="1")
    trans_url    = db.Column(db.String(128), nullable=False, server_default='')

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, agent_id, min_withdraw, l1, l2, l3, withdraw_fee, wallet_pay_enable):
        self.agent_id = agent_id
        self.min_withdraw = min_withdraw
        self.l1 = l1
        self.l2 = l2
        self.l3 = l3
        self.withdraw_fee = withdraw_fee
        self.wallet_pay_enable = wallet_pay_enable
        self.trans_url = ''

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<AgentSetting: %r>' % self.id


"""
    @ 钱包表

    role 钱包所有者的角色
        0表示普通微信用户   1表示代理商用户

    withdrawable_balance    可提现金额
"""
class Wallet(db.Model):
    __tablename__ = 'wallet'

    id      = db.Column(db.Integer, primary_key=True)
    role    = db.Column(db.Integer, nullable=False, server_default='0')
    user_id = db.Column(db.Integer, nullable=False)
    agent_id = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Float, nullable=False, server_default='0')
    withdrawable_balance = db.Column(db.Float, nullable=False, server_default='0')

    ctime   = db.Column(db.DateTime, nullable=False)
    utime   = db.Column(db.DateTime, nullable=False)

    status  = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, user_id, role, agent_id):
        self.user_id = user_id
        self.role = role
        self.agent_id = agent_id

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<Wallet: %r>' % self.id


"""
    @ 钱包交易收据表

    role 钱包所有者的角色
        0表示普通微信用户   1表示代理商用户

    trade_type      交易类型(奇数收入，偶数支出)
        1.  代理提成收入
        2.  代理微信取现
        3.  用户充值
        4.  用户消费
        5.  转账转入
        6.  转账转出
        7.  用户退款
        8.  代理提成退款

    payment_no      微信取现单号
        默认为'--'，当trade_type为2时，该值为微信返回值

    receipt                 收据,进入钱包余额
    withdrawable_receipt    可提现收据,进入钱包可提现余额
"""
WALLET_TRADE_TYPE_TICHENG = 1
WALLET_TRADE_TYPE_WECHAT_WITHDRAW = 2
WALLET_TRADE_TYPE_DEPOSIT = 3
WALLET_TRADE_TYPE_EXPENDITURE = 4
WALLET_TRADE_TYPE_TRANSFER_IN = 5
WALLET_TRADE_TYPE_TRANSFER_OUT = 6
WALLET_TRADE_TYPE_REFUND = 7
WALLET_TRADE_TYPE_REFUND_TICHENG = 8
class WalletReceipt(db.Model):
    __tablename__ = 'wallet_receipt'

    id          = db.Column(db.Integer, primary_key=True)
    role        = db.Column(db.Integer, nullable=False, server_default='0')
    user_id     = db.Column(db.Integer, nullable=False)
    agent_id    = db.Column(db.Integer, nullable=False)
    wallet_id   = db.Column(db.ForeignKey(u'wallet.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    trade_type  = db.Column(db.Integer, nullable=False)
    receipt     = db.Column(db.Float, nullable=False)
    withdrawable_receipt = db.Column(db.Float, nullable=False)
    payment_no  = db.Column(db.String(64), nullable=False)
    remark      = db.Column(db.String(128), nullable=False)

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, role, user_id, agent_id, wallet_id, trade_type, receipt, withdrawable_receipt, remark, payment_no):
        self.role = role
        self.user_id = user_id
        self.agent_id = agent_id
        self.wallet_id = wallet_id
        self.trade_type = trade_type
        self.receipt = receipt
        self.withdrawable_receipt = withdrawable_receipt
        self.remark = remark
        self.payment_no = payment_no

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<WalletReceipt: id,%r receipt,%r>' % (self.id, self.receipt)


"""
    @ 代理提现表

    wechat_agent_id     对接的公众号的代理id

"""
class PayToUser(db.Model):
    __tablename__ = 'pay_to_user'

    id          = db.Column(db.Integer, primary_key=True)
    wechat_agent_id  = db.Column(db.Integer, nullable=False)
    openluat_user_id = db.Column(db.Integer, nullable=False)
    to_openid   = db.Column(db.String(128), nullable=False)
    to_nickname = db.Column(db.String(64), nullable=False)
    trade_no    = db.Column(db.String(24), nullable=False, unique=True, index=True)
    total_fee   = db.Column(db.Integer, nullable=False)
    # fee_rate    = db.Column(db.Float, nullable=False, server_default='0.006')
    desc        = db.Column(db.String(128), nullable=False)
    remark      = db.Column(db.String(128), nullable=False)
    payment_no  = db.Column(db.String(64), nullable=False)
    notify_res  = db.Column(db.Text, nullable=False)

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, wechat_agent_id, user_id, to_openid, to_nickname, trade_no,
            total_fee, desc, remark):
    # def __init__(self, wechat_agent_id, user_id, to_openid, to_nickname, trade_no,
    #         total_fee, fee_rate, desc, remark):
        self.wechat_agent_id = wechat_agent_id
        self.openluat_user_id = user_id
        self.to_openid = to_openid
        self.to_nickname = to_nickname
        self.trade_no = trade_no
        self.total_fee = total_fee
        # self.fee_rate = fee_rate
        self.desc = desc
        self.remark = remark

        self.payment_no = ''
        self.notify_res = ''

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<PayToUser: %r>' % self.id


"""
    线下投币记录表
        time    投币时间
        coin    投币金额，单位分
"""
class OfflineCoin(db.Model):
    __tablename__ = 'offline_coin'

    id          = db.Column(db.Integer, primary_key=True)
    imei        = db.Column(db.String(32), nullable=False, index=True)
    time        = db.Column(db.DateTime, nullable=False)
    coin        = db.Column(db.Integer, nullable=False)

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, imei, time, coin):
        self.imei = imei
        self.time = time
        self.coin = coin

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<OfflineCoin: %r>' % self.id


# """
#       mqtt异步缓存表
#         status  状态
#             0   mqtt未返回
#             1   mqtt返回成功，http返回成功
#             2   mqtt返回失败
#             3   http返回失败
# """

# class MqttAsync(db.Model):
#     __tablename__ = ''

#     id          = db.Column(db.Integer, primary_key=True)
#     greenlet_id = db.Column(db.Integer, nullable=False, index=True)
#     http_url    = db.Column(db.String(128), nullable=False)
#     mqtt_res    = db.Column(db.Text, nullable=False)
#     http_res    = db.Column(db.Text, nullable=False)

#     ctime       = db.Column(db.DateTime, nullable=False)
#     utime       = db.Column(db.DateTime, nullable=False)

#     status      = db.Column(db.Integer, nullable=False, server_default="0")

#     def __init__(self, greenlet_id, http_url):
#      self.greenlet_id = greenlet_id
#      self.http_url = http_url
#      self.mqtt_res = ''
#      self.http_res = ''

#      now = datetime.now()
#      self.ctime = now
#      self.utime = now

#     def __repr__(self):
#      return '<MqttAsync: %r>' % self.id


"""
    @ 管理员用户表
        role    1管理员，2超级管理员，唯一
"""
class God(db.Model):
    __tablename__ = 'god'

    id      = db.Column(db.Integer, primary_key=True)
    openluat_user_id = db.Column(db.Integer, nullable=False)
    role    = db.Column(db.Integer, nullable=False)
    name    = db.Column(db.String(16), nullable=False)
    phone   = db.Column(db.String(32), nullable=False, unique=True)
    email   = db.Column(db.String(64), nullable=False, unique=True)
    remark  = db.Column(db.String(128), nullable=False, server_default="")

    ctime   = db.Column(db.DateTime, nullable=False)
    utime   = db.Column(db.DateTime, nullable=False)

    status  = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, openluat_user_id, role, name, phone, email, remark):
        self.openluat_user_id = openluat_user_id
        self.role = role
        self.name = name
        self.phone = phone
        self.email = email
        self.remark = remark

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<God: %r>' % self.id


class GodInfo(db.Model):
    __tablename__ = 'god_info'

    id      = db.Column(db.Integer, primary_key=True)
    god_id  = db.Column(db.ForeignKey(u'god.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    logo    = db.Column(db.String(128), nullable=False, server_default=config.DEFAULT_LOGO)
    title   = db.Column(db.String(32), nullable=False, server_default='码夫支付管理系统')

    ctime   = db.Column(db.DateTime, nullable=False, server_default=func.now())
    utime   = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    status  = db.Column(db.Integer, nullable=False, server_default='0')

    def __init__(self, god_id, logo, title):
        self.god_id = god_id
        self.logo = logo
        self.title = title

    def __repr__(self):
        return '<GodInfo for god: %r>' % self.god_id


class GodAgent(db.Model):
    __tablename__ = 'god_agent'

    id          = db.Column(db.Integer, primary_key=True)
    god_id      = db.Column(db.Integer, nullable=False)
    agent_id    = db.Column(db.Integer, nullable=False)

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, god_id, agent_id):
        self.god_id = god_id
        self.agent_id = agent_id

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<GodAgent: %r>' % self.id


class WechatConfig(db.Model):
    __tablename__ = 'wechat_config'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(16), nullable=False)
    appid       = db.Column(db.String(32), nullable=False)
    appsecret   = db.Column(db.String(64), nullable=False)
    mchid       = db.Column(db.String(32), nullable=False)
    mchkey      = db.Column(db.String(64), nullable=False)
    redirecturl = db.Column(db.String(128), nullable=False)
    redirect_bind_url = db.Column(db.String(128), nullable=False)
    key_path    = db.Column(db.String(128), nullable=False)
    qrcode_img  = db.Column(db.String(128), nullable=False)

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, name, appid, appsecret, mchid, mchkey, redirecturl, redirect_bind_url, key_path, qrcode_img):
        self.name = name
        self.appid = appid
        self.appsecret = appsecret
        self.mchid = mchid
        self.mchkey = mchkey
        self.redirecturl = redirecturl
        self.redirect_bind_url = redirect_bind_url
        self.key_path = key_path
        self.qrcode_img = qrcode_img

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<WechatConfig: %r>' % self.id


class AgentWechat(db.Model):
    __tablename__ = 'agent_wechat'

    id          = db.Column(db.Integer, primary_key=True)
    agent_id    = db.Column(db.ForeignKey(u'agent.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    wechat_config_id = db.Column(db.ForeignKey(u'wechat_config.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, agent_id, wechat_config_id):
        self.agent_id = agent_id
        self.wechat_config_id = wechat_config_id

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<AgentWechat: %r>' % self.id


class WechatBind(db.Model):
    __tablename__ = 'wechat_bind'

    id          = db.Column(db.Integer, primary_key=True)
    admin_uid   = db.Column(db.Integer, unique=True, nullable=False)
    expires_at  = db.Column(db.DateTime, nullable=False)

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, admin_uid, expires_at):
        self.admin_uid = admin_uid
        self.expires_at = expires_at

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<WechatBind: %r>' % self.id


class AliUser(db.Model):
    __tablename__ = 'ali_user'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.ForeignKey(u'mafu_user.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    user_id_a   = db.Column(db.String(64), nullable=False, unique=True)
    ali_user_id = db.Column(db.String(64), nullable=False, unique=True)

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, user_id, user_id_a, ali_user_id):
        self.user_id = user_id
        self.user_id_a = user_id_a
        self.ali_user_id = ali_user_id

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<AliUser: %r>' % self.id


class AliConfig(db.Model):
    __tablename__ = 'ali_config'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(16), nullable=False)
    appid       = db.Column(db.String(32), nullable=False)
    priv_path   = db.Column(db.String(128), nullable=False)
    pub_path    = db.Column(db.String(128), nullable=False)

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, name, appid, priv_path, pub_path):
        self.name = name
        self.appid = appid
        self.priv_path = priv_path
        self.pub_path = pub_path

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<AliConfig: %r>' % self.id


class AgentAli(db.Model):
    __tablename__ = 'agent_ali'

    id          = db.Column(db.Integer, primary_key=True)
    agent_id    = db.Column(db.ForeignKey(u'agent.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    ali_config_id = db.Column(db.ForeignKey(u'ali_config.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, agent_id, ali_config_id):
        self.agent_id = agent_id
        self.ali_config_id = ali_config_id

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<AgentAli: %r>' % self.id


class UserStartCounter(db.Model):
    __tablename__ = 'user_start_counter'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.ForeignKey(u'mafu_user.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    imei        = db.Column(db.String(32), nullable=False)
    count       = db.Column(db.Integer, nullable=False, server_default="0")

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, user_id, imei):
        self.user_id = user_id
        self.imei = imei

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<UserStartCounter: %r>' % self.id


class Advertisement(db.Model):
    __tablename__ = 'advertisement'

    id      = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.ForeignKey(u'agent.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    name    = db.Column(db.String(16), nullable=False)
    desc    = db.Column(db.String(64), nullable=False)
    img     = db.Column(db.String(128), nullable=False)
    url     = db.Column(db.String(128), nullable=False)

    using   = db.Column(db.Integer, nullable=False, server_default="0")
    deleted = db.Column(db.Integer, nullable=False, server_default='0')

    ctime   = db.Column(db.DateTime, nullable=False)
    utime   = db.Column(db.DateTime, nullable=False)

    status  = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, agent_id, name, desc, img, url):
        self.agent_id = agent_id
        self.name = name
        self.desc = desc
        self.img  = img
        self.url  = url

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<Advertisement: %r>' % self.id


class DeviceAd(db.Model):
    __tablename__ = 'device_advertisement'

    id          = db.Column(db.Integer, primary_key=True)
    device_id   = db.Column(db.ForeignKey(u'device.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)
    ad_id       = db.Column(db.ForeignKey(u'advertisement.id', ondelete=u'CASCADE', onupdate=u'CASCADE'), nullable=False)

    ctime       = db.Column(db.DateTime, nullable=False)
    utime       = db.Column(db.DateTime, nullable=False)

    status      = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, device_id, ad_id):
        self.device_id = device_id
        self.ad_id = ad_id

        now = datetime.now()
        self.ctime = now
        self.utime = now

    def __repr__(self):
        return '<DeviceAd: %r>' % self.id


class Advertiser(db.Model):
    __tablename__ = 'advertiser'

    id          = db.Column(db.Integer, primary_key=True)
    openluat_user_id = db.Column(db.Integer, nullable=False)
    hook_agent_id    = db.Column(db.Integer, nullable=False)
    name    = db.Column(db.String(32), nullable=False)
    phone   = db.Column(db.String(24), nullable=False)
    email   = db.Column(db.String(64), nullable=False)
    desc    = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(128), nullable=False)
    remark  = db.Column(db.String(128), nullable=False)

    ctime   = db.Column(db.DateTime, nullable=False, server_default=func.now())
    utime   = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    status  = db.Column(db.Integer, nullable=False, server_default="0")

    def __init__(self, openluat_user_id, hook_agent_id, name, phone, email, desc, address, remark):
        self.openluat_user_id = openluat_user_id
        self.hook_agent_id = hook_agent_id
        self.name = name
        self.phone = phone
        self.email = email
        self.desc = desc
        self.address = address
        self.remark = remark

    def __repr__(self):
        return '<Advertiser: %r>' % self.id


class Coupon(db.Model):
    __tablename__ = 'coupon'

    id          = db.Column(db.Integer, primary_key=True)
    agent_id    = db.Column(db.Integer, nullable=False)
    advertiser_id   = db.Column(db.ForeignKey('advertiser.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    product_id  = db.Column(db.ForeignKey('product.id', ondelete='CASCADE', onupdate='CASCADE'))
    pay_id      = db.Column(db.ForeignKey('pay.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    title       = db.Column(db.String(32), nullable=False)
    desc        = db.Column(db.String(64), nullable=False)
    total       = db.Column(db.Integer, nullable=False)
    prefix      = db.Column(db.String(10), nullable=False, unique=True)
    img         = db.Column(db.String(128), nullable=False)
    paid        = db.Column(db.Integer, nullable=False, server_default="0")

    ctime       = db.Column(db.DateTime, nullable=False, server_default=func.now())
    utime       = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    status      = db.Column(db.Integer, nullable=False, server_default='0')

    def __init__(self, agent_id, advertiser_id, product_id, pay_id, title, desc, prefix, total, img):
        self.agent_id = agent_id
        self.advertiser_id = advertiser_id
        self.product_id = product_id
        self.pay_id = pay_id
        self.title = title
        self.desc = desc
        self.prefix = prefix
        self.total = total
        self.img = img

    def __repr__(self):
        return '<Coupon: %r>' % self.id


class DeviceCoupon(db.Model):
    __tablename__ = 'device_coupon'

    id          = db.Column(db.Integer, primary_key=True)
    coupon_id   = db.Column(db.ForeignKey('coupon.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    device_id   = db.Column(db.ForeignKey('device.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    ctime       = db.Column(db.DateTime, nullable=False, server_default=func.now())
    utime       = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    status      = db.Column(db.Integer, nullable=False, server_default='0')

    def __init__(self, coupon_id, device_id):
        self.coupon_id = coupon_id
        self.device_id = device_id

    def __repr__(self):
        return '<DeviceCoupon: %r>' % self.id


class CouponReceipt(db.Model):
    __tablename__ = 'coupon_receipt'

    id          = db.Column(db.Integer, primary_key=True)
    coupon_id   = db.Column(db.ForeignKey("coupon.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    user_id     = db.Column(db.Integer, nullable=False, server_default='0')
    code        = db.Column(db.String(32), nullable=False, index=True, unique=True)
    started     = db.Column(db.Integer, nullable=False, server_default="0")
    used        = db.Column(db.Integer, nullable=False, server_default="0")

    ctime       = db.Column(db.DateTime, nullable=False, server_default=func.now())
    utime       = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    status      = db.Column(db.Integer, nullable=False, server_default='0')

    def __init__(self, coupon_id, user_id, code):
        self.coupon_id = coupon_id
        self.user_id = user_id
        self.code = code

    def __repr__(self):
        return '<CouponReceipt: %r>' % self.code

