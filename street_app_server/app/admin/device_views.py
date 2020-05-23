#!/usr/bin/env python3
# coding: utf8
# 20170220 anChaOs


# general
import os, json, time, math
import requests # for http requests
from datetime import datetime, timedelta, date

# wraps
from functools import wraps

# Pillow
from PIL import Image

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

from app.tool import dbg                    # for print
from app.tool import print_exception_info   # for traceback
from app.tool import gen_imei15             # for gen imei

# wechat
import app.third_party.wechatsdk as wechatsdk
import app.third_party.wechatpay as wechatpay

# blueprint
from . import admin_device_blueprint


def gen_serial_imei(start_imei, num):
    prefix = start_imei[:-5]
    delta  = int(start_imei[-5:-1])
    imeis = [start_imei]
    for i in range(int(num)-1):
        imei14 = prefix + str(delta+i+1)
        try:
            imei = gen_imei15(imei14)
        except ValueError as e:
            dbg(e)
            raise ApiError('gen serial imei error', error.ERROR_INVALIDATE_IMEI)
        imeis.append(imei)
    return imeis


@admin_device_blueprint.errorhandler(ApiError)
def handle_api_error(current_error):
    dbg((current_error.msg, current_error.error_no))
    error_info = error.get_error_info(current_error.error_no)
    return make_response(jsonify({'code':current_error.error_no, 'msg':error_info[0]}), error_info[1])


@admin_device_blueprint.errorhandler(Exception)
def handle_base_exception(current_error):
    print_exception_info()
    return make_response(json.dumps({'code':99, 'msg':'server error'}), 500)


def agent_id_required(func):
    @wraps(func)
    def wrapper(*args, **kws):
        agent = dbapi.get_agent(user_id=current_user.id)
        if not agent:
            raise ApiError('ERROR_AGENT_NOT_FOUND', error.ERROR_AGENT_NOT_FOUND)
        current_user.agent_id = agent.id
        current_user.cur_agent = agent
        return func(*args, **kws)
    return wrapper


@admin_device_blueprint.route('/cat')
@login_required
def get_device_cat():
    dbg('get_device_cat')
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    data = {
        0: '倒计时',
        1: '投币器',
    }
    reply['data'] = data
    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/add', methods=["PUT"])
@login_required
@agent_id_required
def add_device():
    dbg('add_device')
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    try:
        data = request.get_json()
        imei  = data['imei']
        cat = data['cat']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    if len(imei) != 15:
        raise ApiError('ERROR_INVALIDATE_IMEI', error.ERROR_INVALIDATE_IMEI)

    agent_id = current_user.agent_id
    agent = dbapi.get_agent(id=agent_id)
    if not agent or agent.level != 4:
        raise ApiError('ERROR_AGENT_NO_PERMISSION', error.ERROR_AGENT_NO_PERMISSION)

    device = dbapi.get_device(imei=imei)
    if device:
        if device.agent_id != 0:
            raise ApiError('ERROR_DEVICE_EXISTS', error.ERROR_DEVICE_EXISTS)
        else:
            # update device
            device.agent_id = agent_id
            device.owner_agent_id = agent_id
            device.cat = cat
    else:
        address_id = 0
        device = dbapi.make_new_device(imei, cat, agent_id, address_id)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise
    if not device:
        raise Exception('add device db error')

    data = {}
    if device:
        # 添加第一次设备分销
        from_agent, to_agent = 0, agent_id
        dbapi.make_new_device_distribution(
            device.id, device.imei, from_agent, to_agent)
        data = {
            'id': device.id,
            'imei': device.imei,
            'cat': device.cat
        }

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise

    reply['data'] = data

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/search', methods=["POST"])
@login_required
@agent_id_required
def search_device():
    dbg('search_device')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        imei = data.get('imei')
        device_id = data.get('device_id')
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    device = None
    if imei:
        device = dbapi.get_device(imei=imei)
    elif device_id:
        device = dbapi.get_device(id=device_id)
    if not device:
        raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)

    has_permission = 0
    cur_agent = current_user.cur_agent
    if cur_agent.salesman == 0:
        dds = dbapi.get_device_distribution(device_id=device.id)
        for dd in dds:
            if dd.to_agent == current_user.agent_id:
                has_permission = 1
                break
    elif cur_agent.salesman == 1:
        items = dbapi.get_device_distribution_salesman(device_id=device.id)
        for item in items:
            if item.to_agent == current_user.agent_id:
                has_permission = 1
                break

    if not has_permission:
        raise ApiError('ERROR_AGENT_NO_PERMISSION', error.ERROR_AGENT_NO_PERMISSION)

    device_address = dbapi.get_device_address(id=device.address_id)
    address = ""
    if device_address:
        address = device_address.address
    agent = dbapi.get_agent(id=device.owner_agent_id)
    imei = device.imei
    status = dbapi.get_cws_device_status(imei)
    online = -1
    if status:
        online = status.get('online', -1)
    latest_report = dbapi.get_device_latestreport(imei)
    if not latest_report:
        online = 0
        lng = '0'
        lat = '0'
        signal = 0
    else:
        nowts = datetime.now().timestamp()
        lrts  = latest_report['time'].timestamp()
        if nowts - lrts > 150:
            if online == 1:
                online = 0
        lng = latest_report['lng']
        lat = latest_report['lat']
        signal = latest_report['signal']
    iccid = ''
    cws_device = dbapi.get_cws_device_iccid(imei)
    if cws_device:
        iccid = cws_device['iccid']

    info = {
        'id': device.id,
        'imei': device.imei,
        'cat': device.cat,
        'address': address,
        'use_state': 0,     # 0空闲，1使用
        'comm_state': online,    # 0关机，1在线
        'lng': lng,
        'lat': lat,
        'signal': signal,
        'iccid': iccid,
        'operator': agent.name,
        'operator_level': agent.level,
        'owner_agent_id': device.owner_agent_id,
        'map_display': device.map_display,
        'remark': device.remark,
        'nopay': device.nopay,
        'coupon': device.coupon,
        'product_unit_price': device.product_unit_price,
        'product_min_money': device.product_min_money,
        'product_unit': device.product_unit,
        'product_unit_pluse': device.product_unit_pluse,
        'l4': device.l4,
        'l3': device.l3,
        'l2': device.l2,
        'l1': device.l1,
        'sl3': device.sl3,
        'sl2': device.sl2,
        'sl1': device.sl1,
        'pulse_period': device.low,
        'pulse_width': device.high
    }

    reply['data'] = info

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/fetch')
@login_required
@agent_id_required
def get_devices():
    dbg('get_devices')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    page  = request.args.get('page', 1, type=int)
    psize = request.args.get('psize', 10, type=int)

    agent_id = current_user.agent_id
    count = 0
    data = []
    count, devices = dbapi.get_device(agent_id=agent_id, page=page, psize=psize)
    if count:
        if devices:
            for device in devices:
                device_address = dbapi.get_device_address(id=device.address_id)
                address = ""
                if device_address:
                    address = device_address.address
                agent = dbapi.get_agent(id=device.owner_agent_id)
                imei = device.imei
                status = dbapi.get_cws_device_status(imei)
                online = -1
                if status:
                    online = status.get('online', -1)
                latest_report = dbapi.get_device_latestreport(imei)
                if not latest_report:
                    online = 0
                    lng = '0'
                    lat = '0'
                    signal = 0
                else:
                    nowts = datetime.now().timestamp()
                    lrts  = latest_report['time'].timestamp()
                    if nowts - lrts > 150:
                        if online == 1:
                            online = 0
                    lng = latest_report['lng']
                    lat = latest_report['lat']
                    signal = latest_report['signal']
                iccid = ''
                cws_device = dbapi.get_cws_device_iccid(imei)
                if cws_device:
                    iccid = cws_device['iccid']
                info = {
                    'id': device.id,
                    'imei': device.imei,
                    'cat': device.cat,
                    'address': address,
                    'use_state': 0,     # 0空闲，1使用
                    'comm_state': online,    # 0关机，1在线
                    'lng': lng,
                    'lat': lat,
                    'signal': signal,
                    'iccid': iccid,
                    'operator': agent.name,
                    'operator_level': agent.level,
                    'owner_agent_id': device.owner_agent_id,
                    'map_display': device.map_display,
                    'remark': device.remark,
                    'nopay': device.nopay,
                    'coupon': device.coupon,
                    'product_unit_price': device.product_unit_price,
                    'product_min_money': device.product_min_money,
                    'product_unit': device.product_unit,
                    'product_unit_pluse': device.product_unit_pluse,
                    'l4': device.l4,
                    'l3': device.l3,
                    'l2': device.l2,
                    'l1': device.l1,
                    'pulse_period': device.low,
                    'pulse_width': device.high
                }
                data.append(info)

    reply['data'] = {
        'count': count,
        'devices': data
    }

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/salesman/fetch')
@login_required
@agent_id_required
def get_salesman_devices():
    dbg('get_salesman_devices')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    page  = request.args.get('page', 1, type=int)
    psize = request.args.get('psize', 10, type=int)

    agent_id = current_user.agent_id
    agent = dbapi.get_agent(id=agent_id)
    if not agent:
        raise ApiError('ERROR_AGENT_NOT_FOUND', error.ERROR_AGENT_NOT_FOUND)
    count = 0
    data = []
    if agent.salesman == 0:
        count, devices = dbapi.get_device(agent_id=agent_id, salesman=0, page=page, psize=psize)
    elif agent.salesman == 1:
        count, devices = dbapi.get_device(agent_id=agent_id, salesman=1, page=page, psize=psize)
    if count:
        if devices:
            for device in devices:
                device_address = dbapi.get_device_address(id=device.address_id)
                address = ""
                if device_address:
                    address = device_address.address
                agent = dbapi.get_agent(id=device.salesman_agent_id)
                if agent:
                    operator = agent.name
                    operator_level = agent.slevel
                else:
                    operator = ''
                    operator_level = 0
                imei = device.imei
                status = dbapi.get_cws_device_status(imei)
                online = -1
                if status:
                    online = status.get('online', -1)
                latest_report = dbapi.get_device_latestreport(imei)
                if not latest_report:
                    online = 0
                    lng = '0'
                    lat = '0'
                    signal = 0
                else:
                    nowts = datetime.now().timestamp()
                    lrts  = latest_report['time'].timestamp()
                    if nowts - lrts > 150:
                        if online == 1:
                            online = 0
                    lng = latest_report['lng']
                    lat = latest_report['lat']
                    signal = latest_report['signal']
                iccid = ''
                cws_device = dbapi.get_cws_device_iccid(imei)
                if cws_device:
                    iccid = cws_device['iccid']
                info = {
                    'id': device.id,
                    'imei': device.imei,
                    'cat': device.cat,
                    'address': address,
                    'use_state': 0,     # 0空闲，1使用
                    'comm_state': online,    # 0关机，1在线
                    'lng': lng,
                    'lat': lat,
                    'signal': signal,
                    'iccid': iccid,
                    'operator': operator,
                    'operator_level': operator_level,
                    'owner_agent_id': device.owner_agent_id,
                    'salesman_agent_id': device.salesman_agent_id,
                    'map_display': device.map_display,
                    'remark': device.remark,
                    'nopay': device.nopay,
                    'product_unit_price': device.product_unit_price,
                    'product_min_money': device.product_min_money,
                    'product_unit': device.product_unit,
                    'product_unit_pluse': device.product_unit_pluse,
                    'l4': device.l4,
                    'l3': device.l3,
                    'l2': device.l2,
                    'l1': device.l1,
                    'sl1': device.sl1,
                    'sl2': device.sl2,
                    'sl3': device.sl3,
                    'pulse_period': device.low,
                    'pulse_width': device.high
                }
                data.append(info)

    reply['data'] = {
        'count': count,
        'devices': data
    }

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/fetch_num')
@login_required
@agent_id_required
def get_device_number():
    dbg('get_device_number')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    agent_id = current_user.agent_id
    agent = current_user.cur_agent
    if agent.salesman:
        numbers, devices = dbapi.get_device(agent_id=agent_id, salesman=1, count=True)
    else:
        numbers, devices = dbapi.get_device(agent_id=agent_id, count=True)
    imeis    = []
    if devices:
        imeis = list(map(lambda x: x.imei, devices))
    onlines  = dbapi.get_cws_device_status_numbers(imeis, 1)
    offlines = numbers - onlines
    unknown  = 0
    # offlines = dbapi.get_cws_device_status_numbers(imeis, 0)
    # unknown  = dbapi.get_cws_device_status_numbers(imeis, 4)
    
    reply['data'] = {
        'numbers': numbers,
        'onlines': onlines,
        'offlines': offlines,
        'unknown': unknown
    }

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/fuzzy_query/<field>', methods=["POST"])
@login_required
@agent_id_required
def fuzzy_query_device(field):
    dbg('fuzzy_query_device')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        assert(field in ('imei'))
        data = request.get_json()
        value = data[field]
    except:
        print_exception_info()
        raise ApiError('fuzzy_query_device error', error.ERROR_PARAM)

    kwargs = {field: value}

    agent_id = current_user.agent_id
    if current_user.cur_agent.salesman == 1:
        upper_agent = dbapi.get_agent(id=current_user.cur_agent.hook_agent_id)
        if upper_agent:
            agent_id = upper_agent.id

    res = dbapi.fuzzy_query_device(agent_id, **kwargs)
    reply['data'] = res

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/address/fuzzy_query/<field>', methods=["POST"])
@login_required
@agent_id_required
def fuzzy_query_device_address(field):
    dbg('fuzzy_query_device_address')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        assert(field in ('address'))
        data = request.get_json()
        value = data[field]
    except:
        print_exception_info()
        raise ApiError('fuzzy_query_device_address error', error.ERROR_PARAM)

    kwargs = {field: value}

    agent_id = current_user.agent_id
    if current_user.cur_agent.salesman == 1:
        upper_agent = dbapi.get_agent(id=current_user.cur_agent.hook_agent_id)
        if upper_agent:
            agent_id = upper_agent.id

    res = dbapi.fuzzy_query_device_address(agent_id, **kwargs)
    reply['data'] = res

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/update', methods=["PATCH"])
@login_required
@agent_id_required
def update_devices():
    dbg('update_devices')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        imeis = data['imeis']
        update = data['update']
        invalid_keys = ('l1', 'l2', 'l3', 'l4', 'agent_id')
        for key in invalid_keys:
            assert(key not in update)
        advanced = data.get('advanced')
        advanced_keys = ('pulse_period', 'pulse_width')
        if advanced:
            for key in advanced_keys:
                assert(key in advanced)

        if 'sl1' in update or 'sl2' in update or 'sl3' in update or 'self' in update :
            keys = ('sl1', 'sl2', 'sl3', 'self')
            all_ = 0
            for k in keys:
                assert(k in update)
                all_ += update[k]
            assert(math.isclose(all_, 1))

    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    agent_id = current_user.agent_id

    for imei in imeis:
        device = dbapi.get_device(imei=imei)
        if not device:
            db.session.rollback()
            dbg('imei: %s not exists' % imei)
            reply['code'] = 999
            reply['msg'] = 'imei: %s 不存在' % imei
            status_code = 422
            return make_response(jsonify(reply), status_code)
        elif device.owner_agent_id != agent_id:
            db.session.rollback()
            dbg('imei: %s no permission' % imei)
            reply['code'] = 999
            reply['msg'] = 'imei: %s 没有权限编辑' % imei
            status_code = 422
            return make_response(jsonify(reply), status_code)

        # 1. 更新套餐
        product_list = update.get('product_list')
        if product_list is not None and isinstance(product_list, list):
            # 1. 删除原来的设备产品
            count = dbapi.delete_device_product(device.id)
            dbg('delete_device_product count: %d' % count)

            # 2. 添加设备产品表
            for product_id in product_list:
                device_product = dbapi.make_new_device_product(device.id, product_id)

        # 2. 更新广告
        ad_list = update.get('ad_list')
        if ad_list is not None and isinstance(ad_list, list):
            # 1. 删除原来的设备广告
            count = dbapi.delete_device_ad(device.id)
            dbg('delete_device_ad count: %d' % count)

            # 2. 添加设备广告表
            for ad_id in ad_list:
                device_ad = dbapi.make_new_device_ad(device.id, ad_id)

        # 3. 更新设备表
        if advanced:
            update['low'] = advanced['pulse_period']
            update['high'] = advanced['pulse_width']
        dbg(update)
        device = dbapi.update_device(device, **update)
        db.session.add(device)

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/rate/update', methods=["PATCH"])
@login_required
@agent_id_required
def update_device_rate():
    dbg('update_device_rate')

    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        imei = data['imei']
        rate = float(data['rate'])
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    if rate < 0 or rate > 1:
        raise ApiError('rate not support')

    dd = dbapi.get_device_distribution(imei=imei, from_agent=current_user.agent_id)
    if not dd:
        raise ApiError('ERROR_NOT_DISTRIBUTION', error.ERROR_NOT_DISTRIBUTION)

    device = dbapi.get_device(id=dd.device_id)
    if not device:
        raise ApiError('ERROR_DEVICE_NOT_FOUNDE', error.ERROR_DEVICE_NOT_FOUND)

    # 更新device_distribution
    dd = dbapi.update_device_distribution(dd, rate=rate)
    db.session.commit()

    # 计算l4,l3,l2,l1
    level = current_user.cur_agent.level
    agent_levels = []
    rates_all = [device.l1, device.l2, device.l3, device.l4]
    dds = dbapi.get_device_distribution(device_id=device.id)
    for dd in dds:
        agent = dbapi.get_agent(id=dd.to_agent)
        agent_levels.append(agent.level)
    update = calc_device_profit(level, rate, agent_levels, rates_all)

    # 更新device
    dbg(update)
    device = dbapi.update_device(device, **update)
    db.session.commit()

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/multi/distribution', methods=["PATCH"])
@login_required
@agent_id_required
def device_multi_distribution():
    dbg('device_multi_distribution')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data  = request.get_json()
        imeis = data['imeis']
        to_agent = data['to_agent']
        rate     = data['rate']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    agent_id = current_user.agent_id

    dbg(imeis)
    levels = ('l1', 'l2', 'l3', 'l4')

    for imei in imeis:
        dbg(imei)
        device = dbapi.get_device(imei=imei)
        if not device:
            db.session.rollback()
            dbg('imei: %s not exists' % imei)
            reply['code'] = 999
            reply['msg'] = 'imei: %s 不存在' % imei
            status_code = 422
            return make_response(jsonify(reply), status_code)
        elif device.owner_agent_id != agent_id:
            db.session.rollback()
            dbg('imei: %s no permission' % imei)
            reply['code'] = 999
            reply['msg'] = 'imei: %s 没有权限分配' % imei
            status_code = 422
            return make_response(jsonify(reply), status_code)
        elif device.salesman_agent_id != 0:
            db.session.rollback()
            dbg('imei: %s belong to salesman' % imei)
            reply['code'] = 999
            reply['msg'] = 'imei: %s 已被分配给业务员' % imei
            status_code = 422
            return make_response(jsonify(reply), status_code)

        update = {}
        # 1. 修改提成比例
        cur_agent_level = current_user.cur_agent.level
        target_agent = dbapi.get_agent(id=to_agent)
        if not target_agent:
            db.session.rollback()
            raise ApiError('ERROR_AGENT_NOT_FOUND', error.ERROR_AGENT_NOT_FOUND)

        tmp_levels = ['l1', 'l2', 'l3', 'l4']
        tmp_levels.pop(cur_agent_level-1)
        tmp_levels.pop(target_agent.level-1)
        sum_rate = rate
        for level in tmp_levels:
            sum_rate += device.__dict__[level]


        update[levels[cur_agent_level-1]] = rate
        update[levels[target_agent.level-1]] = 1 - sum_rate

        if update[levels[target_agent.level-1]] < 0:
            db.session.rollback()
            raise ApiError('ERROR_INVALIDATE_RATE', error.ERROR_INVALIDATE_RATE)

        # device_distributions = dbapi.get_device_distribution(device_id=device.id)
        # distri_count = 0
        # if device_distributions:
        #     distri_count = len(device_distributions)
        # if distri_count == 1:
        #     update['l4'] = rate
        #     update['l3'] = device.l4 - rate
        #     upper_rate = device.l4
        # if distri_count == 2:
        #     update['l3'] = rate
        #     update['l2'] = device.l3 - rate
        #     upper_rate = device.l3
        # if distri_count == 3:
        #     update['l2'] = rate
        #     update['l1'] = device.l2 - rate
        #     upper_rate = device.l2

        # try:
        #     assert(upper_rate>rate)
        # except:
        #     print_exception_info()
        #     raise ApiError('ERROR_INVALIDATE_RATE', error.ERROR_INVALIDATE_RATE)

        # 2. 插入设备分组
        from_agent = agent_id
        device_distribution =  dbapi.make_new_device_distribution(
            device.id, device.imei, from_agent, to_agent, rate)

        # 3. 更细设备
        update['agent_id'] = to_agent
        update['address_id'] = 0
        device = dbapi.update_device(device, **update)
        db.session.add(device)

        # 4. 移除设备的套餐
        dbapi.delete_device_product(device.id)

        # 5. 清除历史订单
        dbapi.delete_pays_and_records(device.imei)

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/salesman/multi/distribution', methods=["PATCH"])
@login_required
@agent_id_required
def device_salesman_multi_distribution():
    dbg('device_salesman_multi_distribution')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data  = request.get_json()
        imeis = data['imeis']
        to_agent = data['to_agent']
        sl1   = data['sl1']
        sl2   = data['sl2']
        sl3   = data['sl3']
        my    = data['self']
        all_ = sl1 + sl2 + sl3 + my
        assert(math.isclose(all_, 1))
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    agent_id = current_user.agent_id

    dbg(imeis)

    for imei in imeis:
        dbg(imei)
        device = dbapi.get_device(imei=imei)
        if not device:
            db.session.rollback()
            dbg('imei: %s not exists' % imei)
            reply['code'] = 999
            reply['msg'] = 'imei: %s 不存在' % imei
            status_code = 422
            return make_response(jsonify(reply), status_code)
        elif device.owner_agent_id != agent_id and device.salesman_agent_id != agent_id:
            db.session.rollback()
            dbg('imei: %s no permission' % imei)
            reply['code'] = 999
            reply['msg'] = 'imei: %s 没有权限分配' % imei
            status_code = 422
            return make_response(jsonify(reply), status_code)
        elif device.salesman_agent_id != 0 and current_user.cur_agent.salesman == 0:
            db.session.rollback()
            dbg('imei: %s belong to salesman' % imei)
            reply['code'] = 999
            reply['msg'] = 'imei: %s 已被分配给业务员' % imei
            status_code = 422
            return make_response(jsonify(reply), status_code)

        update = {
            'sl1': data['sl1'],
            'sl2': data['sl2'],
            'sl3': data['sl3'],
        }

        # 1. 插入设备分组
        from_agent = agent_id
        device_distribution =  dbapi.make_new_device_distribution_salesman(
            device.id, device.imei, from_agent, to_agent)

        # 2. 更细设备
        update['salesman_agent_id'] = to_agent
        if device.salesman_agent_id != 0:
            update.pop('sl1')
            update.pop('sl2')
            update.pop('sl3')
        dbg(update)
        device = dbapi.update_device(device, **update)
        db.session.add(device)

        # 3. 移除设备的套餐
        # dbapi.delete_device_product(device.id)

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/recycle', methods=["PATCH"])
@login_required
@agent_id_required
def recycle_device():
    dbg('recycle_device')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data  = request.get_json()
        imei  = data['imei']
    except:
        print_exception_info()
        raise ApiError('update devices error', error.ERROR_PARAM)

    device = dbapi.get_device(imei=imei)
    if not device:
        raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)

    update = {}
    update['agent_id'] = device.agent_id
    update['address_id'] = 0
    update['salesman_agent_id'] = 0
    update['l4'] = 1
    update['l3'] = 0
    update['l2'] = 0
    update['l1'] = 0

    device = dbapi.update_device(device, **update)

    # device_distribution
    dbapi.delete_device_distribution(imei)

    # device_distribution_salesman
    dbapi.delete_device_distribution_salesman(imei)

    # device_product
    dbapi.delete_device_product(device.id)

    # pay
    dbapi.delete_pays_and_records(imei)

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/address/add', methods=["PUT"])
@login_required
@agent_id_required
def add_device_address():
    dbg('add_device_address')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        region = data['region']
        address = data['address']
    except:
        print_exception_info()
        raise ApiError('add device address error', error.ERROR_PARAM)

    agent_id = current_user.agent_id
    device_address = dbapi.make_new_device_address(agent_id, region, address)
    db.session.commit()

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/address/fetch')
@login_required
@agent_id_required
def get_device_addresses():
    dbg('get_device_addresses')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    agent_id = current_user.agent_id
    device_addresses = dbapi.get_device_address(agent_id=agent_id)

    data = []
    if device_addresses:
        for address in device_addresses:
            info = {
                'id'    : address.id,
                'region': address.region,
                'address': address.address,
            }
            data.append(info)

    reply['data'] = data

    return make_response(jsonify(reply), status_code)


# TODO address update and delete


@admin_device_blueprint.route('/product/add', methods=["PUT"])
@login_required
@agent_id_required
def add_product():
    dbg('add_product')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        title = data['title']
        body = data['body']
        value = data['value']
        cat = data['cat']
        price = data['price']
    except:
        print_exception_info()
        raise ApiError('add product error', error.ERROR_PARAM)

    if price < 1:
        raise ApiError('ERROR_INVALIDATE_PRICE', error.ERROR_INVALIDATE_PRICE)

    agent_id = current_user.agent_id
    product = dbapi.make_new_product(agent_id, title, body, value, cat, price)
    db.session.commit()

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/product/fetch', methods=["POST"])
@login_required
@agent_id_required
def get_products():
    dbg('get_products')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()

        # cat 和 device_id 二选一
        cat = data.get('cat')
        device_id = data.get('device_id')
    except:
        print_exception_info()
        raise ApiError('get products error', error.ERROR_PARAM)

    data = []
    if cat is not None:
        agent_id = current_user.agent_id
        products = dbapi.get_product(agent_id=agent_id, cat=cat)
        if products:
            for product in products:
                info = {
                    'id': product.id,
                    'cat': product.cat,
                    'title': product.title,
                    'body': product.body,
                    'value': product.value,
                    'price': product.price,
                    'inventory': product.inventory
                }
                data.append(info)

    if device_id is not None:
        device = dbapi.get_device(device_id=device_id)
        if not device:
            raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)
        device_products = dbapi.get_device_product(device_id=device_id)
        if device_products:
            for device_product in device_products:
                product = dbapi.get_product(product_id=device_product.product_id)
                info = {
                    'id': product.id,
                    'cat': product.cat,
                    'title': product.title,
                    'body': product.body,
                    'value': product.value,
                    'price': product.price,
                    'inventory': product.inventory,
                    'unit': device.product_unit
                }
                data.append(info)

    reply['data'] = data

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/product/update', methods=["PATCH"])
@login_required
@agent_id_required
def update_product():
    dbg('update_product')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        product_id = data['product_id']
        update = data['update']
        keys = ('title', 'body', 'value', 'price')
        for k in update:
            assert(k in keys)
            if 'value' in update:
                assert(isinstance(update['value'], int) and update['value'] > 0)
            if 'price' in update:
                assert(isinstance(update['price'], int) and update['price'] > 0)
    except:
        print_exception_info()
        raise ApiError('update product error', error.ERROR_PARAM)

    product = dbapi.get_product(product_id=product_id)
    if not product:
        raise ApiError('update product', error.ERROR_PRODUCT_NOT_FOUND)
    product = dbapi.update_product(product, **update)
    db.session.add(product)
    db.session.commit()

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/product/delete', methods=["DELETE"])
@login_required
def delete_product():
    dbg('delete_product')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        product_id = data['product_id']
    except:
        print_exception_info()
        raise ApiError('delete product error', error.ERROR_PARAM)

    product = dbapi.get_product(product_id=product_id)
    if not product:
        raise ApiError('update product', error.ERROR_PRODUCT_NOT_FOUND)

    product = dbapi.update_product(product, deleted=1)
    db.session.add(product)
    db.session.commit()

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/ad/add', methods=["PUT"])
@login_required
@agent_id_required
def add_ad():
    dbg('add_ad')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        name = request.form['name']
        desc = request.form['desc']
        url  = request.form['url']

        imag_file = request.files['0']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    agent_id = current_user.agent_id

    # check img
    im = Image.open(imag_file)
    w, h = im.size
    if w != 500 and h != 200:
        raise ApiError('ERROR_IMG_SIZE_NOT_MATCH', error.ERROR_IMG_SIZE_NOT_MATCH)

    imag_filename = 'ad%d_%s.jpg' % (agent_id, datetime.now().strftime('%y%m%d%H%M%S'))
    imag_filepath = os.path.join('app/static/img/ad', imag_filename)
    qrcode_img    = os.path.join('img/ad', imag_filename)
    if not os.path.exists('app/static/img/ad'):
        os.mkdir('app/static/img/ad')
    dbg("save imag: %s" % imag_filepath)
    im.save(imag_filepath)

    img = 'img/ad/' + imag_filename
    ad = dbapi.make_new_ad(agent_id, name, desc, img, url)
    db.session.commit()

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/ad/fetch', methods=["POST"])
@login_required
@agent_id_required
def get_ads():
    dbg('get_ads')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        imei = data.get('imei')
    except:
        print_exception_info()
        raise ApiError('get products error', error.ERROR_PARAM)

    if imei:
        ads = dbapi.get_ad(imei=imei)
    else:
        agent_id = current_user.agent_id
        ads = dbapi.get_ad(agent_id=agent_id)

    data = []
    for ad in ads:
        info = {
            'id': ad.id,
            'name': ad.name,
            'desc': ad.desc,
            'img' : url_for('static', filename=ad.img),
            'url' : ad.url,
            'using': ad.using
        }
        data.append(info)

    reply['data'] = data

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/ad/update', methods=["PATCH"])
@login_required
@agent_id_required
def update_ad():
    dbg('update_ad')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        ad_id  = request.form['ad_id']
        name   = request.form.get('name')
        desc   = request.form.get('desc')
        url    = request.form.get('url')
        using  = request.form.get('using')
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    update = {}
    if name:
        update['name'] = name
    if desc:
        update['desc'] = desc
    if url:
        update['url'] = url
    if using:
        update['using'] = using

    agent_id = current_user.agent_id

    imag_file = request.files.get('0')
    if imag_file:
        imag_filename = 'ad%d_%s' % (agent_id, datetime.now().strftime('%y%m%d%H%M%S'))
        imag_filepath = os.path.join('app/static/img/ad', imag_filename)
        qrcode_img    = os.path.join('img/ad', imag_filename)
        if not os.path.exists('app/static/img/ad'):
            os.mkdir('app/static/img/ad')
        dbg("save imag: %s" % imag_filepath)
        imag_file.save(imag_filepath)

        img = 'img/ad/' + imag_filename
        update['img'] = img

    ad = dbapi.get_ad(id=ad_id)
    if not ad:
        raise ApiError('ERROR_AD_NOT_FOUND', error.ERROR_AD_NOT_FOUND)
    ad = dbapi.update_ad(ad, **update)
    db.session.commit()

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/ad/delete', methods=["DELETE"])
@login_required
def delete_ad():
    dbg('delete_ad')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        ad_id = data['ad_id']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    ad = dbapi.get_ad(id=ad_id)
    if not ad:
        raise ApiError('ERROR_AD_NOT_FOUND', error.ERROR_AD_NOT_FOUND)

    ad = dbapi.update_ad(ad, deleted=1)
    db.session.commit()

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/ad/using', methods=["POST"])
@login_required
@agent_id_required
def using_ads():
    dbg('using_ads')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        ad_list = data['ad_list']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    agent_id = current_user.agent_id

    ads = dbapi.get_ad(agent_id=agent_id, using=1)
    for ad in ads:
        ad = dbapi.update_ad(ad, using=0)

    for ad_id in ad_list:
        ad = dbapi.get_ad(id=ad_id)
        if not ad:
            dbg(ad_id)
            raise ApiError('ERROR_AD_NOT_FOUND', error.ERROR_AD_NOT_FOUND)
        ad = dbapi.update_ad(ad, using=1)

    db.session.commit()

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/nopay/search', methods=["POST"])
@login_required
@agent_id_required
def search_nopay_device():
    dbg('search_nopay_device')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        imei = data.get('imei')
        device_id = data.get('device_id')
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    device = None
    if imei:
        device = dbapi.get_device(imei=imei)
    elif device_id:
        device = dbapi.get_device(id=device_id)
    if not device:
        raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)

    if device.nopay == 0:
        raise ApiError('', error.ERROR_DEVICE_NOT_SUP_NOPAY)

    has_permission = 0
    cur_agent = current_user.cur_agent
    if cur_agent.salesman == 0:
        dds = dbapi.get_device_distribution(device_id=device.id)
        for dd in dds:
            if dd.to_agent == current_user.agent_id:
                has_permission = 1
                break
    elif cur_agent.salesman == 1:
        items = dbapi.get_device_distribution_salesman(device_id=device.id)
        for item in items:
            if item.to_agent == current_user.agent_id:
                has_permission = 1
                break

    if not has_permission:
        raise ApiError('ERROR_AGENT_NO_PERMISSION', error.ERROR_AGENT_NO_PERMISSION)

    device_address = dbapi.get_device_address(id=device.address_id)
    address = ""
    if device_address:
        address = device_address.address

    nopay_count = dbapi.get_record_no_pay(imei=imei, count=True)

    info = {
        'id': device.id,
        'imei': device.imei,
        'cat': device.cat,
        'address': address,
        'remark': device.remark,
        'nopay_count': nopay_count
    }

    reply['data'] = info

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/nopay/fetch')
@login_required
@agent_id_required
def get_nopay_devices():
    dbg('get_nopay_devices')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    page  = request.args.get('page', 1, type=int)
    psize = request.args.get('psize', 10, type=int)

    agent_id = current_user.agent_id
    count = 0
    data = []
    count, devices = dbapi.get_device(agent_id=agent_id, page=page, psize=psize, nopay=1)
    if count:
        if devices:
            for device in devices:
                device_address = dbapi.get_device_address(id=device.address_id)
                address = ""
                if device_address:
                    address = device_address.address
                imei = device.imei
                nopay_count = dbapi.get_record_no_pay(imei=imei, count=True)
                info = {
                    'id': device.id,
                    'imei': device.imei,
                    'cat': device.cat,
                    'address': address,
                    'remark': device.remark,
                    'nopay_count': nopay_count
                }
                data.append(info)

    reply['data'] = {
        'count': count,
        'devices': data
    }

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/nopay/salesman/fetch')
@login_required
@agent_id_required
def get_nopay_salesman_devices():
    dbg('get_nopay_salesman_devices')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    page  = request.args.get('page', 1, type=int)
    psize = request.args.get('psize', 10, type=int)

    agent_id = current_user.agent_id
    agent = dbapi.get_agent(id=agent_id)
    if not agent:
        raise ApiError('ERROR_AGENT_NOT_FOUND', error.ERROR_AGENT_NOT_FOUND)
    count = 0
    data = []
    if agent.salesman == 0:
        count, devices = dbapi.get_device(agent_id=agent_id, salesman=0, page=page, psize=psize, nopay=1)
    elif agent.salesman == 1:
        count, devices = dbapi.get_device(agent_id=agent_id, salesman=1, page=page, psize=psize, nopay=1)
    if count:
        if devices:
            for device in devices:
                device_address = dbapi.get_device_address(id=device.address_id)
                address = ""
                if device_address:
                    address = device_address.address
                imei = device.imei
                nopay_count = dbapi.get_record_no_pay(imei=imei, count=True)
                info = {
                    'id': device.id,
                    'imei': device.imei,
                    'cat': device.cat,
                    'address': address,
                    'remark': device.remark,
                    'nopay_count': nopay_count
                }
                data.append(info)

    reply['data'] = {
        'count': count,
        'devices': data
    }

    return make_response(jsonify(reply), status_code)


@admin_device_blueprint.route('/nopay/record/fetch', methods=['POST'])
@login_required
@agent_id_required
def get_nopay_record():
    dbg('get_nopay_record')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        imei = data['imei']
        page  = request.args.get('page', 1, type=int)
        psize = request.args.get('psize', 10, type=int)
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    data = []
    count, records = dbapi.get_record_no_pay(imei=imei, page=page, psize=psize)
    if count:
        for record in records:
            info = {
                'stime': int(record.stime.timestamp()),
                'etime': int(record.etime.timestamp()),
                'imei' : record.imei
            }
            data.append(info)

    reply['data'] = {
        'count': count,
        'records': data
    }

    return make_response(jsonify(reply), status_code)