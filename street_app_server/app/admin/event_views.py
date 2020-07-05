#!/usr/bin/env python3
# coding: utf8
# 20170220 anChaOs


# general
import json, time
import requests # for http requests
from datetime import datetime, timedelta, date

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

import app.tool as tool
from app.tool import dbg                    # for print
from app.tool import print_exception_info   # for traceback
from app.tool import gen_imei15             # for gen imei

# wechat
import app.third_party.wechatsdk as wechatsdk
import app.third_party.wechatpay as wechatpay

from app.admin.device_views import agent_id_required

# blueprint
from . import admin_event_blueprint


@admin_event_blueprint.errorhandler(ApiError)
def handle_api_error(current_error):
    dbg((current_error.msg, current_error.error_no))
    error_info = error.get_error_info(current_error.error_no)
    return make_response(jsonify({'code':current_error.error_no, 'msg':error_info[0]}), error_info[1])


@admin_event_blueprint.errorhandler(Exception)
def handle_base_exception(current_error):
    print_exception_info()
    return make_response(json.dumps({'code':99, 'msg':'server error'}), 500)


def check_imei(imei, agent_id):
    dbg('check imei: %s from agent: %d' % (imei, agent_id))
    device = dbapi.db.session.query(dbapi.DeviceDistribution).\
        filter(dbapi.DeviceDistribution.to_agent==agent_id).\
        filter(dbapi.DeviceDistribution.imei==imei).first()
    if device:
        return True
    device = dbapi.db.session.query(dbapi.Device).\
        filter(dbapi.Device.imei==imei).\
        filter(dbapi.Device.agent_id==0).first()
    if device:
        return True
    device = dbapi.db.session.query(dbapi.Device).\
        filter(dbapi.Device.imei==imei).first()
    if not device:
        return True
    return False


@admin_event_blueprint.route('/launch_pulse_signal_deivce', methods=['POST'])
@login_required
@agent_id_required
def launch_pulse_signal_deivce():
    dbg('launch_pulse_signal_deivce')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()

        imei = data.get('imei')
        device_id = data.get('device_id')
        pulse = int(data['pulse'])
        money = pulse
        device_type = 1
        duration = 5
        high = int(data['high'])
        low  = int(data['low'])
        async_url  = data.get('async_url')

    except:
        print_exception_info()
        raise ApiError('launch_pulse_signal_deivce error', error.ERROR_PARAM)

    if device_id:
        device = dbapi.get_device(id=device_id)
        if not device:
            raise ApiError('no permision', error.ERROR_DEVICE_NO_PERMISSION)
        imei = device.imei
    elif imei:
        imei = imei
    else:
        raise ApiError('no permision', error.ERROR_DEVICE_NO_PERMISSION)

    agent_id = current_user.agent_id

    if not (check_imei(imei, agent_id)):
        raise ApiError('no permision', error.ERROR_DEVICE_NO_PERMISSION)

    if async_url:
        data = {
            'async_url': async_url,
            'topic': 'deveventreq',
            'device_type': device_type,
            'money': money,
            'duration': duration,
            'high': high,
            'low': low,
            'pulse': pulse,
            'imei': imei
        }
        event.send_data_to_device.delay(data, need_to_wait=True)
        return make_response(jsonify(reply), status_code)

    data = bytearray([0x54, device_type])

    data += money.to_bytes(4, 'big')
    data += duration.to_bytes(4, 'big')
    data += high.to_bytes(4, 'big')
    data += low.to_bytes(4, 'big')
    data += pulse.to_bytes(4, 'big')

    dbg(data)

    if async_url:
        event.send_data_to_device.delay(async_url, 'deveventreq', imei,
            data, need_to_wait=True)
        return make_response(jsonify(reply), status_code)

    result = tool.send_data_to_device('deveventreq', imei, data, need_to_wait=True)

    if result == 0:
        return make_response(jsonify(reply), status_code)
    elif result['result'] == 0:
        raise ApiError("ERROR_FAIL", error.ERROR_DEVICE_BUSY)
    elif result['result'] == 1:
        return make_response(jsonify(reply), status_code)


@admin_event_blueprint.route('/launch_relay_signal_deivce', methods=['POST'])
@login_required
@agent_id_required
def launch_relay_signal_deivce():
    dbg('launch_relay_signal_deivce')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()

        imei = data.get('imei')
        device_id = data.get('device_id')
        duration = int(data['duration'])
        device_type = int(data.get('device_type', 0))
        pulse = 1
        money = pulse
        high = 500
        low  = 4294967295   # 'ffffffff'
        async_url  = data.get('async_url')

    except:
        print_exception_info()
        raise ApiError('launch_relay_signal_deivce error', error.ERROR_PARAM)

    agent_id = current_user.agent_id

    if device_id:
        device = dbapi.get_device(id=device_id)
        if not device:
            raise ApiError('no permision', error.ERROR_DEVICE_NO_PERMISSION)
        imei = device.imei
    elif imei:
        imei = imei
    else:
        raise ApiError('no permision', error.ERROR_DEVICE_NO_PERMISSION)

    if not (check_imei(imei, agent_id)):
        raise ApiError('no permision', error.ERROR_DEVICE_NO_PERMISSION)

    if async_url:
        data = {
            'async_url': async_url,
            'topic': 'deveventreq',
            'device_type': device_type,
            'money': money,
            'duration': duration,
            'high': high,
            'low': low,
            'pulse': pulse,
            'imei': imei
        }
        event.send_data_to_device.delay(data, need_to_wait=True)
        return make_response(jsonify(reply), status_code)

    data = bytearray([0x54, device_type])

    data += money.to_bytes(4, 'big')
    data += duration.to_bytes(4, 'big')
    data += high.to_bytes(4, 'big')
    data += low.to_bytes(4, 'big')
    data += pulse.to_bytes(4, 'big')

    dbg(data)
    result = tool.send_data_to_device('deveventreq', imei, data, need_to_wait=True)

    if result == 0:
        raise ApiError("ERROR_FAIL", error.ERROR_FAIL)
    elif result['result'] == 0:
        raise ApiError("ERROR_FAIL", error.ERROR_DEVICE_BUSY)
    elif result['result'] == 1:
        return make_response(jsonify(reply), status_code)