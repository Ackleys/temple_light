#!/usr/bin/env python3
# coding: utf8
# 20170220 anChaOs


# general
import os, json, time, calendar
import requests # for http requests
from datetime import datetime, timedelta, date

# Pillow
from PIL import Image

# wraps
from functools import wraps

# flask
from flask import Flask, request, session, jsonify, current_app, g
from flask import redirect, url_for, render_template, make_response

# flask-login
from flask_login import login_user, logout_user, current_user
from flask_login import login_required, LoginManager

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

from app.tool import dbg                    # for print
from app.tool import print_exception_info   # for traceback
import app.tool as tool

# wechat
import app.third_party.wechatsdk as wechatsdk
import app.third_party.wechatpay as wechatpay

# blueprint
from . import admin_advertiser_blueprint
from app.admin.device_views import agent_id_required


@admin_advertiser_blueprint.errorhandler(ApiError)
def handle_api_error(current_error):
    dbg((current_error.msg, current_error.error_no))
    error_info = error.get_error_info(current_error.error_no)
    return make_response(jsonify({'code':current_error.error_no, 'msg':error_info[0]}), error_info[1])


@admin_advertiser_blueprint.errorhandler(Exception)
def handle_base_exception(current_error):
    print_exception_info()
    return make_response(json.dumps({'code':99, 'msg':'server error'}), 500)


def advertiser_required(func):
    @wraps(func)
    def wrapper(*args, **kws):
        advertiser = dbapi.get_advertiser(user_id=current_user.id)
        if not advertiser:
            raise ApiError('ERROR_ADVERTISER_NOT_FOUND', error.ERROR_ADVERTISER_NOT_FOUND)
        current_user.cur_advertiser = advertiser
        return func(*args, **kws)
    return wrapper


@admin_advertiser_blueprint.route('/cur')
@login_required
def get_cur_advertiser():
    dbg('get_cur_advertiser')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    advertiser = dbapi.get_advertiser(user_id=user_id)
    if not advertiser:
        raise ApiError('ERROR_AGENT_NOT_FOUND', error.ERROR_AGENT_NOT_FOUND)
    reply['data'] = {
        'id': advertiser.id,
        'name': advertiser.name,
        'phone': advertiser.phone,
        'email': advertiser.email,
        'desc': advertiser.desc,
        'address': advertiser.address,
        'remark': advertiser.remark
    }
    return make_response(jsonify(reply), status_code)


@admin_advertiser_blueprint.route('/add', methods=["PUT"])
@login_required
@agent_id_required
def add_advertiser():
    dbg('add_advertiser')
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    try:
        data    = request.get_json()
        name    = data['name']
        email   = data['email']
        phone   = data['phone']
        address = data['address']
        desc    = data['desc']
        remark  = data['remark']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    target_advertiser = dbapi.get_advertiser(phone=phone)
    if target_advertiser:
        raise ApiError('ERROR_PHONE_EXISTS', error.ERROR_PHONE_EXISTS)

    agent = dbapi.get_agent(phone=phone)
    if agent:
        raise ApiError('ERROR_PHONE_EXISTS', error.ERROR_PHONE_EXISTS)

    openluat_user = dbapi.get_openluat_user(phone=phone)
    if not openluat_user:
        openluat_user = dbapi.make_new_openluat_user(name, email, phone)
        db.session.commit()

    agent_id = current_user.agent_id
    hook_agent_id = agent_id
    new_agent = dbapi.make_new_advertiser(openluat_user.id, hook_agent_id,
        name, phone, email, desc, address, remark)
    db.session.commit()

    return make_response(jsonify(reply), status_code)


@admin_advertiser_blueprint.route('/fetch', methods=['POST'])
@login_required
def get_advertiser_info():
    dbg('get_advertiser_info')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data     = request.get_json()
        advertiser_id = data['advertiser_id']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    advertiser = dbapi.get_advertiser(id=advertiser_id)
    if not advertiser:
        raise ApiError('ERROR_ADVERTISER_NOT_FOUND', error.ERROR_ADVERTISER_NOT_FOUND)

    reply['data'] = {
        'id': advertiser.id,
        'name': advertiser.name,
        'phone': advertiser.phone,
        'email': advertiser.email,
        'desc': advertiser.desc,
        'address': advertiser.address,
        'remark': advertiser.remark
    }
    return make_response(jsonify(reply), status_code)


@admin_advertiser_blueprint.route('/agent_sub/fetch', methods=["POST"])
@login_required
def get_agent_sub_advertiser():
    dbg('get_agent_sub_advertiser')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data     = request.get_json()
        agent_id = data['agent_id']
        page  = request.args.get('page', 1, type=int)
        psize = request.args.get('psize', 10, type=int)
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    count, advertisers = dbapi.get_advertiser(hook_agent_id=agent_id, page=page, psize=psize)

    data = []
    if count:
        for advertiser in advertisers:
            info = {
                'id': advertiser.id,
                'name': advertiser.name,
                'phone': advertiser.phone,
                'email': advertiser.email,
                'desc': advertiser.desc,
                'address': advertiser.address,
                'remark': advertiser.remark
            }
            data.append(info)

    reply['data'] = {
        'count': count,
        'advertisers': data
    }

    return make_response(jsonify(reply), status_code)


@admin_advertiser_blueprint.route('/update', methods=["PATCH"])
@login_required
def update_advertiser():
    dbg('update_advertiser')
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    try:
        data     = request.get_json()
        advertiser_id = data['advertiser_id']
        update   = data['update']
        keys = ('desc', 'address', 'remark')
        for k in update:
            assert(k in keys)
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    advertiser = dbapi.get_advertiser(id=advertiser_id)
    if not advertiser:
        raise ApiError('ERROR_ADVERTISER_NOT_FOUND', error.ERROR_ADVERTISER_NOT_FOUND)

    advertiser = dbapi.update_advertiser(advertiser, **update)
    db.session.commit()

    return make_response(jsonify(reply), status_code)


@admin_advertiser_blueprint.route('/coupon/add', methods=['POST'])
@login_required
@agent_id_required
def add_coupon():
    dbg('add_coupon')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        advertiser_id = request.form['advertiser_id']
        title       = request.form['title']
        desc        = request.form['desc']
        price       = request.form['price']
        total       = request.form['total']

        imag_file   = request.files['0']

    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    advertiser = dbapi.get_advertiser(id=int(advertiser_id))
    if not advertiser:
        raise ApiError('ERROR_ADVERTISER_NOT_FOUND', error.ERROR_ADVERTISER_NOT_FOUND)

    # check img
    im = Image.open(imag_file)
    w, h = im.size
    ratio = w / h

    if ratio > 0.53 or ratio < 0.47:
        raise ApiError('ERROR_IMG_SIZE_NOT_MATCH', error.ERROR_IMG_SIZE_NOT_MATCH)

    # 创建product
    value, cat = 0, dbapi.PRODUCT_CAT_COUPON
    product = dbapi.make_new_product(advertiser.hook_agent_id, title,
        desc, value, cat, price, total)
    db.session.commit()

    # 创建订单
    pay_mode = 1 # 默认微信支付
    trade_no = gen_coupon_order_no(advertiser.openluat_user_id, pay_mode)
    data = wechat_qrcode_make_new_pay(product, trade_no, advertiser.openluat_user_id)

    # 创建coupon
    coupon_img = get_coupon_img(advertiser.id, im, 'jpg')
    prefix = gen_coupon_prefix(title+desc)
    if not prefix:
        raise ApiError('gen prefix failed')
    pay_id = data['id']
    agent_id = current_user.agent_id
    coupon = dbapi.make_new_coupon(agent_id, advertiser.id, product.id, pay_id, 
        title, desc, prefix, total, coupon_img)

    db.session.commit()

    return make_response(jsonify(reply), status_code)


@admin_advertiser_blueprint.route('/coupon/pay', methods=["POST"])
@login_required
@advertiser_required
def pay_coupon():
    dbg('pay_coupon')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        coupon_id = data['coupon_id']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    coupon = dbapi.get_coupon(id=coupon_id)
    if not coupon:
        raise ApiError('ERROR_COUPON_NOT_FOUND', error.ERROR_COUPON_NOT_FOUND)

    pay    = dbapi.get_pay(pay_id=coupon.pay_id)
    if not pay:
        raise ApiError('ERROR_PAY_NOT_FOUND', error.ERROR_PAY_NOT_FOUND)

    if pay.status != 0 or coupon.paid:
        raise ApiError('ERROR_ALREADY_PAID', error.ERROR_ALREADY_PAID)

    if int(datetime.now().timestamp()) - int(pay.utime.timestamp()) >= 2*60*60:
        product = dbapi.get_product(product_id=coupon.product_id)
        trade_no = pay.trade_no
        pay = wechat_qrcode_update(pay, product, trade_no, current_user.id)

    reply['data'] = {
        'pay_request': {
            'prepay_id': pay.prepay_id,
            'qrcode': pay.qrcode
        },
        'trade_no'   : pay.trade_no,
        'id'         : pay.id
    }

    return make_response(jsonify(reply), status_code)


@admin_advertiser_blueprint.route('/pay/query', methods=["POST"])
@login_required
@advertiser_required
def get_coupon_pay():
    dbg('get_coupon_pay')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        pay_id = data['pay_id']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    pay = dbapi.get_pay(pay_id=pay_id)
    if not pay:
        raise ApiError('ERROR_PAY_NOT_FOUND', error.ERROR_PAY_NOT_FOUND)

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


@admin_advertiser_blueprint.route('/coupon/fetch', methods=["POST"])
@login_required
def get_coupon():
    dbg('get_coupon')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        advertiser_id = data.get('advertiser_id')
        device_id = data.get('device_id')
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    page  = request.args.get('page', 1, type=int)
    psize = request.args.get('psize', 10, type=int)

    data = []

    if advertiser_id:
        count, coupons = dbapi.get_coupon(advertiser_id=int(advertiser_id), page=page, psize=psize)
    elif device_id:
        count, coupons = dbapi.get_coupon(device_id=int(device_id), page=page, psize=psize)
    else:
        agent = dbapi.get_agent(user_id=current_user.id)
        if not agent:
            raise ApiError('ERROR_AGENT_NOT_FOUND', error.ERROR_AGENT_NOT_FOUND)
        agent_id = agent.id
        count, coupons = dbapi.get_coupon(agent_id=agent_id, page=page, psize=psize)

    if count:
        for coupon in coupons:
            product = dbapi.get_product(product_id=coupon.product_id)
            pay     = dbapi.get_pay(pay_id=coupon.pay_id)
            info = {
                'id': coupon.id,
                'title': coupon.title,
                'desc': coupon.desc,
                'img': url_for('static', filename=coupon.img),
                'total': coupon.total,
                'left': product.inventory,
                'pay_status': pay.status,
                'time': int(coupon.ctime.timestamp())
            }
            data.append(info)

    reply['data'] = {
        'count': count,
        'coupons': data
    }

    return make_response(jsonify(reply), status_code)


@admin_advertiser_blueprint.route('/device/multi/add/coupon', methods=["PATCH"])
@login_required
def device_multi_add_coupon():
    dbg('device_multi_add_coupon')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        device_ids = data['device_ids']
        device_ids = list(set(device_ids))
        coupon_id = data['coupon_id']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    coupon = dbapi.get_coupon(id=coupon_id)
    if not coupon:
        raise ApiError('ERROR_COUPON_NOT_FOUND', error.ERROR_COUPON_NOT_FOUND)

    for device_id in device_ids:
        device = dbapi.get_device(id=device_id)
        if not device:
            db.session.rollback()
            dbg('device_id: %s not exists' % device_id)
            reply['code'] = 999
            reply['msg'] = '自编号: %s 不存在' % device_id
            status_code = 422
            return make_response(jsonify(reply), status_code)

        device_coupon = dbapi.get_device_coupon(device_id=device_id, coupon_id=coupon_id)
        if device_coupon:
            db.session.rollback()
            dbg('device_id: %d added before' % device_id)
            reply['code'] = 999
            reply['msg'] = '自编号: %s 已添加该优惠券' % device_id
            status_code = 422
            return make_response(jsonify(reply), status_code)
        else:
            # 建立设备和优惠券之间的联系
            device_coupon = dbapi.make_new_device_coupon(coupon_id, device_id)

            # 更新pay表中的imei，用户查询订单收益
            pay = dbapi.get_pay(pay_id=coupon.pay_id)
            pay = dbapi.update_pay(pay, imei=device.imei)

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise

    return make_response(jsonify(reply), status_code)


@admin_advertiser_blueprint.route('/device/coupon/fetch')
@login_required
@agent_id_required
def get_coupon_devices():
    dbg('get_coupon_devices')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    page  = request.args.get('page', 1, type=int)
    psize = request.args.get('psize', 10, type=int)
    address_id = request.args.get('address_id', 0, type=int)

    agent_id = current_user.agent_id
    count = 0
    data = []
    count, devices = dbapi.get_device(owner_agent_id=agent_id, 
        page=page, psize=psize, coupon=1, address_id=address_id)
    if count:
        if devices:
            for device in devices:
                device_address = dbapi.get_device_address(id=device.address_id)
                address = ""
                if device_address:
                    address = device_address.address
                device_coupons = dbapi.get_device_coupon(device_id=device.id)
                coupons = list(map(lambda x:x.coupon_id, device_coupons))
                info = {
                    'id': device.id,
                    'imei': device.imei,
                    'cat': device.cat,
                    'address': address,
                    'remark': device.remark,
                    'coupon': device.coupon,
                    'coupons': coupons
                }
                data.append(info)

    reply['data'] = {
        'count': count,
        'devices': data
    }

    return make_response(jsonify(reply), status_code)


@admin_advertiser_blueprint.route('/coupon_receipt/search', methods=["POST"])
@login_required
def search_coupon_receipt():
    dbg('search_coupon_receipt')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        code = data['code']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    coupon_receipt = dbapi.get_coupon_receipt(code=code)

    reply['data'] = {
        'used' : coupon_receipt.used,
        'time' : int(coupon_receipt.utime.timestamp())
    }

    return make_response(jsonify(reply), status_code)


@admin_advertiser_blueprint.route('/coupon_receipt/use', methods=["PATCH"])
@login_required
def use_coupon_receipt():
    dbg('use_coupon_receipt')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        code = data['code']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    coupon_receipt = dbapi.get_coupon_receipt(code=code)
    if coupon_receipt.used:
        raise ApiError('ERROR_COUPON_RECEIPT_ALREADY_USED', error.ERROR_COUPON_RECEIPT_ALREADY_USED)

    coupon_receipt = dbapi.update_coupon_receipt(coupon_receipt, used=1)
    db.session.commit()

    return make_response(jsonify(reply), status_code)