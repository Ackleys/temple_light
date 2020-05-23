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
from . import admin_openapp_blueprint


@admin_openapp_blueprint.errorhandler(ApiError)
def handle_api_error(current_error):
    dbg((current_error.msg, current_error.error_no))
    error_info = error.get_error_info(current_error.error_no)
    return make_response(jsonify({'code':current_error.error_no, 'msg':error_info[0]}), error_info[1])


@admin_openapp_blueprint.errorhandler(Exception)
def handle_base_exception(current_error):
    print_exception_info()
    return make_response(json.dumps({'code':99, 'msg':'server error'}), 500)


def check_openid(func):
    @wraps(func)
    def wrapper(*args, **kws):
        # session['openid'] = 'oEMOtjoiv9HBQiAC7x7BnSDAUuVw'
        if 'openid' not in session:
            raise ApiError('do not login', error.ERROR_NO_LOGIN)
        wechat_user = dbapi.get_wechat_user(openid=session['openid'])
        if not wechat_user:
            raise ApiError('do not login', error.ERROR_NO_LOGIN)
        g.wechat_user = wechat_user
        return func(*args, **kws)
    return wrapper


@admin_openapp_blueprint.route('/create', methods=["PUT"])
@login_required
def create_app():
    dbg('create_app')

    try:
        data = request.get_json()
        appname = data['appname']
        appdesc = data['appdesc']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    send_data = data
    send_data['user_id'] = current_user.id
    send_data['project'] = 5    # mafu 固定为5

    r = requests.put('https://api.openluat.com/auth/create', data=send_data)
    reply = r.json()
    status_code = r.status_code

    return make_response(jsonify(reply), status_code)


@admin_openapp_blueprint.route('/copy', methods=["PUT"])
@login_required
def copy_app():
    dbg('copy_app')
    try:
        data = request.get_json()
        appid = data['appid']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    send_data = data
    send_data['project'] = 5    # mafu 固定为5

    r = requests.put('https://api.openluat.com/auth/copy', data=send_data)
    reply = r.json()
    status_code = r.status_code

    return make_response(jsonify(reply), status_code)


@admin_openapp_blueprint.route('/get', methods=["POST"])
@login_required
def get_app():
    dbg('get_app')
    try:
        data = request.get_json()
        appid = data['appid']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    send_data = data

    r = requests.post('https://api.openluat.com/auth/get', data=send_data)
    reply = r.json()
    status_code = r.status_code

    return make_response(jsonify(reply), status_code)


@admin_openapp_blueprint.route('/getall', methods=["POST"])
@login_required
def get_all_app():
    dbg('get_all_app')
    try:
        data = request.get_json()
        project = data['project']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    send_data = data
    send_data['user_id'] = current_user.id
    send_data['project'] = project

    r = requests.post('https://api.openluat.com/auth/getall', data=send_data)
    reply = r.json()
    status_code = r.status_code

    return make_response(jsonify(reply), status_code)