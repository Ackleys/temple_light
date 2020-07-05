#!/usr/bin/env python3
# coding: utf8
# 20170220 anChaOs


# general
import json, time, calendar, math
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
from app.tool import gen_imei15             # for gen imei

# wechat
import app.third_party.wechatsdk as wechatsdk
import app.third_party.wechatpay as wechatpay

# refund api
from app.api.apis import pay_refund

# blueprint
from . import admin_economic_blueprint
from app.admin.device_views import agent_id_required


@admin_economic_blueprint.errorhandler(ApiError)
def handle_api_error(current_error):
    dbg((current_error.msg, current_error.error_no))
    error_info = error.get_error_info(current_error.error_no)
    return make_response(jsonify({'code':current_error.error_no, 'msg':error_info[0]}), error_info[1])


@admin_economic_blueprint.errorhandler(Exception)
def handle_base_exception(current_error):
    print_exception_info()
    return make_response(json.dumps({'code':99, 'msg':'server error'}), 500)


@admin_economic_blueprint.route('/manual_refund', methods=["POST"])
@login_required
@agent_id_required
def manual_refund():
    dbg('manual_refund')
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    try:
        data    = request.get_json()
        pay_id  = data['pay_id']
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    pay = dbapi.get_pay(pay_id=pay_id)
    if not pay:
        raise ApiError('ERROR_PAY_NOT_FOUND', error.ERROR_PAY_NOT_FOUND)

    # 充值套餐、广告优惠券，不支持退款
    not_support_list = (99, 199)
    if pay.cat in not_support_list:
        raise ApiError('not support this', error.ERROR_AGENT_NO_PERMISSION)

    imei = pay.imei

    device = dbapi.get_device(imei=imei)
    if not device:
        raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)

    if device.owner_agent_id != current_user.agent_id:
        raise ApiError('ERROR_AGENT_NO_PERMISSION', error.ERROR_AGENT_NO_PERMISSION)

    refund_available = check_refund_available(device, pay.total_fee)
    if not refund_available:
        raise ApiError('ERROR_REFUND_NOT_AVAILABLE', error.ERROR_REFUND_NOT_AVAILABLE)

    if pay.status != 1:
        raise ApiError('ERROR_NOT_PAY', error.ERROR_NOT_PAY)

    product = dbapi.get_product(product_id=pay.product_id)
    if not product:
        raise ApiError('can not find product: %s' % pay.product_id)

    # 退款
    pay_refund(pay, product)

    db.session.commit()

    return make_response(jsonify(reply), status_code)


@admin_economic_blueprint.route('/order/query', methods=["POST"])
@login_required
@agent_id_required
def query_order():
    dbg('query_order')
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    try:
        data    = request.get_json()
        start   = datetime.fromtimestamp(int(data['start']))
        end     = datetime.fromtimestamp(int(data['end']))
        status  = data.get('status')
        address = data.get('address')
        imei    = data.get('imei')
        pay_mode = data.get('pay_mode')
        page    = request.args.get('page', 1, type=int)
        psize   = request.args.get('psize', 10, type=int)
    except:
        print_exception_info()
        raise ApiError('query order error', error.ERROR_PARAM)

    agent_id = current_user.agent_id
    if current_user.cur_agent.salesman:
        count, res = dbapi.query_orders_salesman(start, end, psize, page, agent_id, status, address, imei, pay_mode)
        # agent = dbapi.get_agent(id=current_user.cur_agent.hook_agent_id)
        # salesman = agent.salesman
        # count = 0
        # while salesman:
        #     agent = dbapi.get_agent(id=agent.hook_agent_id)
        #     salesman = agent.salesman
        #     if count == 3:
        #         break
        #     count += 1
        # agent_id = agent.id
    else:
        count, res = dbapi.query_orders(start, end, psize, page, agent_id, status, address, imei, pay_mode)
    data = []
    if count and res:
        for r in res:
            pay, device, device_address = r
            agent = dbapi.get_agent(id=device.owner_agent_id)
            pay_way = ''
            if pay.cat == 100:
                user = dbapi.get_advertiser(user_id=pay.user_id)
                user.nickname = user.name
            else:
                user = dbapi.get_user(user_id=pay.user_id)
            username = ''
            if pay.pay_mode == 1:
                pay_way = '微信'
                if user:
                    username = user.nickname
            if pay.pay_mode == 2:
                pay_way = '支付宝'
                if user:
                    username = user.name
            if pay.pay_mode == 3:
                pay_way = '钱包支付'
                if user:
                    username = user.nickname or user.name
            address = ''
            if device_address:
                address = device_address.address
            info = {
                'id'        : pay.id,
                'username'  : username,
                'time'      : int(pay.ctime.timestamp()),
                'trade_no'  : pay.trade_no,
                'total_fee' : pay.total_fee,
                'pay_way'   : pay_way,
                'status'    : pay.status,
                'device_id' : device.id,
                'imei'      : device.imei,
                'cat'       : device.cat,
                'address'   : address,
                'operator'  : agent.name,
            }
            data.append(info)
    reply['data'] = {
        'orders': data,
        'count' : count
    }
    return make_response(jsonify(reply), status_code)


@admin_economic_blueprint.route('/income/query', methods=["POST"])
@login_required
@agent_id_required
def query_income():
    dbg('query_income')
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    try:
        data    = request.get_json()
        start   = datetime.fromtimestamp(int(data['start']))
        end     = datetime.fromtimestamp(int(data['end']))
        address = data.get('address')
        imei    = data.get('imei')
        page    = request.args.get('page', 1, type=int)
        psize   = request.args.get('psize', 10, type=int)
    except:
        print_exception_info()
        raise ApiError('query income error', error.ERROR_PARAM)

    agent_id = current_user.agent_id

    if current_user.cur_agent.salesman:
        count, res = dbapi.query_devices_income_with_sql_salesman(start, end, page, psize, agent_id, address, imei)
    else:
        count, res = dbapi.query_devices_income_with_sql(start, end, page, psize, agent_id, address, imei)
    data = []
    if count and res:
        for r in res:
            device_id, imei, owner_agent_id, product_min_money,\
                address, online_income, offline_coin = r

            if not address:
                address = ""

            online_income = get_online_income(online_income)
            offline_coin, offline_income = get_offline_coin_and_offline_income(offline_coin, product_min_money)

            agent = dbapi.get_agent(id=owner_agent_id)
            status = dbapi.get_cws_device_status(imei)
            online = -1
            if status:
                online = status.get('online', -1)
            latest_report = dbapi.get_device_latestreport(imei)
            if not latest_report:
                online = 0
            else:
                nowts = datetime.now().timestamp()
                lrts  = latest_report['time'].timestamp()
                if nowts - lrts > 150:
                    if online == 1:
                        online = 0

            info = {
                'id'        : device_id,
                'imei'      : imei,
                'income'    : online_income,
                'online_income': online_income,
                'offline_coin': offline_coin,
                'offline_income': offline_income,
                'status'    : online,
                'address'   : address,
                'operator'  : agent.name,
            }
            data.append(info)
    reply['data'] = {
        'incomes': data,
        'count'  : count
    }
    return make_response(jsonify(reply), status_code)


@admin_economic_blueprint.route('/income/today')
@login_required
@agent_id_required
def today_income():
    dbg('today_income')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    user_id = current_user.id
    agent_id = current_user.agent_id
    today_wallet_income = dbapi.get_today_wallet_income(user_id)
    today_online_income = dbapi.get_today_online_income(agent_id)
    today_offline_coin, today_offline_income = dbapi.get_today_offline_coin(agent_id)

    reply['data'] = {
        'today_wallet_income': today_wallet_income,
        'today_online_income': today_online_income,
        'today_offline_coin' : today_offline_coin,
        'today_offline_income': 0,
        'today_total_income': today_online_income
    }

    return make_response(jsonify(reply), status_code)


'''
    @ freq  : 1表示每天 2表示每月
'''
@admin_economic_blueprint.route('/income/daily', methods=["POST"])
@login_required
@agent_id_required
def daily_income():
    dbg('daily_income')
    reply ,status_code = {'code': 0, 'msg': ''}, 200
    try:
        data    = request.get_json()
        start   = date.fromtimestamp(int(data['start']))
        end     = date.fromtimestamp(int(data['end']))
        freq    = int(data['freq'])
    except:
        print_exception_info()
        raise ApiError('daily income error', error.ERROR_PARAM)

    agent_id = current_user.agent_id

    daily_incomes = dbapi.get_daily_income(start=start, end=end, agent_id=agent_id)
    cur = start
    d_format = '%Y-%m-%d'
    if freq == 2:
        d_format = '%Y-%m'
    data = []
    if freq == 1:
        # 每天
        while cur <= end:
            info = {
                'date': cur.strftime(d_format),
                'income': 0
            }
            for i, daily_income in enumerate(daily_incomes):
                if daily_income.date == cur:
                    info['income'] = daily_income.online_income + daily_income.offline_income
                    daily_incomes.pop(i)
                    break
            data.append(info)
            cur = cur + timedelta(days=1)


    if freq == 2:
        # 每月
        sum_income = 0
        while cur <= end:
            firstday_weekday, month_range = calendar.monthrange(cur.year, cur.month)
            for i, daily_income in enumerate(daily_incomes):
                if daily_income.date.month == cur.month and daily_income.date.year == cur.year:
                    sum_income += daily_income.online_income + daily_income.offline_income
                    daily_incomes.pop(i)
                if cur.day == month_range or len(daily_incomes)==0:
                    break
            if cur.day==month_range or cur == end:
                info = {
                    'date': cur.strftime(d_format),
                    'income': sum_income
                }
                sum_income = 0
                data.append(info)

            cur = cur + timedelta(days=1)

    reply['data'] = data
    return make_response(jsonify(reply), status_code)


@admin_economic_blueprint.route('/bindwechat_url/fetch')
@login_required
@agent_id_required
def get_bindwechat_url():
    dbg('get_bindwechat_url')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    admin_uid  = current_user.id
    expires_at = datetime.now() + timedelta(seconds=60)

    wechat_bind = dbapi.get_wechat_bind(admin_uid=admin_uid)
    if not wechat_bind:
        wechat_bind = dbapi.make_new_wechat_bind(admin_uid, expires_at)
    else:
        wechat_bind = dbapi.update_wechat_bind(wechat_bind, expires_at=expires_at, status=0)

    db.session.commit()

    url = config.BIND_WECHAT_URL + str(wechat_bind.id) + '?t=%d' % int(time.time())
    reply['data'] = {
        'url': url,
        'expires_at': int(wechat_bind.expires_at.timestamp()),
        'status': wechat_bind.status
    }
    return make_response(jsonify(reply), status_code)


@admin_economic_blueprint.route('/bindwechat/query')
@login_required
@agent_id_required
def query_bind_wechat():
    dbg('query_bind_wechat')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    admin_uid  = current_user.id
    wechat_bind = dbapi.get_wechat_bind(admin_uid=admin_uid)
    if not wechat_bind:
        raise ApiError('no wechat_bind')

    url = config.BIND_WECHAT_URL + str(wechat_bind.id)
    reply['data'] = {
        'expires_at': int(wechat_bind.expires_at.timestamp()),
        'status': wechat_bind.status
    }
    return make_response(jsonify(reply), status_code)


@admin_economic_blueprint.route('/wallet/fetch')
@login_required
@agent_id_required
def get_wallet():
    dbg('get_wallet')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    user_id = current_user.id
    agent_id = current_user.agent_id
    wallet = dbapi.get_wallet(user_id=user_id, agent_id=agent_id)
    wechat_user = dbapi.get_wechat_user(admin_uid=user_id)
    nickname = ''
    if not wechat_user:
        nickname = '未绑定微信'
    else:
        nickname = wechat_user.nickname

    total_fee_sum = dbapi.get_pay_to_user(user_id=user_id, total=True)
    wallet = dbapi.get_wallet(user_id=user_id, agent_id=agent_id)
    receipt_sum = dbapi.get_agent_wallet_receipt_sum(wallet.id)

    reply['data'] = {
        'balance': int(wallet.balance),
        'withdrawable_balance': int(wallet.withdrawable_balance),
        'nickname': nickname,
        'total_fee_sum': total_fee_sum,
        'receipt_sum': receipt_sum,
    }
    return make_response(jsonify(reply), status_code)


@admin_economic_blueprint.route('/wechat_withdraw', methods=["PUT"])
@login_required
@agent_id_required
def wechat_withdraw():
    dbg('wechat_withdraw')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        data    = request.get_json()
        fee     = data['fee']
        desc    = data['desc']
        remark  = data['remark']
        pswd    = data['pswd']
        assert(isinstance(fee, int))
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    if not current_user.verify_password(pswd):
        raise ApiError('ERROR_WRONG_PSWD', error.ERROR_WRONG_PSWD)

    agent_id = current_user.agent_id
    agent_setting = dbapi.get_agent_setting(agent_id=agent_id)
    if fee < agent_setting.min_withdraw:
        dbg('fee: %d\tmin_withdraw: %d' % (fee, agent_setting.min_withdraw))
        raise ApiError('ERROR_WITHDRAW_FEE', error.ERROR_WITHDRAW_FEE)

    wallet = dbapi.get_wallet(user_id=current_user.id, agent_id=agent_id)
    if fee > wallet.withdrawable_balance:
        dbg('fee: %d\twithdrawable_balance: %d' % (fee, wallet.withdrawable_balance))
        raise ApiError('ERROR_WITHDRAW_FEE', error.ERROR_WITHDRAW_FEE)

    user_id = current_user.id
    wechat_user = dbapi.get_wechat_user(admin_uid=user_id)
    if not wechat_user:
        # TODO 错误类型需要优化
        raise ApiError('ERROR_NO_USER', error.ERROR_NO_USER)
    to_openid = wechat_user.openid
    to_nickname = wechat_user.nickname
    max_id  = dbapi.get_max_pay_to_user_id()
    str_max_id = '%04d' % max_id
    if len(str_max_id) > 4:
        str_max_id = str_max_id[-4:]
    trade_no = 'P' + str(int(time.time())) + str_max_id

    wechat_agent_id = get_top_wechat_agent_id(agent_id)
    if not wechat_agent_id:
        raise ApiError('ERROR_TOP_WECHAT_NOT_FOUND', error.ERROR_NO_USER)

    pay_to_user = dbapi.make_new_pay_to_user(wechat_agent_id, user_id, to_openid, to_nickname, trade_no,
        fee, desc, remark)
    db.session.commit()

    kwargs = {
        'openid': to_openid,
        'trade_no': trade_no,
        'money': fee - math.ceil(fee*agent_setting.withdraw_fee),   # 向上取整
        'desc': desc,
        'agent_id': agent_id
    }
    err, result = wechatpay.pay_to_user(**kwargs)
    if err:
        pay_to_user = dbapi.update_pay_to_user(pay_to_user, status=2,
            notify_res=str(err))
        db.session.add(pay_to_user)
        db.session.commit()
        raise ApiError('wechat withdraw error', error.ERROR_PAY_TO_USER_FAIL)

    payment_no = result['payment_no']
    pay_to_user = dbapi.update_pay_to_user(pay_to_user, status=1,
        notify_res=str(result), payment_no=payment_no)
    db.session.add(pay_to_user)

    wallet_id = wallet.id
    trade_type = dbapi.WALLET_TRADE_TYPE_WECHAT_WITHDRAW
    receipt = -fee
    withdrawable_receipt = -fee
    wallet_receipt = dbapi.make_new_wallet_receipt(user_id, agent_id, wallet_id,
        trade_type, receipt, withdrawable_receipt, remark, payment_no)

    balance = wallet.balance - fee
    withdrawable_balance = wallet.withdrawable_balance - fee
    wallet = dbapi.update_wallet(wallet, balance=balance, withdrawable_balance=withdrawable_balance)
    db.session.add(wallet)
    db.session.commit()

    return make_response(jsonify(reply), status_code)


@admin_economic_blueprint.route('/wechat_withdraw/fetch')
@login_required
@agent_id_required
def get_wechat_withdraw():
    dbg('get_wechat_withdraw')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        page  = int(request.args.get('page', 1))
        psize = int(request.args.get('psize', 10))

    except:
        print_exception_info()
        raise ApiError('get_wechat_withdraw error', error.ERROR_PARAM)

    user_id = current_user.id

    count, res = dbapi.get_pay_to_user(user_id=user_id,
        page=page, psize=psize)
    data = []
    if count and res:
        for pay_to_user in res:
            info = {
                'time': int(pay_to_user.ctime.timestamp()),
                'to_nickname': pay_to_user.to_nickname,
                'fee'   : pay_to_user.total_fee,
                'remark': pay_to_user.remark
            }
            data.append(info)

    reply['data'] = {
        'count': count,
        'pays': data
    }

    return make_response(jsonify(reply), status_code)


@admin_economic_blueprint.route('/top_agent/wechat_withdraw/fetch')
@login_required
@agent_id_required
def top_agent_get_wechat_withdraw():
    dbg('top_agent_get_wechat_withdraw')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        page  = int(request.args.get('page', 1))
        psize = int(request.args.get('psize', 10))
    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    agent_id = current_user.agent_id
    user_id  = current_user.id

    wechat_agent_id = get_top_wechat_agent_id(agent_id)
    if wechat_agent_id != agent_id:
        raise ApiError('ERROR_AGENT_NO_PERMISSION', error.ERROR_AGENT_NO_PERMISSION)

    agent_setting = dbapi.get_agent_setting(agent_id=wechat_agent_id)

    count, res = dbapi.get_pay_to_user(wechat_agent_id=wechat_agent_id,
        page=page, psize=psize)
    data = []
    sum_dict = {}
    if count:
        for pay_to_user in res:
            openluat_user_id = pay_to_user.openluat_user_id
            agent = dbapi.get_agent(user_id=openluat_user_id)
            if agent:
                wallet = dbapi.get_wallet(user_id=openluat_user_id, agent_id=agent_id)
                name = agent.name
                agent_id = agent.id
                if agent_id in sum_dict:
                    dbg('sum in dict')
                    total_fee_sum = sum_dict[agent_id]['total_fee_sum']
                    receipt_sum = sum_dict[agent_id]['receipt_sum']
                else:
                    total_fee_sum = dbapi.get_pay_to_user(user_id=openluat_user_id, total=True)
                    receipt_sum = dbapi.get_agent_wallet_receipt_sum(wallet.id)
                    sum_dict[agent_id] = {
                        'total_fee_sum': total_fee_sum,
                        'receipt_sum': receipt_sum
                    }
            else:
                dbg('agent not found for openluat_user_id: %s' % openluat_user_id)
                name = ''
                total_fee_sum = 0
                receipt_sum = 0

            info = {
                'time': int(pay_to_user.ctime.timestamp()),
                # 'to_nickname': pay_to_user.to_nickname,
                'payment_no': pay_to_user.payment_no,
                'name': name,
                'total_fee': pay_to_user.total_fee,
                'wechat_fee': math.ceil(pay_to_user.total_fee * agent_setting.withdraw_fee),
                'wechat_fee_rate': agent_setting.withdraw_fee,
                'fee': pay_to_user.total_fee - math.ceil(pay_to_user.total_fee * agent_setting.withdraw_fee),
                'total_fee_sum': total_fee_sum,
                'receipt_sum': receipt_sum,
                'balance': int(wallet.balance),
                'withdrawable_balance': int(wallet.withdrawable_balance),
                'status': pay_to_user.status
            }
            data.append(info)

    reply = {
        'count': count,
        'pays': data
    }

    return make_response(jsonify(reply), status_code)


@admin_economic_blueprint.route('/wallet_receipt/fetch')
@login_required
@agent_id_required
def get_wallet_receipt():
    dbg('get_wallet_receipt')
    reply ,status_code = {'code': 0, 'msg': ''}, 200

    try:
        page  = int(request.args.get('page', 1))
        psize = int(request.args.get('psize', 10))

    except:
        print_exception_info()
        raise ApiError('ERROR_PARAM', error.ERROR_PARAM)

    user_id = current_user.id

    count, wallet_receipts = dbapi.get_wallet_receipt(user_id=user_id,
        agent_id=current_user.agent_id, no_zero=1, page=page, psize=psize)

    data = []
    if count and wallet_receipts:
        for wallet_receipt in wallet_receipts:
            info = {
                'time': int(wallet_receipt.ctime.timestamp()),
                'receipt': int(wallet_receipt.receipt),
                'withdrawable_receipt'   : int(wallet_receipt.withdrawable_receipt),
                'trade_type': wallet_receipt.trade_type,
                'remark': wallet_receipt.remark
            }
            data.append(info)

    reply['data'] = {
        'count': count,
        'wallet_receipts': data
    }

    return make_response(jsonify(reply), status_code)