#!/usr/bin/env python3
# coding: utf8
# 20170220 anChaOs


# general
import os, json, time
import requests # for http requests
from datetime import datetime, timedelta, date

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

from app.tool import dbg                    # for print
from app.tool import print_exception_info   # for traceback

# blueprint
from . import admin_god_blueprint


@admin_god_blueprint.errorhandler(ApiError)
def handle_api_error(current_error):
    dbg((current_error.msg, current_error.error_no))
    error_info = error.get_error_info(current_error.error_no)
    return make_response(jsonify({'code':current_error.error_no, 'msg':error_info[0]}), error_info[1])


@admin_god_blueprint.errorhandler(Exception)
def handle_base_exception(current_error):
    print_exception_info()
    return make_response(json.dumps({'code':99, 'msg':'server error'}), 500)


@admin_god_blueprint.route('/<role>/add', methods=["PUT"])
@login_required
def add_agent_or_god(role):
    dbg('add_agent_or_god')
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    try:
        data  = request.get_json()
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    role_bit = int(current_user.role[5])

    if role_bit == 2:
        try:
            assert(role == 'god')
            name    = data['name']
            email   = data['email']
            phone   = data['phone']
            remark  = data['remark']
        except:
            print_exception_info()
            raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

        target_god = dbapi.get_god(phone=phone)
        if target_god:
            raise ApiError('ERROR_PHONE_EXISTS', error.ERROR_PHONE_EXISTS)

        target_god = dbapi.get_god(email=email)
        if target_god:
            raise ApiError('ERROR_EMAIL_EXISTS', error.ERROR_EMAIL_EXISTS)

        openluat_user = dbapi.get_openluat_user(phone=phone)
        if not openluat_user:
            openluat_user = dbapi.make_new_openluat_user(name, email, phone, role='000001000000')
        else:
            openluat_user.role[5] = '1'
            db.session.add(openluat_user)

        db.session.commit()

        openluat_user_id = openluat_user.id
        new_god = dbapi.make_new_god(openluat_user_id, name, phone, email, remark)
        db.session.commit()


    elif role_bit == 1:
        try:
            assert(role == 'agent')
            level   = 4
            name    = data['name']
            email   = data['email']
            phone   = data['phone']
            address = data['address']
            remark  = data['remark']
            expandable  = 1
            withdrawable = 1
        except:
            print_exception_info()
            raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

        target_agent = dbapi.get_agent(phone=phone)
        if target_agent:
            raise ApiError('ERROR_PHONE_EXISTS', error.ERROR_PHONE_EXISTS)

        target_agent = dbapi.get_agent(email=email)
        if target_agent:
            raise ApiError('ERROR_EMAIL_EXISTS', error.ERROR_EMAIL_EXISTS)

        openluat_user = dbapi.get_openluat_user(phone=phone)
        if not openluat_user:
            openluat_user = dbapi.make_new_openluat_user(name, email, phone)
            db.session.commit()

        hook_agent_id = 0
        salesman = 0
        slevel = 0
        new_agent = dbapi.make_new_agent(salesman, openluat_user.id, hook_agent_id, level,
            slevel, expandable, withdrawable, name, phone, email, address, remark)
        db.session.commit()

        agent_setting = dbapi.make_new_agent_setting(new_agent.id)

        openluat_user_id = current_user.id
        god = dbapi.get_god(openluat_user_id=openluat_user_id)
        god_agent = dbapi.make_new_god_agent(god.id, new_agent.id)
        db.session.commit()

    elif role_bit == 0:
        raise ApiError('ERROR_AGENT_NO_PERMISSION', error.ERROR_AGENT_NO_PERMISSION)

    return make_response(jsonify(reply), status_code)


@admin_god_blueprint.route('/<role>/fetch')
@login_required
def get_agent_or_god(role):
    dbg('get_agent_or_god')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    page  = int(request.args.get('page', 1))
    psize = int(request.args.get('psize', 10))

    role_bit = int(current_user.role[5])

    if role_bit == 2:
        try:
            assert(role == 'god')
        except:
            print_exception_info()
            raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

        count, gods = dbapi.get_god(role=1, page=page, psize=psize)
        data = []
        if count and gods:
            for god in gods:
                info = {
                    'id'  : god.id,
                    'name': god.name,
                    'phone': god.phone,
                    'email': god.email,
                    'remark': god.remark
                }
                data.append(info)

        reply['data'] = {
            'count': count,
            'gods': data
        }

    elif role_bit == 1:
        try:
            assert(role == 'agent')
        except:
            print_exception_info()
            raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

        openluat_user_id = current_user.id
        god = dbapi.get_god(openluat_user_id=openluat_user_id)
        count, res = dbapi.get_god_agent(god_id=god.id, page=page, psize=psize)
        data = []
        if count and res:
            for god_agent in res:
                agent_id = god_agent.agent_id
                agent = dbapi.get_agent(id=agent_id)
                if not agent:
                    continue
                info = {
                    'id': agent.id,
                    'name': agent.name,
                    'level': agent.level,
                    'phone': agent.phone,
                    'address': agent.address,
                    'expandable': agent.expandable,
                    'remark': agent.remark
                }
                data.append(info)

        reply['data'] = {
            'count': count,
            'agents': data
        }

    elif role_bit == 0:
        raise ApiError('ERROR_AGENT_NO_PERMISSION', error.ERROR_AGENT_NO_PERMISSION)

    return make_response(jsonify(reply), status_code)


@admin_god_blueprint.route('/agent_devices/fetch', methods=["POST"])
@login_required
def get_agent_devices():
    dbg('get_agent_devices')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data  = request.get_json()
        agent_id = data['agent_id']
        page = request.args.get('page', 1, type=int)
        psize = request.args.get('psize', 10, type=int)
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    role_bit = int(current_user.role[5])
    if role_bit != 1:
        raise ApiError('ERROR_AGENT_NO_PERMISSION', error.ERROR_AGENT_NO_PERMISSION)

    count = 0
    data = []
    count, devices = dbapi.get_device(agent_id=agent_id, page=page, psize=psize)
    if count:
        for device in devices:
            device_address = dbapi.get_device_address(id=device.address_id)
            address = ""
            if device_address:
                address = device_address.address
            operator = ''
            operator_level = 0
            agent = dbapi.get_agent(id=device.owner_agent_id)
            if agent:
                operator = agent.name
                operator_level = agent.level
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
                'operator': operator,
                'operator_level': operator_level,
                'owner_agent_id': device.owner_agent_id,
                'map_display': device.map_display,
                'remark': device.remark,
                'l4': device.l4,
                'l3': device.l3,
                'l2': device.l2,
                'l1': device.l1
            }
            data.append(info)

    reply['data'] = {
        'count': count,
        'devices': data
    }

    return make_response(jsonify(reply), status_code)


@admin_god_blueprint.route('/god_devices/fetch', methods=["POST"])
@login_required
def get_god_devices():
    dbg('get_god_devices')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data  = request.get_json()
        god_id = data['god_id']
        page = request.args.get('page', 1, type=int)
        psize = request.args.get('psize', 10, type=int)
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    role_bit = int(current_user.role[5])
    if role_bit != 2:
        raise ApiError('ERROR_AGENT_NO_PERMISSION', error.ERROR_AGENT_NO_PERMISSION)

    count = 0
    data = []

    ct1, agents = dbapi.get_god_agent(god_id=god_id, page=1, psize=999)
    for agent in agents:
        agent_id = agent.id
        ct2, devices = dbapi.get_device(agent_id=agent_id, page=page, psize=psize)
        if ct2:
            count += ct2
            for device in devices:
                device_address = dbapi.get_device_address(id=device.address_id)
                address = ""
                if device_address:
                    address = device_address.address
                operator = ''
                operator_level = 0
                agent = dbapi.get_agent(id=device.owner_agent_id)
                if agent:
                    operator = agent.name
                    operator_level = agent.level
                imei = device.imei
                status = dbapi.get_cws_device_status(imei)
                online = -1
                if status:
                    online = status.get('online', -1)
                latest_report = dbapi.get_device_latestreport(imei)
                if not latest_report:
                    online = 0
                else:
                    if imei == '868575021151255':
                        dbg(latest_report['time'])
                    nowts = datetime.now().timestamp()
                    lrts  = latest_report['time'].timestamp()
                    if nowts - lrts > 150:
                        if online == 1:
                            online = 0
                info = {
                    'id': device.id,
                    'imei': device.imei,
                    'cat': device.cat,
                    'address': address,
                    'use_state': 0,     # 0空闲，1使用
                    'comm_state': online,    # 0关机，1在线
                    'operator': operator,
                    'operator_level': operator_level,
                    'owner_agent_id': device.owner_agent_id,
                    'map_display': device.map_display,
                    'remark': device.remark,
                    'l4': device.l4,
                    'l3': device.l3,
                    'l2': device.l2,
                    'l1': device.l1
                }
                data.append(info)

    reply['data'] = {
        'count': count,
        'devices': data
    }

    return make_response(jsonify(reply), status_code)


@admin_god_blueprint.route('/unknow_device/fetch')
@login_required
def get_unknow_device():
    dbg('get_unknow_device')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    role_bit = int(current_user.role[5])
    if role_bit != 2:
        raise ApiError('ERROR_AGENT_NO_PERMISSION', error.ERROR_AGENT_NO_PERMISSION)

    page = request.args.get('page', 1, type=int)
    psize = request.args.get('psize', 10, type=int)

    data = []
    dbsession = dbapi.db.session
    Device = dbapi.Device
    query = dbsession.query(Device).filter(Device.agent_id==0)
    count = query.count()
    devices = query.slice(psize*(page-1), psize*page).all()
    if count:
        for device in devices:
            info = {
                'id': device.id,
                'imei': device.imei
            }
            data.append(info)

    reply['data'] = {
        'count': count,
        'devices': data
    }

    return make_response(jsonify(reply), status_code)


@admin_god_blueprint.route('/unknow_device/search', methods=["POST"])
@login_required
def search_unknow_device():
    dbg('search_unknow_device')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data  = request.get_json()
        imei = data.get('imei')
        device_id = data.get('device_id')
        dbg(data)
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    role_bit = int(current_user.role[5])
    if role_bit != 2:
        raise ApiError('ERROR_AGENT_NO_PERMISSION', error.ERROR_AGENT_NO_PERMISSION)

    device = None
    dbsession = dbapi.db.session
    Device = dbapi.Device
    query = dbsession.query(Device).filter(Device.agent_id==0)
    if imei:
        device = query.filter(Device.imei==imei).first()
    elif device_id:
        device = query.filter(Device.id==int(device_id)).first()
    if not device:
        raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)

    reply['data'] = {
        'id': device.id,
        'imei': device.imei
    }

    return make_response(jsonify(reply), status_code)


@admin_god_blueprint.route('/fuzzy_agent/name', methods=["POST"])
@login_required
def fuzzy_get_agent_name():
    dbg('fuzzy_get_agent_name')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        name = data['name']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    role_bit = int(current_user.role[5])
    if role_bit != 2:
        raise ApiError('ERROR_AGENT_NO_PERMISSION', error.ERROR_AGENT_NO_PERMISSION)

    dbsession = dbapi.db.session
    Agent = dbapi.Agent
    agents = dbsession.query(Agent).filter(Agent.name.like("%%%s%%" % name)).\
        filter(Agent.level==4).limit(5)

    data = []
    for agent in agents:
        info = {
            'name': agent.name,
            'id' : agent.id
        }
        data.append(info)

    reply['data'] = {
        'names': data
    }

    return make_response(jsonify(reply), status_code)


@admin_god_blueprint.route('/multi/first_distribution', methods=["PATCH"])
@login_required
def device_multi_distribution():
    dbg('device_multi_distribution')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data  = request.get_json()
        imeis = data['imeis']
        to_agent = data['to_agent']
    except:
        print_exception_info()
        raise ApiError('update devices error', error.ERROR_PARAM)

    agent = dbapi.get_agent(id=to_agent)
    if not agent or agent.level != 4:
        raise ApiError('can only give level 4')

    for imei in imeis:
        device = dbapi.get_device(imei=imei)
        if not device:
            db.session.rollback()
            dbg('imei: %s not exists' % imei)
            reply['code'] = 999
            reply['msg'] = 'imei: %s 不存在' % imei
            status_code = 422
            return make_response(jsonify(reply), status_code)
        elif device.agent_id != 0:
            db.session.rollback()
            dbg('imei: %s already first_distribution' % imei)
            reply['code'] = 999
            reply['msg'] = 'imei: %s 已经被首次分配' % imei
            status_code = 422
            return make_response(jsonify(reply), status_code)

        # 1. 插入设备分组
        from_agent = device.agent_id
        device_distribution =  dbapi.make_new_device_distribution(
            device.id, device.imei, from_agent, to_agent)

        # 2. 更细设备
        device.agent_id = to_agent
        device.owner_agent_id = to_agent
        device.utime = datetime.now()
        db.session.add(device)

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise

    return make_response(jsonify(reply), status_code)


@admin_god_blueprint.route('/device/recycle', methods=["PATCH"])
@login_required
def god_recycle_device():
    dbg('god_recycle_device')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data  = request.get_json()
        imei  = data['imei']
    except:
        print_exception_info()
        raise ApiError('update devices error', error.ERROR_PARAM)

    god = dbapi.get_god(openluat_user_id=current_user.id)
    if not god:
        raise ApiError('ERROR_GOD_NOT_FOUND', error.ERROR_GOD_NOT_FOUND)

    role_bit = int(current_user.role[5])
    if role_bit not in (1, 2):
        raise ApiError('ERROR_AGENT_NO_PERMISSION', error.ERROR_AGENT_NO_PERMISSION)

    device = dbapi.get_device(imei=imei)
    if not device:
        raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)
    if role_bit == 1:
        god_agents = dbapi.get_god_agent(god_id=god.id)
        g = (god_agent.agent_id for god_agent in god_agents)
        if device.agent_id not in g:
            raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)

    update = {}
    update['agent_id'] = 0
    update['address_id'] = 0
    update['salesman_agent_id'] = 0
    update['l4'] = 1
    update['l3'] = 0
    update['l2'] = 0
    update['l1'] = 0

    device = dbapi.update_device(device, **update)

    # device_distribution
    dbapi.delete_device_distribution_total(imei)

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


@admin_god_blueprint.route('/device/query', methods=["POST"])
@login_required
def god_get_device():
    dbg('god_get_device')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data  = request.get_json()
        imei = data.get('imei')
        device_id = data.get('device_id')
        dbg(data)
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    god = dbapi.get_god(openluat_user_id=current_user.id)
    if not god:
        raise ApiError('ERROR_GOD_NOT_FOUND', error.ERROR_GOD_NOT_FOUND)

    role_bit = int(current_user.role[5])
    if role_bit not in (1, 2):
        raise ApiError('ERROR_AGENT_NO_PERMISSION', error.ERROR_AGENT_NO_PERMISSION)

    device = None
    if imei:
        device = dbapi.get_device(imei=imei)
    elif device_id:
        device = dbapi.get_device(id=int(device_id))
    if not device:
        raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)
    if role_bit == 1:
        god_agents = dbapi.get_god_agent(god_id=god.id)
        g = (god_agent.agent_id for god_agent in god_agents)
        if device.agent_id not in g:
            raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)

    device_address = dbapi.get_device_address(id=device.address_id)
    address = ""
    if device_address:
        address = device_address.address
    agentname = ''
    agent = dbapi.get_agent(id=device.owner_agent_id)
    if agent:
        agentname = agent.name

    reply['data'] = {
        'id': device.id,
        'imei': device.imei,
        'address': address,
        'operator': agentname,
        'remark': device.remark
    }

    return make_response(jsonify(reply), status_code)


@admin_god_blueprint.route('/device/fuzzy_query/<field>', methods=["POST"])
@login_required
def god_fuzzy_query_device(field):
    dbg('god_fuzzy_query_device')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        assert(field in ('imei'))
        data = request.get_json()
        value = data[field]
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    kwargs = {field: value}

    res = dbapi.fuzzy_query_all_device(**kwargs)
    reply['data'] = res

    return make_response(jsonify(reply), status_code)


@admin_god_blueprint.route('/info/update', methods=["POST"])
@login_required
def update_god_info():
    dbg('update_god_info')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        update = request.form['update']
        update = json.loads(update)
        invalid_keys = ('logo')
        for key in invalid_keys:
            assert(key not in update)

        imag_file = request.files.get('0')
        if imag_file:
            postfix = request.form['postfix']

    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    god = dbapi.get_god(openluat_user_id=current_user.id)
    god_id = god.id

    if not update:
        update = {}

    god_info = dbapi.get_god_info(god_id=god_id)
    if not god_info:
        god_info = dbapi.make_new_god_info(god_id)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

    if imag_file:
        imag_filename = 'logo%d.%s' % (god_id, postfix)
        imag_filepath = os.path.join('app/static/img/logo', imag_filename)
        logo_img      = os.path.join('img/logo', imag_filename)
        if not os.path.exists('app/static/img/logo'):
            os.mkdir('app/static/img/logo')
        dbg("save imag: %s" % imag_filepath)
        imag_file.save(imag_filepath)

        update['logo'] = logo_img

    god_info = dbapi.update_god_info(god_info, **update)

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise

    return make_response(jsonify(reply), status_code)


@admin_god_blueprint.route('/agent/update', methods=["PATCH"])
@login_required
def update_agent():
    dbg('update_agent')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data  = request.get_json()
        agent_id = data['agent_id']
        update   = data['update']

        keys = ('name', 'desc', 'address', 'remark')
        for key in update:
            assert(key in keys)

    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    role_bit = int(current_user.role[5])
    if role_bit != 1:
        raise ApiError('ERROR_AGENT_NO_PERMISSION', error.ERROR_AGENT_NO_PERMISSION)

    agent = dbapi.get_agent(id=agent_id)
    god   = dbapi.get_god(openluat_user_id=current_user.id)
    god_agent = dbapi.get_god_agent(agent_id=agent_id)
    if god.id != god_agent.god_id:
        raise ApiError('ERROR_AGENT_NO_PERMISSION', error.ERROR_AGENT_NO_PERMISSION)

    agent = dbapi.update_agent(agent, **update)

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise

    return make_response(jsonify(reply), status_code)