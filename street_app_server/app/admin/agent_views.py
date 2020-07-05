#!/usr/bin/env python3
# coding: utf8
# 20170220 anChaOs


# general
import os, json, time, calendar
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

from app.tool import dbg                    # for print
from app.tool import print_exception_info   # for traceback
import app.tool as tool

# wechat
import app.third_party.wechatsdk as wechatsdk
import app.third_party.wechatpay as wechatpay

# blueprint
from . import admin_agent_blueprint
from app.admin.device_views import agent_id_required


@admin_agent_blueprint.errorhandler(ApiError)
def handle_api_error(current_error):
    dbg((current_error.msg, current_error.error_no))
    error_info = error.get_error_info(current_error.error_no)
    return make_response(jsonify({'code':current_error.error_no, 'msg':error_info[0]}), error_info[1])


@admin_agent_blueprint.errorhandler(Exception)
def handle_base_exception(current_error):
    print_exception_info()
    return make_response(json.dumps({'code':99, 'msg':'server error'}), 500)


@admin_agent_blueprint.route('/info')
def get_agent_info_without_login():
    dbg('get_cur_agent')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        agent_id = request.args.get('agent_id')
        assert(agent_id)
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    agent = dbapi.get_agent(id=int(agent_id))
    if not agent:
        raise ApiError('ERROR_AGENT_NOT_FOUND', error.ERROR_AGENT_NOT_FOUND)

    god_info = get_god_info_common(agent)

    reply['data'] = {
        'logo': url_for('static', filename=god_info.logo),
        'title': god_info.title
    }
    return make_response(jsonify(reply), status_code)


@admin_agent_blueprint.route('/cur')
@login_required
@agent_id_required
def get_cur_agent():
    dbg('get_cur_agent')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    agent_id = current_user.agent_id
    agent = dbapi.get_agent(id=agent_id)
    if not agent:
        raise ApiError('get_cur_agent error', error.ERROR_AGENT_NOT_FOUND)

    joinup = check_joinup_available(agent_id)

    reply['data'] = {
        'id': agent.id,
        'salesman': agent.salesman,
        'level': agent.level,
        'slevel': agent.slevel,
        'expandable': agent.expandable,
        'name': agent.name,
        'phone': agent.phone,
        'email': agent.email,
        'desc': agent.desc,
        'address': agent.address,
        'remark':agent.remark,
        'joinup': joinup
    }
    return make_response(jsonify(reply), status_code)


@admin_agent_blueprint.route('/add', methods=["PUT"])
@login_required
@agent_id_required
def add_agent():
    dbg('add_agent')
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    try:
        data    = request.get_json()
        salesman = data['salesman']
        level   = data['level']
        slevel  = data['slevel']
        name    = data['name']
        email   = data['email']
        phone   = data['phone']
        address = data['address']
        remark  = data['remark']
        expandable  = data['expandable']
        withdrawable = data['withdrawable']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    target_agent = dbapi.get_agent(phone=phone)
    if target_agent:
        raise ApiError('ERROR_PHONE_EXISTS', error.ERROR_PHONE_EXISTS)

    target_agent = dbapi.get_agent(email=email)
    if target_agent:
        raise ApiError('ERROR_EMAIL_EXISTS', error.ERROR_EMAIL_EXISTS)

    agent_id = current_user.agent_id
    agent = dbapi.get_agent(id=agent_id)
    if not agent:
        raise ApiError('ERROR_AGENT_NO_PERMISSION not agent', error.ERROR_AGENT_NO_PERMISSION)
    if not agent.expandable:
        raise ApiError('ERROR_AGENT_NO_PERMISSION not expandable', error.ERROR_AGENT_NO_PERMISSION)
    if salesman == 0 and agent.salesman == 0 and level >= agent.level:
        raise ApiError('ERROR_AGENT_NO_PERMISSION not allowed level', error.ERROR_AGENT_NO_PERMISSION)
    if agent.salesman == 1 and slevel < agent.slevel:
        raise ApiError('ERROR_AGENT_NO_PERMISSION not allowed slevel', error.ERROR_AGENT_NO_PERMISSION)

    openluat_user = dbapi.get_openluat_user(phone=phone)
    if not openluat_user:
        openluat_user = dbapi.make_new_openluat_user(name, email, phone)
        db.session.commit()

    hook_agent_id = agent_id
    new_agent = dbapi.make_new_agent(salesman, openluat_user.id, hook_agent_id, level,
        slevel, expandable, withdrawable, name, phone, email, address, remark)
    db.session.commit()

    cur_agent_setting = dbapi.get_agent_setting(agent_id=agent_id)
    if not cur_agent_setting:
        cur_agent_setting = dbapi.make_new_agent_setting(agent_id)

    min_withdraw = cur_agent_setting.min_withdraw
    withdraw_fee = cur_agent_setting.withdraw_fee
    wallet_pay_enable = cur_agent_setting.wallet_pay_enable
    agent_setting = dbapi.make_new_agent_setting(new_agent.id, min_withdraw=min_withdraw,
        withdraw_fee=withdraw_fee, wallet_pay_enable=wallet_pay_enable)

    # 默认微信公众号对接
    old_agent_wechat = dbapi.get_agent_wechat(agent_id=agent_id)
    agent_wechat  = dbapi.make_new_agent_wechat(new_agent.id, old_agent_wechat.wechat_config_id)

    # 默认阿里生活号对接
    old_agent_ali = dbapi.get_agent_ali(agent_id=agent_id)
    agent_ali = dbapi.make_new_agent_ali(new_agent.id, old_agent_ali.ali_config_id)

    db.session.commit()

    return make_response(jsonify(reply), status_code)


@admin_agent_blueprint.route('/fetch', methods=['POST'])
@login_required
def get_agent_info():
    dbg('get_agent_info')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data     = request.get_json()
        agent_id = data['agent_id']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    agent = dbapi.get_agent(id=agent_id)
    if not agent:
        raise ApiError('ERROR_AGENT_NOT_FOUND', error.ERROR_AGENT_NOT_FOUND)

    reply['data'] = {
        'id': agent.id,
        'salesman': agent.salesman,
        'level': agent.level,
        'slevel': agent.slevel,
        'name': agent.name,
        'phone': agent.phone,
        'email': agent.email,
        'desc': agent.desc,
        'address': agent.address,
        'remark':agent.remark,
        'expandable': agent.expandable,
        'withdrawable': agent.withdrawable
    }
    return make_response(jsonify(reply), status_code)


@admin_agent_blueprint.route('/search', methods=['POST'])
@login_required
@agent_id_required
def search_agent_info():
    dbg('search_agent_info')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        name = data.get('name', '')
        phone = data.get('phone', '')
        salesman = int(data.get('salesman', 0))

        page  = request.args.get('page', 1, type=int)
        psize = request.args.get('psize', 10, type=int)

    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    agent_id = current_user.agent_id

    count, agents = dbapi.get_agent(fuzzy_name=name, fuzzy_phone=phone,
        hook_agent_id=agent_id, salesman=salesman, page=page, psize=psize)
    
    data = []
    if count:
        for agent in agents:
            info = {
                'id': agent.id,
                'salesman': agent.salesman,
                'level': agent.level,
                'slevel': agent.slevel,
                'name': agent.name,
                'phone': agent.phone,
                'email': agent.email,
                'desc': agent.desc,
                'address': agent.address,
                'remark':agent.remark,
                'expandable': agent.expandable,
                'withdrawable': agent.withdrawable
            }
            data.append(info)

    reply['data'] = {
        'count': count,
        'agents': data
    }
    return make_response(jsonify(reply), status_code)


@admin_agent_blueprint.route('/update', methods=["PATCH"])
@login_required
@agent_id_required
def update_agent():
    dbg('update_agent')
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    try:
        data     = request.get_json()
        agent_id = data['agent_id']
        update   = data['update']
        keys = ('name', 'desc', 'address', 'remark', 'expandable', 'withdrawable')
        for k in update:
            assert(k in keys)
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    agent = dbapi.get_agent(id=agent_id)
    if not agent:
        raise ApiError('ERROR_AGENT_NOT_FOUND', error.ERROR_AGENT_NOT_FOUND)

    cur_agent_id = current_user.agent_id
    print(agent_id, cur_agent_id, agent.hook_agent_id)
    if cur_agent_id not in (agent_id, agent.hook_agent_id):
        raise ApiError('ERROR_AGENT_NO_PERMISSION', error.ERROR_AGENT_NO_PERMISSION)

    agent = dbapi.update_agent(agent, **update)
    db.session.commit()

    return make_response(jsonify(reply), status_code)


@admin_agent_blueprint.route('/sub_agent/fetch')
@login_required
@agent_id_required
def get_sub_agent():
    dbg('get_sub_agent')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    page  = request.args.get('page', 1, type=int)
    psize = request.args.get('psize', 10, type=int)

    agent_id = current_user.agent_id
    count, agents = dbapi.get_agent(hook_agent_id=agent_id, salesman=0, page=page, psize=psize)

    data = []
    if count:
        for agent in agents:
            info = {
                'id': agent.id,
                'name': agent.name,
                'level': agent.level,
                'phone': agent.phone,
                'address': agent.address,
                'expandable': agent.expandable,
                'withdrawable':agent.withdrawable,
                'remark': agent.remark
            }
            data.append(info)

    reply['data'] = {
        'count': count,
        'agents': data
    }

    return make_response(jsonify(reply), status_code)


@admin_agent_blueprint.route('/sub_salesman/onelevel/fetch', methods=["POST"])
@login_required
@agent_id_required
def get_sub_salesman_onelevel():
    dbg('get_sub_salesman_onelevel')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data     = request.get_json()
        agent_id = data['agent_id']
        page  = request.args.get('page', 1, type=int)
        psize = request.args.get('psize', 10, type=int)
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    count, salesmen = dbapi.get_agent(hook_agent_id=agent_id, salesman=1, page=page, psize=psize)

    data = []
    if count:
        for salesman in salesmen:
            info = {
                'id': salesman.id,
                'salesman': salesman.salesman,
                'name': salesman.name,
                'level': salesman.level,
                'slevel': salesman.slevel,
                'phone': salesman.phone,
                'email': salesman.email,
                'address': salesman.address,
                'desc': salesman.desc,
                'expandable': salesman.expandable,
                'remark': salesman.remark
            }
            data.append(info)

    reply['data'] = {
        'count': count,
        'salesmen': data
    }

    return make_response(jsonify(reply), status_code)


@admin_agent_blueprint.route('/sub_salesman/search', methods=['POST'])
@login_required
@agent_id_required
def search_sub_salesman_info():
    dbg('search_sub_salesman_info')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data = request.get_json()
        name = data.get('name', '')
        phone = data.get('phone', '')

        page  = request.args.get('page', 1, type=int)
        psize = request.args.get('psize', 10, type=int)

    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    agent_id = current_user.agent_id

    count, salesmen = dbapi.get_agent(fuzzy_name=name, fuzzy_phone=phone,
        hook_agent_id=agent_id, salesman=1, page=page, psize=psize)
    
    data = []
    if count:
        for salesman in salesmen:
            info = {
                'id': salesman.id,
                'salesman': salesman.salesman,
                'name': salesman.name,
                'level': salesman.level,
                'slevel': salesman.slevel,
                'phone': salesman.phone,
                'email': salesman.email,
                'address': salesman.address,
                'desc': salesman.desc,
                'expandable': salesman.expandable,
                'remark': salesman.remark
            }
            data.append(info)

    reply['data'] = {
        'count': count,
        'salesmen': data
    }
    return make_response(jsonify(reply), status_code)


@admin_agent_blueprint.route('/sub_salesman/fetch')
@login_required
@agent_id_required
def get_sub_salesman():
    dbg('get_sub_salesman')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    agent_id = current_user.agent_id
    salesmen = dbapi.get_agent(hook_agent_id=agent_id, salesman=1, name_id_only=1)

    data = []
    for salesman in salesmen:
        info = {
            'key': salesman[0],     # agent_id
            'title': salesman[1],   # agent name
        }
        salesmen2 = dbapi.get_agent(hook_agent_id=salesman[0], salesman=1, name_id_only=1)
        children = []
        for salesman2 in salesmen2:
            info2 = {
                'key'   : salesman2[0], # agent_id
                'title' : salesman2[1]  # agent name
            }
            salesmen3 = dbapi.get_agent(hook_agent_id=salesman2[0], salesman=1, name_id_only=1)
            children2 = []
            for salesman3 in salesmen3:
                info3 = {
                    'key'   : salesman3[0], # agent_id
                    'title' : salesman3[1]  # agent name
                }
                children2.append(info3)
            info2['children'] = children2
            children.append(info2)
        info['children'] = children
        data.append(info)

    reply['data'] = {
        'salesmen': data
    }

    return make_response(jsonify(reply), status_code)


@admin_agent_blueprint.route('/setting/fetch', methods=["POST"])
@login_required
@agent_id_required
def get_agent_setting():
    dbg('get_agent_setting')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data     = request.get_json()
        target_agent_id = data['target_agent_id']
    except:
        print_exception_info()
        raise ApiError('update agent setting error', error.ERROR_PARAM)

    agent_id = current_user.agent_id
    target_agent = dbapi.get_agent(id=target_agent_id)
    if not target_agent:
        raise ApiError('ERROR_AGENT_NOT_FOUND', error.ERROR_AGENT_NOT_FOUND)

    agent_setting = dbapi.get_agent_setting(agent_id=target_agent_id)
    reply['data'] = {
        'min_withdraw': agent_setting.min_withdraw,
        'withdraw_fee': agent_setting.withdraw_fee,
        'wallet_pay_enable': agent_setting.wallet_pay_enable,
        'trans_url': agent_setting.trans_url
    }

    return make_response(jsonify(reply), status_code)


@admin_agent_blueprint.route('/setting/update', methods=["PATCH"])
@login_required
@agent_id_required
def update_agent_setting():
    dbg('update_agent_setting')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data     = request.get_json()
        target_agent_id = data['target_agent_id']
        update   = data['update']
        dbg(update)
        keys = ('min_withdraw', 'withdraw_fee', 'wallet_pay_enable', 'trans_url')
        for k in update:
            assert(k in keys)
    except:
        print_exception_info()
        raise ApiError('update agent setting error', error.ERROR_PARAM)

    if 'min_withdraw' in update and update['min_withdraw'] < 200:
        raise ApiError('ERROR_SETTING_WITH_DRAW', error.ERROR_SETTING_WITH_DRAW)

    if 'withdraw_fee' in update and update['withdraw_fee'] < 0.006:
        raise ApiError('ERROR_SETTING_WITHDRAW_FEE', error.ERROR_SETTING_WITHDRAW_FEE)

    agent_id = current_user.agent_id
    target_agent = dbapi.get_agent(id=target_agent_id)
    if not target_agent:
        raise ApiError('ERROR_AGENT_NOT_FOUND', error.ERROR_AGENT_NOT_FOUND)

    if target_agent.hook_agent_id != 0 and target_agent.hook_agent_id != agent_id:
        raise ApiError('ERROR_AGENT_NO_PERMISSION', error.ERROR_AGENT_NO_PERMISSION)

    # 更新目标代理
    agent_setting = dbapi.get_agent_setting(agent_id=target_agent_id)
    if not agent_setting:
        agent_setting = dbapi.make_new_agent_setting(target_agent_id)
        db.session.commit()
    dbapi.update_agent_setting(agent_setting, **update)

    # 更新level3的代理
    agents3 = dbapi.get_agent(hook_agent_id=target_agent_id)
    for agent3 in agents3:
        agent_id = agent3.id
        agent_setting = dbapi.get_agent_setting(agent_id=agent_id)
        if not agent_setting:
            agent_setting = dbapi.make_new_agent_setting(agent_id)
            db.session.commit()
        dbapi.update_agent_setting(agent_setting, **update)

        # 更新level2的代理
        agents2 = dbapi.get_agent(hook_agent_id=agent_id)
        for agent2 in agents2:
            agent_id = agent2.id
            agent_setting = dbapi.get_agent_setting(agent_id=agent_id)
            if not agent_setting:
                agent_setting = dbapi.make_new_agent_setting(agent_id)
                db.session.commit()
            dbapi.update_agent_setting(agent_setting, **update)

            # 更新level1的代理
            agents1 = dbapi.get_agent(hook_agent_id=agent_id)
            for agent1 in agents1:
                agent_id = agent1.id
                agent_setting = dbapi.get_agent_setting(agent_id=agent_id)
                if not agent_setting:
                    agent_setting = dbapi.make_new_agent_setting(agent_id)
                    db.session.commit()
                dbapi.update_agent_setting(agent_setting, **update)

    db.session.commit()

    return make_response(jsonify(reply), status_code)


@admin_agent_blueprint.route('/wechat_config/add', methods=['POST'])
@login_required
@agent_id_required
def add_wechat_config():
    dbg('add_wechat_config')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:

        name        = request.form['name']
        shortname   = request.form['shortname']
        appid       = request.form['appid']
        appsecret   = request.form['appsecret']
        mchid       = request.form['mchid']
        mchkey      = request.form['mchkey']
        txtname     = request.form['txtname']

        cert_file   = request.files['0']
        text_file   = request.files['1']
        imag_file   = request.files['2']

    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    agent_id = current_user.agent_id
    joinup = check_joinup_available(agent_id)
    if not joinup['wechat']:
        raise ApiError('ERROR_WECHAT_CONFIG_EXISTS', error.ERROR_WECHAT_CONFIG_EXISTS)

    wechat_config = dbapi.get_wechat_config(appid=appid)
    if wechat_config:
        raise ApiError('ERROR_WECHAT_CONFIG_EXISTS', error.ERROR_WECHAT_CONFIG_EXISTS)

    agent_id = current_user.agent_id

    if not os.path.exists('tmp'):
        os.mkdir("tmp")

    cert_filename = '%dcert.zip' % agent_id
    cert_filepath = os.path.join('tmp', cert_filename)
    dbg("save cert: %s" % cert_filepath)
    cert_file.save(cert_filepath)

    text_filename = txtname
    text_filepath = os.path.join('../streetweb', text_filename)
    dbg("save text: %s" % text_filepath)
    text_file.save(text_filepath)

    imag_filename = 'qrcode_%d' % agent_id
    imag_filepath = os.path.join('app/static/img/qrcode', imag_filename)
    qrcode_img    = os.path.join('img/qrcode', imag_filename)
    if not os.path.exists('app/static/img/qrcode'):
        os.mkdir('app/static/img/qrcode')
    dbg("save imag: %s" % imag_filepath)
    imag_file.save(imag_filepath)

    import platform
    if 'Windows' in platform.platform():
        config.WECHAT_PAY_KEY_PATH = 'keys/pro'
    output_dir = config.WECHAT_PAY_KEY_PATH + '/' + shortname
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    tool.extract(cert_filepath, output_dir)

    if os.path.exists(cert_filepath):
        os.remove(cert_filepath)

    redirecturl = config.WECHAT_LIST[1].REDIRECT_URI
    redirect_bind_url = config.WECHAT_LIST[1].REDIRECT_BIND_URL
    key_path = output_dir
    wechat_config = dbapi.make_new_wechat_config(name, appid, appsecret, mchid, mchkey,
        redirecturl, redirect_bind_url, key_path, qrcode_img)
    db.session.commit()

    # 更新各级代理的微信信息
    agent_wechat = dbapi.update_agent_wechat(agent_id, wechat_config.id)
    agents3 = dbapi.get_agent(hook_agent_id=agent_id)
    for agent3 in agents3:
        agent_wechat = dbapi.update_agent_wechat(agent3.id, wechat_config.id)
        agents2 = dbapi.get_agent(hook_agent_id=agent3.id)
        for agent2 in agents2:
            agent_wechat = dbapi.update_agent_wechat(agent2.id, wechat_config.id)
            agents1 = dbapi.get_agent(hook_agent_id=agent2.id)
            for agent1 in agents1:
                agent_wechat = dbapi.update_agent_wechat(agent1.id, wechat_config.id)

    db.session.commit()

    return make_response(jsonify(reply), status_code)


@admin_agent_blueprint.route('/ali_config/add', methods=['POST'])
@login_required
@agent_id_required
def add_ali_config():
    dbg('add_ali_config')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:

        name        = request.form['name']
        shortname   = request.form['shortname']
        appid       = request.form['appid']

        priv_file   = request.files['0']
        pub_file    = request.files['1']

    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    agent_id = current_user.agent_id

    joinup = check_joinup_available(agent_id)
    if not joinup['ali']:
        raise ApiError('ERROR_ALI_CONFIG_EXISTS', error.ERROR_ALI_CONFIG_EXISTS)

    ali_config = dbapi.get_ali_config(appid=appid)
    if ali_config:
        raise ApiError('ERROR_ALI_CONFIG_EXISTS', error.ERROR_ALI_CONFIG_EXISTS)

    import platform
    if 'Windows' in platform.platform():
        config.ALI_PAY_KEY_PATH = 'keys/pro/alipay'
    if not os.path.exists(config.ALI_PAY_KEY_PATH):
        os.mkdir(config.ALI_PAY_KEY_PATH)
    output_dir = config.ALI_PAY_KEY_PATH + '/' + shortname
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    priv_path = os.path.join(output_dir, 'rsa_private_key.pem')
    dbg("save priv: %s" % priv_path)
    priv_file.save(priv_path)
    pub_path = os.path.join(output_dir, 'rsa_public_key.pem')
    dbg("save pub: %s" % pub_path)
    pub_file.save(pub_path)

    ali_config = dbapi.make_new_ali_config(name, appid, priv_path, pub_path)
    db.session.commit()

    # 更新各级代理的支付宝信息
    agent_ali = dbapi.update_agent_ali(agent_id, ali_config.id)
    agents3 = dbapi.get_agent(hook_agent_id=agent_id)
    for agent3 in agents3:
        agent_ali = dbapi.update_agent_ali(agent3.id, ali_config.id)
        agents2 = dbapi.get_agent(hook_agent_id=agent3.id)
        for agent2 in agents2:
            agent_ali = dbapi.update_agent_ali(agent2.id, ali_config.id)
            agents1= dbapi.get_agent(hook_agent_id=agent2.id)
            for agent1 in agents1:
                agent_ali = dbapi.update_agent_ali(agent1.id, ali_config.id)

    db.session.commit()

    return make_response(jsonify(reply), status_code)


@admin_agent_blueprint.route('/joinup_guide/<type>')
def get_joinup_guide(type):
    dbg('get_joinup_guide')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    link = ''
    if type == 'wechat':
        link = url_for('static', filename='files/wechat.pdf')
    if type == 'ali':
        link = url_for('static', filename='files/ali.pdf')

    reply['data'] = {
        'link': link
    }

    return make_response(jsonify(reply), status_code)