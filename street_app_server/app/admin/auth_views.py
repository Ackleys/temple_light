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
from . import admin_auth_blueprint


@admin_auth_blueprint.errorhandler(ApiError)
def handle_api_error(current_error):
    dbg((current_error.msg, current_error.error_no))
    error_info = error.get_error_info(current_error.error_no)
    return make_response(jsonify({'code':current_error.error_no, 'msg':error_info[0]}), error_info[1])


@admin_auth_blueprint.errorhandler(Exception)
def handle_base_exception(current_error):
    print_exception_info()
    return make_response(json.dumps({'code':99, 'msg':'server error'}), 500)


def check_openid(func):
    @wraps(func)
    def wrapper(*args, **kws):
        # session['openid'] = 'oEMOtjoiv9HBQiAC7x7BnSDAUuVw'
        if 'openid' not in session:
            # 比如这里产生一个api错误, 需要错误描述和错误号, 其中错误描述前端用不到
            raise ApiError('do not login', error.ERROR_NO_LOGIN)
        wechat_user = dbapi.get_wechat_user(openid=session['openid'])
        if not wechat_user:
            raise ApiError('do not login', error.ERROR_NO_LOGIN)
        g.wechat_user = wechat_user
        return func(*args, **kws)
    return wrapper


@admin_auth_blueprint.route('/unlogin')
def unlogin():
    dbg('unlogin')
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    raise ApiError('unlogin', error.ERROR_NO_LOGIN)
    return make_response(jsonify(reply), status_code)

11
@admin_auth_blueprint.route('/login', methods=["POST"])
def web_login():
    dbg('web_login')
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    try:
        data = request.get_json()
        phone = data['phone']
        pswd  = data['pswd']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    openluat_user = dbapi.get_openluat_user(phone=phone)
    if not openluat_user:
        raise ApiError('ERROR_NO_USER', error.ERROR_NO_USER)

    if not openluat_user.verify_password(pswd):
        raise ApiError('ERROR_WRONG_PSWD', error.ERROR_WRONG_PSWD)

    login_user(openluat_user)

    openluat_role  = openluat_user.role[5]
    user_id        = openluat_user.id
    data = {
        'role': 0
    }
    if openluat_role == '0':
        agent = dbapi.get_agent(user_id=user_id)
        if agent:
            god_info = get_god_info_common(agent)
            data['common'] = {
                'logo': url_for('static', filename=god_info.logo),
                'title': god_info.title
            }
            agent_id = agent.id
            joinup = check_joinup_available(agent_id)
            joinuped = get_joinup_status(agent_id)
            data['role'] = 2
            data['agent'] = {
                'id': agent.id,
                'salesman': agent.salesman,
                'level': agent.level,
                'slevel': agent.slevel,
                'expandable': agent.expandable,
                'withdrawable': agent.withdrawable,
                'name': agent.name,
                'phone': agent.phone,
                'email': agent.email,
                'desc': agent.desc,
                'address': agent.address,
                'remark':agent.remark,
                'joinup': joinup,
                'joinuped': joinuped
            }
        else:
            advertiser = dbapi.get_advertiser(user_id=user_id)
            if advertiser:
                god_info = get_god_info_common(advertiser)
                data['common'] = {
                    'logo': url_for('static', filename=god_info.logo),
                    'title': god_info.title
                }
                top_agent = get_top_agent(advertiser)
                data['role'] = 3
                data['advertiser'] = {
                    'id': advertiser.id,
                    'name': advertiser.name,
                    'phone': advertiser.phone,
                    'email': advertiser.email,
                    'desc': advertiser.desc,
                    'address': advertiser.address,
                    'remark': advertiser.remark
                }
    elif openluat_role in ('1', '2'):
        god = dbapi.get_god(openluat_user_id=user_id)
        if god:
            god_info = get_god_info_common(god)
            data['common'] = {
                'logo': url_for('static', filename=god_info.logo),
                'title': god_info.title
            }
            data['role'] = 1
            data['god'] = {
                'level': int(openluat_role),
                'id': god.id,
                'name': god.name
            }

    reply['data'] = data

    return make_response(jsonify(reply), status_code)


@admin_auth_blueprint.route('/logout')
@login_required
def logout():
    dbg('logout')
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    logout_user()
    return make_response(jsonify(reply), status_code)


@admin_auth_blueprint.route('/cur')
@login_required
def get_cur_user_info():
    dbg('get_cur_user_info')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    """
        role: 1god 2agent 3advertiser 0other
    """

    openluat_role  = current_user.role[5]
    user_id        = current_user.id
    data = {
        'role': 0
    }
    if openluat_role == '0':
        agent = dbapi.get_agent(user_id=user_id)
        if agent:
            god_info = get_god_info_common(agent)
            data['common'] = {
                'logo': url_for('static', filename=god_info.logo),
                'title': god_info.title
            }
            agent_id = agent.id
            joinup = check_joinup_available(agent_id)
            joinuped = get_joinup_status(agent_id)
            data['role'] = 2
            data['agent'] = {
                'id': agent.id,
                'salesman': agent.salesman,
                'level': agent.level,
                'slevel': agent.slevel,
                'expandable': agent.expandable,
                'withdrawable': agent.withdrawable,
                'name': agent.name,
                'phone': agent.phone,
                'email': agent.email,
                'desc': agent.desc,
                'address': agent.address,
                'remark':agent.remark,
                'joinup': joinup,
                'joinuped': joinuped
            }
        else:
            advertiser = dbapi.get_advertiser(user_id=user_id)
            if advertiser:
                god_info = get_god_info_common(advertiser)
                data['common'] = {
                    'logo': url_for('static', filename=god_info.logo),
                    'title': god_info.title
                }
                data['role'] = 3
                data['advertiser'] = {
                    'id': advertiser.id,
                    'name': advertiser.name,
                    'phone': advertiser.phone,
                    'email': advertiser.email,
                    'desc': advertiser.desc,
                    'address': advertiser.address,
                    'remark': advertiser.remark
                }
    elif openluat_role in ('1', '2'):
        god = dbapi.get_god(openluat_user_id=user_id)
        if god:
            god_info = get_god_info_common(god)
            data['common'] = {
                'logo': url_for('static', filename=god_info.logo),
                'title': god_info.title
            }
            data['role'] = 1
            data['god'] = {
                'level': int(openluat_role),
                'id': god.id,
                'name': god.name
            }

    reply['data'] = data

    return make_response(jsonify(reply), status_code)


@admin_auth_blueprint.route('/change_pswd', methods=["PATCH"])
@login_required
def change_pswd():
    dbg('change_pswd')
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    try:
        data = request.get_json()
        old_pswd = data['old_pswd']
        new_pswd = data['new_pswd']
    except:
        print_exception_info()
        raise ApiError('change pswd error', error.ERROR_PARAM)

    if not current_user.verify_password(old_pswd):
        raise ApiError('web login error', error.ERROR_WRONG_PSWD)

    dbapi.update_openluat_user(current_user, password=new_pswd)
    db.session.commit()

    return make_response(jsonify(reply), status_code)


# TODO RESET PASSWORD