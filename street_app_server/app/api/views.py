#!/usr/bin/env python3
# coding: utf8
# 20170220 anChaOs


# general
import json, time, random
import requests # for http requests
from datetime import datetime, timedelta, date
from fractions import Fraction

# wraps
from functools import wraps

# flask
from flask import Flask, request, session, jsonify, current_app, g
from flask import redirect, url_for, render_template, make_response

# flask-login
from flask.ext.login import login_user, logout_user, current_user
from flask.ext.login import login_required, LoginManager

# db
from app import db

# config
import config as config

# database functions
import app.database.api as dbapi

# error
import app.error as error
ApiError = error.ApiError

# normal functions
from .apis import *
from app.admin.apis import refund_income

import app.tool as tool
from app.tool import dbg                    # for print
from app.tool import print_exception_info   # for traceback

# wechat
import app.third_party.wechatsdk as wechatsdk
import app.third_party.wechatpay as wechatpay

# blueprint
from . import api_blueprint


@api_blueprint.errorhandler(ApiError)
def handle_api_error(current_error):
    dbg((current_error.msg, current_error.error_no))
    error_info = error.get_error_info(current_error.error_no)
    return make_response(jsonify({'code':current_error.error_no, 'msg':error_info[0]}), error_info[1])


@api_blueprint.errorhandler(Exception)
def handle_base_exception(current_error):
    print_exception_info()
    db.session.rollback()
    return make_response(json.dumps({'code':99, 'msg':'server error'}), 500)


def check_openid(func):
    @wraps(func)
    def wrapper(*args, **kws):
        if 'has_openid' in session:
            session.pop('has_openid')
        # session['openid'] = 'oEMOtjoiv9HBQiAC7x7BnSDAUuVw'
        user_agent = request.headers.get('User-Agent')
        if 'MicroMessenger' in user_agent:
            if 'openid' not in session:
                raise ApiError('do not login', error.ERROR_NO_LOGIN)
            wechat_user = dbapi.get_wechat_user(openid=session['openid'])
            if not wechat_user:
                raise ApiError('do not login', error.ERROR_NO_LOGIN)
            g.wechat_user = wechat_user
            g.oauth_user = wechat_user
        else:
            if 'ali_user_id' not in session:
                raise ApiError('do not login', error.ERROR_NO_LOGIN)
            ali_user = dbapi.get_ali_user(ali_user_id=session['ali_user_id'])
            if not ali_user:
                raise ApiError('do not login', error.ERROR_NO_LOGIN)
            g.oauth_user = ali_user
            g.wechat_user = None
        return func(*args, **kws)
    return wrapper


@api_blueprint.route('/wallet/fetch', methods=["POST"])
@check_openid
def get_wallet_balance():
    dbg('get_wallet_balance')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        imei = data['imei']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    device = dbapi.get_device(imei=imei)
    if not device:
        raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)

    user_id = g.oauth_user.user_id
    wallet = dbapi.get_wallet(role=0, user_id=user_id, agent_id=device.owner_agent_id)

    agent_setting = dbapi.get_agent_setting(agent_id=device.agent_id)
    wallet_pay_enable = 1
    if agent_setting and agent_setting.wallet_pay_enable == 0:
        wallet_pay_enable = 0


    reply['data'] = {
        'balance': wallet.balance,
        'wallet_pay_enable': wallet_pay_enable
    }
    return make_response(jsonify(reply), status_code)


@api_blueprint.route('/wechat_info/fetch', methods=["POST"])
@check_openid
def get_wechat_info():
    dbg('get_wechat_info')
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    try:
        data = request.get_json()
        imei = data['imei']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    wechat_config   = dbapi.get_wechat_config(imei=imei)
    appid           = wechat_config.appid
    appsecret       = wechat_config.appsecret
    openid          = session['openid']
    qrcode_img      = wechat_config.qrcode_img

    wechat_info     = wechatsdk.get_wechat_user_info(appid, appsecret, openid)

    reply['data']   = {
        'subscribe': wechat_info['subscribe'],
        'qrcode'   : url_for('static', filename=qrcode_img)
    }
    return make_response(jsonify(reply), status_code)


@api_blueprint.route('/title/fetch', methods=["POST"])
def get_wechat_title():
    dbg('get_wechat_title')
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    try:
        data = request.get_json()
        imei = data['imei']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    wechat_config   = dbapi.get_wechat_config(imei=imei)
    title = ''
    if wechat_config:
        title = wechat_config.name

    reply['data'] = {
        'title': title
    }
    return make_response(jsonify(reply), status_code)



@api_blueprint.route('/ysq_test', methods=["GET"])
def ysq_test():
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    try:
        ...
        # data = request.get_json()
        # imei = data['imei']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)
    reply['data'] = {
        'temples': [ {
                'name': '大雄宝殿',
                'id': 1,
                'lights': [{
                    'name': '健康灯',
                    'id': 1,
                    'price': 0.1,
                }, {
                    'name': '亲情灯',
                    'id': 2,
                    'price': 0.15,
                }, {
                    'name': '爱情灯',
                    'id': 3,
                    'price': 0.22,
                }, {
                    'name': '友情灯',
                    'id': 4,
                    'price': 0.05,
                }, {
                    'name': '事业灯',
                    'id': 5,
                    'price': 0.25,
                }, {
                    'name': '学业灯',
                    'id': 6,
                    'price': 0.12,
                }, {
                    'name': '幸运灯',
                    'id': 7,
                    'price': 0.23,
                }, {
                    'name': '桃花灯',
                    'id': 8,
                    'price': 0.17,
                }, {
                    'name': '随便灯',
                    'id': 9,
                    'price': 0.32,
                }]
            },{
                'name': '大雷音寺',
                'id': 2,
                'lights': [],
            }, {
                'name': '小雷音寺',
                'id': 3,
            }
        ],
        'packages': [{
            'id': 0,
            'name': '日供',
            'rate': 1,
        }, {
            'id': 1,
            'name': '七日',
            'rate': 7,
        }, {
            'id': 2,
            'name': '一月',
            'rate': 30,
        }, {
            'id': 3,
            'name': '七七四十九',
            'rate': 49,
        }]
    }

    resp = make_response(jsonify(reply), status_code)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp



@api_blueprint.route('/device_status', methods=["POST"])
@check_openid
def get_device_status():
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    try:
        data = request.get_json()
        imei = data['imei']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    status = dbapi.get_cws_device_status(imei)
    online = -1
    if status:
        online = status.get('online', -1)
    latest_report = dbapi.get_device_latestreport(imei)
    if not latest_report:
        raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)

    # dbg((datetime.now().timestamp(), latest_report['time'].timestamp()))
    if datetime.now().timestamp() - latest_report['time'].timestamp() > 150:
        if online == 1:
            online = 0

    alipay_available = 0
    if check_alipay_available(imei):
        alipay_available = 1

    reply['data'] = {
        'status': online,   # 0离线 1在线 4关机
        'alipay_available': alipay_available,
        'user_id': g.oauth_user.user_id
    }


    return make_response(jsonify(reply), status_code)


@api_blueprint.route('/wallet_products', methods=["POST"])
def get_wallet_products():
    dbg('get_wallet_products')
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    try:
        data = request.get_json()
        imei = data['imei']
    except:
        print_exception_info()
        raise ApiError('get products error', error.ERROR_PARAM)

    device = dbapi.get_device(imei=imei)
    if not device:
        raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)

    agent_id = device.owner_agent_id

    products = dbapi.get_product(agent_id=agent_id, cat=99)
    data = []
    if products:
        for product in products:
            dic = {
                'id'   : product.id,
                'title': product.title,
                'body' : product.body,
                'value': product.value,
                'price': product.price,
            }
            data.append(dic)
    reply['data'] = data

    return make_response(jsonify(reply), status_code)


@api_blueprint.route('/products', methods=["POST"])
def get_products():
    dbg('get_products')
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    try:
        data = request.get_json()
        imei = data['imei']
    except:
        print_exception_info()
        raise ApiError('get products error', error.ERROR_PARAM)

    device = dbapi.get_device(imei=imei)
    if not device:
        raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)
    device_products = dbapi.get_device_product(device_id=device.id)
    data = []
    if device_products:
        for device_product in device_products:
            product = dbapi.get_product(product_id=device_product.product_id)
            if not product:
                continue
            dic = {
                'id'   : product.id,
                'title': product.title,
                'body' : product.body,
                'value': product.value,
                'price': product.price,
                'unit' : device.product_unit,
                'number': str(Fraction(product.value, device.product_unit_pluse)),
            }
            data.append(dic)
    reply['data'] = data

    return make_response(jsonify(reply), status_code)


@api_blueprint.route('/ad/fetch', methods=["POST"])
def get_ads():
    dbg('get_ads')
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    try:
        data = request.get_json()
        imei = data['imei']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    device = dbapi.get_device(imei=imei)
    if not device:
        raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)
    ads = dbapi.get_ad(agent_id=device.owner_agent_id, using=1)
    data = []
    for ad in ads:
        info = {
            'id': ad.id,
            'name': ad.name,
            'desc': ad.desc,
            'img' : url_for('static', filename=ad.img),
            'url' : ad.url
        }
        data.append(info)

    reply['data'] = data

    return make_response(jsonify(reply), status_code)


@api_blueprint.route('/game_coin/fetch')
@check_openid
def fetch_game_coin():
    dbg('fetch_game_coin')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    user_id = g.oauth_user.user_id
    game_coin = dbapi.get_game_coin(user_id=user_id)
    if not game_coin:
        game_coin = dbapi.make_new_game_coin(user_id)
        db.session.commit()
    coin = game_coin.coin

    reply['data'] = {
        'coin': coin
    }

    return make_response(jsonify(reply), status_code)


@api_blueprint.route('/pay', methods=["PUT"])
@check_openid
def make_pay():
    dbg('make_pay')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        product_id = data['product_id']
        trade_type = data['trade_type']
        pay_mode = data['pay_mode']
        imei       = data['imei']
        if pay_mode == 2:
            cur_url  = data['url']
    except:
        print_exception_info()
        raise ApiError('pay error', error.ERROR_PARAM)

    device = dbapi.get_device(imei=imei)
    if not device:
        raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)

    agent_id = device.owner_agent_id

    user_id = g.oauth_user.user_id
    max_id  = dbapi.get_max_pay_id()
    str_max_id = '%04d' % max_id
    if len(str_max_id) > 4:
        str_max_id = str_max_id[-4:]
    trade_no = str(pay_mode) + datetime.now().strftime("%Y%m%d%H%M%S") + str_max_id
    product = dbapi.get_product(product_id=product_id)

    if pay_mode == 1:
        # 微信支付
        data = wechat_make_new_pay(product, trade_no, agent_id, user_id, imei, trade_type)
    elif pay_mode == 2:
        # 支付宝支付
        data = ali_make_new_pay(product, trade_no, agent_id, user_id, imei, cur_url)
    elif pay_mode == 3:
        if product.cat == 99:
            raise ApiError('not support')
        # 钱包支付
        data = wallet_make_new_pay(product, trade_no, agent_id, user_id, imei)
    else:
        raise ApiError('ERROR_PAY', error.ERROR_PAY)

    reply['data'] = data

    return make_response(jsonify(reply), status_code)


@api_blueprint.route('/pay/query', methods=["POST"])
@check_openid
def get_pay():
    dbg('get_pay')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        pay_id = data['pay_id']
    except:
        print_exception_info()
        raise ApiError('get pay error', error.ERROR_PARAM)

    pay = dbapi.get_pay(pay_id=pay_id)
    if not pay:
        raise ApiError('get pay error', error.ERROR_PAY_NOT_FOUND)

    data = {
        'trade_no': pay.trade_no,
        'title': pay.title,
        'body': pay.body,
        'total_fee': pay.total_fee,
        'time': int(pay.utime.timestamp()),
        'status': pay.status
    }
    reply['data'] = data

    return make_response(jsonify(reply), status_code)


@api_blueprint.route('/machine/restart', methods=['PATCH'])
@check_openid
def machine_restart():
    dbg('machine_restart')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        record_id = data['record_id']

    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    record = dbapi.get_record(record_id=record_id)
    if not record:
        dbg('record_id: %d' % record_id)
        raise ApiError('ERROR_RECORD_NOT_FOUND', error.ERROR_RECORD_NOT_FOUND)

    # pay = dbapi.get_pay(pay_id=record.pay_id)
    # imei = pay.imei

    # delta = record.etime - datetime.now()
    # value = delta.seconds
    # if value > 0:
    #     succ, result = launch_relay_signal_deivce_v2(imei, value)

    reply['data'] = {
            'id': record.id,
            'stime': int(record.stime.timestamp()),
            'etime': int(record.etime.timestamp()),
            'now': int(time.time())
        }

    return make_response(jsonify(reply), status_code)


@api_blueprint.route('/machine/start', methods=['PUT'])
@check_openid
def machine_start():
    dbg('machine_start')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        cat  = data['cat']
        pay_id = data['pay_id']

    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    pay = dbapi.get_pay(pay_id=pay_id)
    if not pay:
        raise ApiError('machine start error', error.ERROR_PAY_NOT_FOUND)

    imei = pay.imei

    if pay.status != 1:
        raise ApiError('machine start error', error.ERROR_NOT_PAY)

    product = dbapi.get_product(product_id=pay.product_id)
    if not product:
        raise ApiError('can not find product: %s' % pay.product_id)

    if product.cat == 99:
        raise ApiError('ERROR_PAY_NOT_FOUND', error.ERROR_PAY_NOT_FOUND)

    if product.cat == 0:
        # 倒计时限制同时支付
        last_pay = dbapi.get_last_pay(pay.imei, not_include_pay_id=pay_id)
        if last_pay and datetime.now().timestamp() - last_pay.utime.timestamp() < 5:
            # 退款
            pay_refund(pay, product)
            raise ApiError('ERROR_PAY_TOO_FREQUENCE', error.ERROR_PAY_TOO_FREQUENCE)
    
    

    dbg('cat: %s' % cat)
    device = dbapi.get_device(imei=imei)
    if not device:
        raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)

    value = product.value
    record = dbapi.get_record(pay_id=pay.id)
    if record:
        raise ApiError('machine start error', error.ERROR_ALREADY_START)

    high = device.high
    low = device.low
    cat = product.cat
    dbg('imei: %s, value: %d, cat: %d, high: %d, low: %d' % (imei, value, cat, low, high))

    cat = product.cat
    if cat in (0,):
        device_type = device.cat
        succ, result = launch_relay_signal_deivce_v2(imei, value, device_type)
    if cat in (2,):
        print('sending uart message..')
        succ, result = launch_uart_deivce_v2(imei, product.uart_val, product.uart_exp)

    elif cat == 1:
        if imei == '868575023189139' and value == 3:
            succ, result = launch_pulse_signal_deivce(imei, 2, high, low)
            time.sleep(2)
            succ, result = launch_pulse_signal_deivce(imei, 1, high, low)
        else:
            succ, result = launch_pulse_signal_deivce(imei, value, high, low)

    else:
        raise ApiError('not support')

    if not succ:
        # 退款
        pay_refund(pay, product)

        try:
            data = json.loads(result)
            dbg((data['code'], data['msg']))
            reply['code'] = data['code']
            reply['msg']  = data['msg']
            status_code = 422
        except:
            print_exception_info()
            reply['code'] = 99
            reply['msg']  = 'server error'
            status_code = 500
        return make_response(jsonify(reply), status_code)

    if cat == 0:
        # 按摩椅需要记录开始记录
        pay_way = pay.pay_mode
        stime = datetime.now()
        etime = stime + timedelta(seconds=product.value)
        record = dbapi.make_new_record(pay.id, pay_way, pay.user_id, 
            product.agent_id, pay.product_id, stime, etime)

    else:
        # 投币器也需要记录开始记录
        pay_way = pay.pay_mode
        stime = datetime.now()
        etime = stime
        record = dbapi.make_new_record(pay.id, pay_way, pay.user_id, 
            product.agent_id, pay.product_id, stime, etime)

    db.session.commit()

    reply['data'] = {
            'id': record.id,
            'stime': int(record.stime.timestamp()),
            'etime': int(record.etime.timestamp()),
            'now': int(time.time()),
            'user_id': record.user_id,
        }

    return make_response(jsonify(reply), status_code)


@api_blueprint.route('/machine/stop', methods=["PATCH"])
@check_openid
def mahcine_stop():
    dbg('machine_stop')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        imei = data['imei']
    except:
        print_exception_info()
        raise ApiError('get machine record error', error.ERROR_PARAM)

    device = dbapi.get_device(imei=imei)
    if not device:
        raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)

    record = dbapi.get_record(imei=imei, recent=1)
    if not record:
        raise ApiError('ERROR_RECORD_NOT_FOUND', error.ERROR_RECORD_NOT_FOUND)

    succ, result = launch_relay_signal_deivce_v2(imei, 0, device.cat)
    if not succ:
        try:
            data = json.loads(result)
            dbg((data['code'], data['msg']))
            reply['code'] = data['code']
            reply['msg']  = data['msg']
            status_code = 422
        except:
            print_exception_info()
            reply['code'] = 99
            reply['msg']  = 'server error'
            status_code = 500
        return make_response(jsonify(reply), status_code)

    try:
        record = dbapi.update_record(record, status=1)
        db.session.commit()
    except:
        db.session.rollback()
        raise

    now = int(time.time())
    etime = int(record.etime.timestamp())
    if record.status == 1:
        etime = now
    reply['data'] = {
        'id': record.id,
        'stime': int(record.stime.timestamp()),
        'etime': etime,
        'now': now,
        'user_id': record.user_id,
    }

    return make_response(jsonify(reply), status_code)


@api_blueprint.route('/nopay/count', methods=["POST"])
@check_openid
def get_nopay_count():
    dbg('get_nopay_count')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        imei  = data['imei']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    device = dbapi.get_device(imei=imei)
    if not device:
        raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)
    if not device.nopay:
        raise ApiError('ERROR_DEVICE_NOT_SUP_NOPAY', error.ERROR_DEVICE_NOT_SUP_NOPAY)

    user_id = g.oauth_user.user_id

    user_start_counter = dbapi.get_user_start_counter(user_id=user_id, imei=imei)
    if not user_start_counter:
        user_start_counter = dbapi.make_new_user_start_counter(user_id, imei)
        db.session.commit()

    user_start_counters = dbapi.get_user_start_counter(user_id=user_id, address_id=device.address_id)
    count = 0
    for user_start_counter in user_start_counters:
        count += user_start_counter.count

    reply['data'] = {
        'count': count,
        'nopay': device.nopay
    }

    return make_response(jsonify(reply), status_code)


@api_blueprint.route('/machine/start_nopay', methods=['PUT'])
@check_openid
def machine_start_nopay():
    dbg('machine_start_nopay')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        cat  = data['cat']
        imei  = data['imei']
        value = data['value']

    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    device = dbapi.get_device(imei=imei)
    if not device:
        raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)
    if not device.nopay:
        raise ApiError('ERROR_DEVICE_NOT_SUP_NOPAY', error.ERROR_DEVICE_NOT_SUP_NOPAY)

    user_id = g.oauth_user.user_id

    user_start_counter = dbapi.get_user_start_counter(user_id=user_id, imei=imei)
    if not user_start_counter:
        user_start_counter = dbapi.make_new_user_start_counter(user_id, imei)
        db.session.commit()

    user_start_counters = dbapi.get_user_start_counter(user_id=user_id, address_id=device.address_id)
    count = 0
    for counter in user_start_counters:
        count += counter.count

    if count >= device.nopay:
        raise ApiError('ERROR_NOPAY_NOT_ENOUGH', error.ERROR_NOPAY_NOT_ENOUGH)

    agent_id = device.agent_id

    wechat_config   = dbapi.get_wechat_config(imei=imei)
    appid           = wechat_config.appid
    appsecret       = wechat_config.appsecret
    openid          = session['openid']

    wechat_info     = wechatsdk.get_wechat_user_info(appid, appsecret, openid)

    if not wechat_info or wechat_info['subscribe'] != 1:
        raise ApiError('ERROR_WECHAT_NOT_SUBSCRIBE', error.ERROR_WECHAT_NOT_SUBSCRIBE)

    if cat in (0, 2, 3):
        device_type = device.cat
        succ, result = launch_relay_signal_deivce_v2(imei, value, device_type)
        if not succ:
            try:
                data = json.loads(result)
                dbg((data['code'], data['msg']))
                reply['code'] = data['code']
                reply['msg']  = data['msg']
                status_code = 422
            except:
                print_exception_info()
                reply['code'] = 99
                reply['msg']  = 'server error'
                status_code = 500
            return make_response(jsonify(reply), status_code)

        stime = datetime.now()
        etime = stime + timedelta(seconds=value)
        # 1. 记录开始记录
        record = dbapi.make_new_record_no_pay(imei, user_id,
            agent_id, stime, etime)
        db.session.commit()

        reply['data'] = {
            'id': record.id,
            'stime': int(record.stime.timestamp()),
            'etime': int(record.etime.timestamp())
        }

    elif cat == 1:
        # 娃娃机
        value = 1

        succ, result = launch_pulse_signal_deivce(imei, value, device.high, device.low)
        if not succ:
            try:
                data = json.loads(result)
                dbg((data['code'], data['msg']))
                reply['code'] = data['code']
                reply['msg']  = data['msg']
                status_code = 422
            except:
                print_exception_info()
                reply['code'] = 99
                reply['msg']  = 'server error'
                status_code = 500
            return make_response(jsonify(reply), status_code)

        stime = datetime.now()
        etime = stime
        # 1. 记录开始记录
        record = dbapi.make_new_record_no_pay(imei, user_id,
            agent_id, stime, etime)
        db.session.commit()

    # 记录启动次数
    count = user_start_counter.count + 1
    user_start_counter = dbapi.update_user_counter(user_start_counter, count=count)
    db.session.commit()

    return make_response(jsonify(reply), status_code)


@api_blueprint.route('/machine/start_coupon_nopay', methods=['PUT'])
@check_openid
def machine_start_coupon_nopay():
    dbg('machine_start_coupon_nopay')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        cat  = data['cat']
        imei  = data['imei']
        value = data['value']

    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    device = dbapi.get_device(imei=imei)
    if not device:
        raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)
    if not device.coupon:
        raise ApiError('ERROR_DEVICE_NOT_SUP_NOPAY', error.ERROR_DEVICE_NOT_SUP_NOPAY)

    user_id = g.oauth_user.user_id

    receipt = None
    coupon_receipts = dbapi.get_coupon_receipt(device_id=device.id, user_id=user_id)
    for coupon_receipt in coupon_receipts:
        if coupon_receipt.started == 0:
            receipt = coupon_receipt

    if not receipt:
        raise ApiError('ERROR_NOPAY_NOT_ENOUGH', error.ERROR_NOPAY_NOT_ENOUGH)

    agent_id = device.agent_id

    if cat in (0, 2, 3):
        device_type = device.cat
        succ, result = launch_relay_signal_deivce_v2(imei, value, device_type)
        if not succ:
            try:
                data = json.loads(result)
                dbg((data['code'], data['msg']))
                reply['code'] = data['code']
                reply['msg']  = data['msg']
                status_code = 422
            except:
                print_exception_info()
                reply['code'] = 99
                reply['msg']  = 'server error'
                status_code = 500
            return make_response(jsonify(reply), status_code)

        stime = datetime.now()
        etime = stime + timedelta(seconds=value)
        # 1. 记录开始记录
        record = dbapi.make_new_record_coupon_no_pay(imei, user_id,
            agent_id, stime, etime)
        db.session.commit()

        reply['data'] = {
            'id': record.id,
            'stime': int(record.stime.timestamp()),
            'etime': int(record.etime.timestamp())
        }

    elif cat == 1:
        # 娃娃机
        value = 1

        succ, result = launch_pulse_signal_deivce(imei, value, device.high, device.low)
        if not succ:
            try:
                data = json.loads(result)
                dbg((data['code'], data['msg']))
                reply['code'] = data['code']
                reply['msg']  = data['msg']
                status_code = 422
            except:
                print_exception_info()
                reply['code'] = 99
                reply['msg']  = 'server error'
                status_code = 500
            return make_response(jsonify(reply), status_code)

        stime = datetime.now()
        etime = stime
        # 1. 记录开始记录
        record = dbapi.make_new_record_coupon_no_pay(imei, user_id,
            agent_id, stime, etime)
        db.session.commit()

    # 记录优惠券已启动
    receipt = dbapi.update_coupon_receipt(receipt, started=1)
    db.session.commit()

    return make_response(jsonify(reply), status_code)


@api_blueprint.route('/machine/record', methods=["POST"])
def get_machine_record():
    dbg('get_machine_record')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        imei = data['imei']
    except:
        print_exception_info()
        raise ApiError('get machine record error', error.ERROR_PARAM)

    record = dbapi.get_record(imei=imei, recent=1)
    if not record:
        raise ApiError('ERROR_RECORD_NOT_FOUND', error.ERROR_RECORD_NOT_FOUND)

    now = int(time.time())
    etime = int(record.etime.timestamp())
    if record.status == 1:
        etime = now
    reply['data'] = {
        'id': record.id,
        'stime': int(record.stime.timestamp()),
        'etime': etime,
        'now': now,
        'user_id': record.user_id,
    }

    return make_response(jsonify(reply), status_code)


@api_blueprint.route('/machine/record_nopay', methods=["POST"])
def get_machine_record_nopay():
    dbg('get_machine_record_nopay')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        record_id = data['record_id']
    except:
        print_exception_info()
        raise ApiError('get machine record error', error.ERROR_PARAM)

    dbg((record_id, type(record_id)))
    record = dbapi.get_record_no_pay(id=record_id)
    if not record:
        raise ApiError('ERROR_RECORD_NOT_FOUND', error.ERROR_RECORD_NOT_FOUND)

    reply['data'] = {
        'id': record.id,
        'stime': int(record.stime.timestamp()),
        'etime': int(record.etime.timestamp())
    }

    return make_response(jsonify(reply), status_code)


@api_blueprint.route('/machine/record_coupon_nopay', methods=["POST"])
def get_machine_record_coupon_nopay():
    dbg('get_machine_record_coupon_nopay')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        record_id = data['record_id']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    dbg((record_id, type(record_id)))
    record = dbapi.get_record_coupon_no_pay(id=record_id)
    if not record:
        raise ApiError('ERROR_RECORD_NOT_FOUND', error.ERROR_RECORD_NOT_FOUND)

    reply['data'] = {
        'id': record.id,
        'stime': int(record.stime.timestamp()),
        'etime': int(record.etime.timestamp())
    }

    return make_response(jsonify(reply), status_code)


@api_blueprint.route('/coupon_receipt/random', methods=["POST"])
@check_openid
def random_get_coupon_receipt():
    dbg('random_get_coupon_receipt')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        imei = data['imei']
    except:
        print_exception_info()
        raise ApiError('get machine record error', error.ERROR_PARAM)

    device = dbapi.get_device(imei=imei)
    if not device:
        raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)

    coupons = dbapi.get_coupon(device_id=device.id, paid=1, inventory=1)
    if coupons:
        coupon = random.choice(coupons)
        coupon_id = coupon.id
        code = gen_coupon_receipt_code(coupon_id, coupon.prefix)
        user_id = g.oauth_user.user_id
        coupon_receipt = dbapi.make_new_coupon_receipt(coupon_id, user_id, code)
        product = dbapi.get_product(product_id=coupon.product_id)
        if product.inventory <= 0:
            raise ApiError('ERROR_COUPON_NO_AVAILABLE', error.ERROR_COUPON_NO_AVAILABLE)
        product = dbapi.update_product(product, inventory=product.inventory-1)
        color   = get_boxed_reverse_color(coupon.img)
        reply['data'] = {
            'img': url_for('static', filename=coupon.img),
            'code': code,
            'color': color
        }
    else:
        raise ApiError('ERROR_COUPON_NO_AVAILABLE', error.ERROR_COUPON_NO_AVAILABLE)

    db.session.commit()

    return make_response(jsonify(reply), status_code)


@api_blueprint.route('/pay/notify/', methods=['POST'])
def pay_notify():
    dbg('pay_notify')
    reply = {"return_code": 'SUCCESS', "return_msg": ""}

    try:
        data_info = request.data.decode('utf8')
        data = wechatpay.xml_to_dict(data_info)
        nofity_res = json.dumps(data)
        dbg('data_info: %s' % data_info)

        return_code = None
        result_code = None

        if "result_code" in data and "return_code" in data:
            return_code = data["return_code"]
            result_code = data["result_code"]

        if return_code != "SUCCESS":
            raise ApiError('wechat interface return error')

        # return_code为`SUCCESS`, 则包含out_trade_no

        # 检查订单
        trade_no = data['out_trade_no']
        pay  = dbapi.get_pay(trade_no=trade_no)
        if not pay:
            raise ApiError('can not find pay: %s' % trade_no)

        # 如果已经支付，则直接返回Ok
        if pay.status > 0:
            return make_response(wechatpay.dict_to_xml(reply).encode('utf-8'))

        # 检查签名
        sign = data['sign']
        data.pop('sign')
        wechat_config = dbapi.get_wechat_config(agent_id=pay.agent_id)
        key = wechat_config.mchkey
        local_sign = wechatpay.params_sign(data, key)
        data['sign'] = sign
        dbg((sign, local_sign))
        if sign != local_sign:
            raise ApiError('sign error')

        if result_code != "SUCCESS":
            '''
                ``` 支付失败, 更新支付异常
            '''
            dbapi.update_pay(pay, status=2, nofity_res=nofity_res)

            try:
                db.session.commit()
            except:
                print_exception_info()
                db.session.rollback()
                raise ApiError('pay_notify error')

        else:
            '''
                ``` 支付成功, 并更新支付成功
            '''
            cash_fee = data['cash_fee']
            dbapi.update_pay(pay=pay, status=1, cash_fee=cash_fee, nofity_res=nofity_res)
            product = dbapi.get_product(product_id=pay.product_id)
            if product.cat == 99:
                # 钱包充值
                user_id = pay.user_id
                wallet = dbapi.get_wallet(role=0, user_id=user_id, agent_id=pay.agent_id)
                wallet_id = wallet.id
                trade_type = dbapi.WALLET_TRADE_TYPE_DEPOSIT
                receipt = product.value
                withdrawable_receipt = 0
                remark = product.title
                wallet_receipt = dbapi.make_new_wallet_receipt(user_id, pay.agent_id, wallet_id,
                                                               trade_type, receipt,
                                                               withdrawable_receipt, remark)

                balance = wallet.balance + receipt
                wallet = dbapi.update_wallet(wallet, balance=balance)

            if product.cat == dbapi.PRODUCT_CAT_COUPON:
                # 优惠券
                coupon = dbapi.get_coupon(pay_id=pay.id)
                if coupon:
                    coupon = dbapi.update_coupon(coupon, paid=1)

            wechat_pay_receipt(pay)

            try:
                db.session.commit()
            except:
                print_exception_info()
                db.session.rollback()
                raise ApiError('wechat_pay_notify error', error.ERROR_DATABASE_COMMIT)

    except ApiError as e:
        # if e.msg != 'wechat pay failed':
        print_exception_info()
        reply['return_code'] = "FAIL"
        reply['return_msg']  = e.msg
    except:
        print_exception_info()
        reply['return_code'] = "FAIL"
        reply['return_msg']  = 'server error'

    res_data = wechatpay.dict_to_xml(reply).encode('utf-8')
    print(res_data)
    return make_response(res_data)


@api_blueprint.route('/ali_notify', methods=["GET", 'POST'])
def ali_notify():
    dbg('ali_notify')

    reply = {"return_code": 'SUCCESS', "return_msg": ""}

    try:
        trade_no = request.form['out_trade_no']
        nofity_res = {}
        for k in request.form:
            print(k, request.form[k])
            nofity_res[k] = request.form[k]
        trade_status = request.form['trade_status']
        ali_trade_no = request.form['trade_no']
        buyer_id = request.form['buyer_id']
        buyer_logon_id = request.form['buyer_logon_id']
        cash_fee = request.form.get('buyer_pay_amount') or request.form['total_amount']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    # 检查订单
    pay = dbapi.get_pay(trade_no=trade_no)
    if not pay:
        raise ApiError('can not find pay: %s' % trade_no)

    # 签名
    # sign = request.form['sign']
    # ali_config = dbapi.get_ali_config(agent_id=int(agent_id))
    # key_path   = ali_config.pub_path

    # 如果已经支付，则直接返回Ok
    if pay.status > 0:
        return make_response('success')

    if trade_status == 'TRADE_CLOSED':
        dbapi.update_pay(pay, user_id=pay.user_id, status=2, nofity_res=json.dumps(nofity_res))
        try:
            db.session.commit()
        except:
            print_exception_info()
            db.session.rollback()
            raise ApiError('ali_notify error')

    elif trade_status == 'TRADE_SUCCESS':
        dbapi.update_pay(pay=pay, user_id=pay.user_id, status=1, cash_fee=cash_fee, nofity_res=json.dumps(nofity_res), ali_trade_no=ali_trade_no)
        product = dbapi.get_product(product_id=pay.product_id)
        if product.cat == 99:
            # 钱包充值
            user_id = pay.user_id
            wallet = dbapi.get_wallet(role=0, user_id=user_id, agent_id=pay.agent_id)
            wallet_id = wallet.id
            trade_type = dbapi.WALLET_TRADE_TYPE_DEPOSIT
            receipt = product.value
            withdrawable_receipt = 0
            remark = product.title
            wallet_receipt = dbapi.make_new_wallet_receipt(user_id, pay.agent_id, wallet_id,
                                                           trade_type, receipt,
                                                           withdrawable_receipt, remark)

            balance = wallet.balance + receipt
            wallet = dbapi.update_wallet(wallet, balance=balance)

        wechat_pay_receipt(pay)

        try:
            db.session.commit()
        except:
            print_exception_info()
            db.session.rollback()
            raise ApiError('ali_notify error', error.ERROR_DATABASE_COMMIT)

    return make_response('success')


# @api_blueprint.route('/test_refund', methods=["POST"])
# def test_refund():
#     dbg('test_refund')
#     reply ,status_code = {'code': 0, 'msg': ''}, 200

#     data = request.get_json()
#     pay_id = data['pay_id']

#     pay = dbapi.get_pay(pay_id=pay_id)
#     product = dbapi.get_product(product_id=pay.product_id)

#     # 按摩椅退款
#     appid = config.WECHAT_LIST[product.agent_id].APP_ID
#     mchid = config.WECHAT_LIST[product.agent_id].WECHAT_MCH_ID

#     max_id  = dbapi.get_max_refund_id()
#     str_max_id = '%04d' % max_id
#     if len(str_max_id) > 4:
#         str_max_id = str_max_id[-4:]
#     refund_no = 'R' + str(int(time.time())) + str_max_id

#     refund = dbapi.make_new_refund(pay.user_id, pay.id, refund_no, 
#         pay.total_fee, pay.total_fee)
#     db.session.commit()
#     if refund.id:
#         kwargs = {
#             'appid': appid,
#             'mchid': mchid,
#             'trade_no': pay.trade_no,
#             'refund_no': refund_no,
#             'total_fee': pay.total_fee,
#             'refund_fee': pay.total_fee,
#             'agent_id': product.agent_id
#         }
#         err, res = wechatpay.refund_request(**kwargs)
#         if not err:
#             refund = dbapi.update_refund(refund, nofity_res=res, status=1)
#         else:
#             dbg(err)
#             refund = dbapi.update_refund(refund, nofity_res=res, status=2)
#         db.session.commit()
    # return make_response(jsonify(reply), status_code)


# @api_blueprint.route('/test_pay_to_user')
# def test_refund():
#     dbg('test_refund')
#     reply ,status_code = {'code': 0, 'msg': ''}, 200

#     kwargs = {
#         'openid': 'oEMOtjoiv9HBQiAC7x7BnSDAUuVw',
#         'trade_no': 'paytest123',
#         'money': 100,
#         'desc': '取现',
#         'agent_id': 1
#     }
#     err, result = wechatpay.pay_to_user(**kwargs)
#     print(err)
#     print(result)
    
#     return make_response(jsonify(reply), status_code)


# @api_blueprint.route('/test_wechat_pay')
# def test_pay():
#     dbg('test_pay')
#     reply ,status_code = {'code': 0, 'msg': ''}, 200

#     params = {
#         'body': 'body',
#         'out_trade_no': 'test%d' % int(time.time()),
#         'total_fee': 1,
#         'spbill_create_ip': current_app.config['SELF_IP'],
#         'notify_url': 'http://wxapp.mafu.shop/api/test_wechat_notify',
#         'trade_type': "NATIVE",
#         'agent_id': "1"
#     }
#     err, payRequest = wechatpay.get_native_pay_request(**params)
#     if not err:
#         reply['data'] = payRequest
#     else:
#         reply['data'] = err

#     return make_response(jsonify(reply), status_code)


# @api_blueprint.route('/test_wechat_notify', methods=['POST'])
# def test_wechat_notify():
#     dbg('test_wechat_notify')
#     reply = {"return_code": 'SUCCESS', "return_msg": ""}

#     data_info = request.data.decode('utf8')
#     data = wechatpay.xml_to_dict(data_info)
#     nofity_res = json.dumps(data)
#     dbg('data_info: %s' % data_info)

#     res_data = wechatpay.dict_to_xml(reply).encode('utf-8')
#     print(res_data)
#     return make_response(res_data)


# @api_blueprint.route('/test_recalc_income')
# def test_recalc_income():
#     dbg('test_recalc_income')
#     reply ,status_code = {'code': 0, 'msg': ''}, 200

#     pays = dbapi.db.session.query(dbapi.Pay).filter(dbapi.Pay.status==1)

#     for pay in pays:
#         wechat_pay_receipt(pay)
#     db.session.commit()

#     return make_response(jsonify(reply), status_code)


# @api_blueprint.route('/test_init_device_distribution')
# def test_init_device_distribution():
#     dbg('test_init_device_distribution')
#     reply ,status_code = {'code': 0, 'msg': ''}, 200

#     query = dbapi.db.session.query(dbapi.Device)
#     count = query.count()
#     devices = query.all()
#     print(count)

#     for device in devices:
#         dbapi.make_new_device_distribution(device.id, device.imei, 
#             0, device.agent_id)
#         if device.agent_id != device.owner_agent_id:
#             dbapi.make_new_device_distribution(device.id, device.imei, 
#                 device.agent_id, device.owner_agent_id)
#     dbapi.db.session.commit()

#     return make_response(jsonify(reply), status_code)
