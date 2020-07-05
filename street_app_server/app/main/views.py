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
from flask import Flask, request, session, jsonify, send_from_directory
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

# wechatsdk
import app.third_party.wechatsdk as wechatsdk

# alisdk
import app.third_party.alisdk as alisdk

# blueprint
from . import main_blueprint


@main_blueprint.errorhandler(ApiError)
def handle_api_error(current_error):
    dbg((current_error.msg, current_error.error_no))
    error_info = error.get_error_info(current_error.error_no)
    return make_response(jsonify({'code':current_error.error_no, 'msg':error_info[0]}), error_info[1])


@main_blueprint.errorhandler(Exception)
def handle_base_exception(current_error):
    print_exception_info()
    return make_response(json.dumps({'code':99, 'msg':'server error'}), 500)


def oauth_required(func):
    @wraps(func)
    def wrapper(*args, **kws):
        # session['openid'] = 'oEMOtjoiv9HBQiAC7x7BnSDAUuVw'
        user_agent = request.headers.get('User-Agent')
        if 'MicroMessenger' in user_agent:
            dbg('has_openid: %s' % session.get('has_openid'))
            if 'openid' not in session or 'has_openid' not in session:
                dbg(('openid' not in session, 'has_openid' not in session))
                dbg('need to redirect to login')
                next_url = request.url
                session['next_url'] = next_url
                return redirect(url_for('main.login', agent_id=kws['agent_id'], next_url=next_url))
            dbg('call %s():' % func.__name__)
        else:
            dbg('has_openid: %s' % session.get('has_openid'))
            if 'ali_user_id' not in session or 'has_openid' not in session:
                next_url = request.url
                session['next_url'] = next_url
                return redirect(url_for('main.ali_oauth', agent_id=kws['agent_id'], next_url=next_url))
            dbg('call %s():' % func.__name__)
        return func(*args, **kws)
    return wrapper


@main_blueprint.route('/')
def index():
    dbg('index')
    reply ,status_code = {'code': 0, 'msg': 'hello'}, 200
    return make_response(jsonify(reply), status_code)

@main_blueprint.route('/<path:filename>')
def weixin_txt(filename: str):
    reply ,status_code = {'code': 0, 'msg': 'err'}, 200
    if filename.lower().endswith('.txt'):
        return send_from_directory(config.ADMINPAGE_PATH, filename)
    else:
        return make_response(jsonify(reply), status_code)
    

# @main_blueprint.route('/assets/<path:filename>')
# def assets(filename):
#     return send_from_directory(config.ASSETS_PATH, filename)
#     ...

@main_blueprint.route('/assets/<path:filename>')
def assets(filename):
    #app.register_blueprint(Blueprint('assets', __name__, static_url_path='/assets', static_folder=config.ASSETS_PATH))
    print(f'accessing -> {config.ASSETS_PATH}')
    return send_from_directory(config.ASSETS_PATH, filename)

@main_blueprint.route('/adminpage')
def adminpage():
    return redirect("/adminpage/", code=302)

@main_blueprint.route('/adminpage/')
def adminpage_slash():
    return send_from_directory(config.ADMINPAGE_PATH, 'index.html')

@main_blueprint.route('/adminpage/<path:filename>')
def adminpage_other(filename):
    if filename == 'logo.ico':
        return send_from_directory(config.ADMINPAGE_PATH, 'logo.ico')

    return send_from_directory(config.ADMINPAGE_PATH, 'index.html')

@main_blueprint.route('/succ')
def succ():
    return render_template('succ.html')


@main_blueprint.route('/fail')
def fail():
    message = '操作失败'
    return render_template('fail.html', message=message)


@main_blueprint.route('/login/<agent_id>')
def login(agent_id):
    dbg('login')
    code  = request.args.get('code')
    state = request.args.get('state')

    wechat_config = dbapi.get_wechat_config(agent_id=int(agent_id))
    appid       = wechat_config.appid
    appsecret   = wechat_config.appsecret

    dbg((appid, appsecret))

    if code and state:

        # succ, res = wechatsdk.get_auth_access_token(appid, appsecret, code)
        succ, res = wechatsdk.get_auth_user_info(appid, appsecret, code)
        if succ:
            user_info = res
            openid = res['openid']
            wechat_user = dbapi.get_wechat_user(openid=res['openid'])
            if not wechat_user:
                # # 1. 获取用户信息
                # user_info = wechatsdk.get_wechat_user_info(appid, appsecret, openid)
                # if not user_info:
                #     return 'error'

                # dbg(user_info)

                # 1. 创建用户
                user = dbapi.make_new_user(wechat_body=user_info)
                db.session.commit()
                if not user:
                    raise ApiError('login error', error.ERROR_INSERT_USER)

                # 2. 创建微信用户
                user_info['user_id'] = user.id
                user_info['admin_uid'] = 0    # 普通用户都为0
                wechat_user = dbapi.make_new_wechat_user(user_info)
                db.session.commit()
                if not wechat_user:
                    raise ApiError('login error', error.ERROR_INSERT_WECHAT_USER)
            else:
                user = dbapi.get_user(user_id=wechat_user.user_id)
                if user.nickname == "":
                    wechat_user = dbapi.update_wechat_user(wechat_user, wechat_body=user_info)
                    user = dbapi.update_user(user, wechat_body=user_info)
                    db.session.commit()

            session['openid'] = res.get('openid')
            session['has_openid'] = 1
            next_url = state
            return redirect(next_url)
        else:
            dbg(str(res))
            return 'error'

    elif not code and not state:
        redirect_uri = wechat_config.redirecturl + agent_id
        next_url     = request.args.get('next_url') or session['next_url']
        state        = next_url
        url          = wechatsdk.gen_auth_url(appid, redirect_uri, state)
        dbg('url: %s' % url)
        return redirect(url)


@main_blueprint.route('/doll/<agent_id>/')
@oauth_required
def doll(agent_id):
    dbg('doll')
    # if 'has_openid' in session:
    #     session.pop('has_openid')
    return render_template('doll_machine.html')


@main_blueprint.route('/chair/<agent_id>/')
@oauth_required
def chair(agent_id):
    # if 'has_openid' in session:
    #     session.pop('has_openid')
    return render_template('massage_chair.html')


@main_blueprint.route('/uart/<agent_id>/')
@oauth_required
def uart(agent_id):
    # if 'has_openid' in session:
    #     session.pop('has_openid')
    return render_template('massage_uart.html')


@main_blueprint.route('/chair_nopay/<agent_id>/')
@oauth_required
def chair_nopay(agent_id):
    # if 'has_openid' in session:
    #     session.pop('has_openid')
    return render_template('massage_chair_nopay.html')


@main_blueprint.route('/doll_nopay/<agent_id>/')
@oauth_required
def doll_nopay(agent_id):
    # if 'has_openid' in session:
    #     session.pop('has_openid')
    return render_template('doll_nopay.html')


@main_blueprint.route('/chair_coupon/<agent_id>/')
@oauth_required
def chair_coupon(agent_id):
    # if 'has_openid' in session:
    #     session.pop('has_openid')
    return render_template('chair_coupon.html')


@main_blueprint.route('/doll_coupon/<agent_id>/')
@oauth_required
def doll_coupon(agent_id):
    # if 'has_openid' in session:
    #     session.pop('has_openid')
    return render_template('doll_coupon.html')


@main_blueprint.route('/pay/')
def pay():
    return render_template('pay.html')


@main_blueprint.route('/member')
def member():
    return render_template('member.html')


@main_blueprint.route('/alitest')
def alitest():
    dbg(request.headers.get('User-Agent'))
    args = request.args
    if 'v' in args:
        requests.args = None
    return render_template('alitest.html')


# @main_blueprint.route('/test')
# def test():
#     return render_template('test.html')


@main_blueprint.route('/bindwechat/<bind_id>')
def bindwechat(bind_id):
    code  = request.args.get('code')
    state = request.args.get('state')

    wechat_bind = dbapi.get_wechat_bind(id=int(bind_id))
    now = datetime.now()
    if not wechat_bind:
        return redirect(url_for('main.fail'))
    elif wechat_bind.expires_at < now:
        return render_template('fail.html', message='二维码已超时')

    bind_admin_uid = wechat_bind.admin_uid

    admin_agent = dbapi.get_agent(user_id=bind_admin_uid)
    agent_id = admin_agent.id


    # 第一次应该返回null
    wechat_config = dbapi.get_wechat_config(agent_id=int(agent_id))
    print("WechatConfig: %s" % wechat_config)
    appid       = wechat_config.appid
    appsecret   = wechat_config.appsecret

    print("WechatConfig here!")

    if code and state:

        succ, res = wechatsdk.get_auth_user_info(appid, appsecret, code)
        if succ:
            wechat_user = dbapi.get_wechat_user(openid=res['openid'])
            if not wechat_user:
                # 1. 创建用户
                user = dbapi.make_new_user(wechat_body=res)
                db.session.commit()
                if not user:
                    raise ApiError('login error', error.ERROR_INSERT_USER)
                # 2. 将旧的关联清除
                old_wechat_user = dbapi.get_wechat_user(admin_uid=bind_admin_uid)
                if old_wechat_user:
                    old_wechat_user = dbapi.update_wechat_user(old_wechat_user, admin_uid=0)
                    db.session.add(old_wechat_user)
                # 3. 创建新的关联
                res['user_id'] = user.id
                res['admin_uid'] = bind_admin_uid
                wechat_user = dbapi.make_new_wechat_user(res)
                db.session.commit()
                if not wechat_user:
                    raise ApiError('bindwechat error', error.ERROR_INSERT_WECHAT_USER)
            else:
                # 1. 将旧的关联清除
                old_wechat_user = dbapi.get_wechat_user(admin_uid=bind_admin_uid)
                if old_wechat_user:
                    old_wechat_user = dbapi.update_wechat_user(old_wechat_user, admin_uid=0)
                    db.session.add(old_wechat_user)
                # 2. 创建新的关联
                wechat_user = dbapi.update_wechat_user(wechat_user, admin_uid=bind_admin_uid)
                db.session.add(wechat_user)
                db.session.commit()

            # 绑定成功
            wechat_bind = dbapi.update_wechat_bind(wechat_bind, status=1)
            db.session.commit()

            return redirect(url_for('main.succ'))
        else:
            dbg(str(res))
            return redirect(url_for('main.fail'))

    elif not code and not state:
        redirect_uri = wechat_config.redirect_bind_url + bind_id
        url          = wechatsdk.gen_auth_url(appid, redirect_uri, state)
        dbg('url: %s' % url)
        return redirect(url)


@main_blueprint.route('/ali_oauth/<agent_id>')
def ali_oauth(agent_id):
    auth_code   = request.args.get('auth_code')
    app_id      = request.args.get('app_id')
    scope       = request.args.get('scope')
    state       = request.args.get('state')

    ali_config = dbapi.get_ali_config(agent_id=int(agent_id))
    appid      = ali_config.appid
    key_path   = ali_config.priv_path

    dbg((auth_code, appid, scope, state))

    if auth_code and app_id and scope:

        succ, res = alisdk.get_auth_access_token(app_id, auth_code, key_path)

        if succ:
            dbg(res['alipay_system_oauth_token_response'])
            ali_user_id = res['alipay_system_oauth_token_response']['alipay_user_id']
            user_id_a   = res['alipay_system_oauth_token_response']['user_id']

            ali_user = dbapi.get_ali_user(ali_user_id=ali_user_id)
            if not ali_user:
                # 1. 创建用户
                user = dbapi.make_new_user(name=user_id_a)
                db.session.commit()
                if not user:
                    raise ApiError('ERROR_INSERT_USER', error.ERROR_INSERT_USER)

                # 2. 创建阿里用户
                ali_user = dbapi.make_new_ali_user(user.id, user_id_a, ali_user_id)
                db.session.commit()
                if not ali_user:
                    raise ApiError('ERROR_INSERT_ALI_USER', error.ERROR_INSERT_ALI_USER)

            session['ali_user_id'] = ali_user_id
            session['has_openid'] = 1
            next_url = state.replace('|', '&')
            return redirect(next_url)

        else:
            dbg(res)
            return 'error'

    else:
        redirect_uri = config.MaFuAli.REDIRECT_URI + agent_id
        scope        = 'auth_base'
        state        = session['next_url']
        state        = state.replace('&', '|')
        dbg('state: %s' % state)
        url          = alisdk.gen_auth_url(appid, scope, redirect_uri, state)
        dbg('url: %s' % url)
        return redirect(url)