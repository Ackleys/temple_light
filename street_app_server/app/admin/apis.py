#!/usr/bin/env python3
# coding: utf8
# 20170220 anChaOs


import os, json, requests, string, random, traceback
from datetime import datetime

from flask import current_app

from app.tool import dbg                    # for print
from app.tool import print_exception_info   # for traceback

# error
import app.error as error
ApiError = error.ApiError

# db
from app import db

# database functions
import app.database.api as dbapi

import app.third_party.wechatpay as wechatpay


def to_dict(self):
  return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


KEY = 'mgDmXvGYvtb9JUN6IXNZZECXEwd5K4s0'


"""
    @参数说明
    device_type 0按摩椅 1娃娃机 2洗衣机
    money 单位分
    duration 单位秒
"""
def request_machine_start(imei, cat, total_fee, duration):
    dbg('request_machine_start')
    url = 'https://iot.openluat.com/api/event/payment_notification_to_device'
    headers = {'Event-Key': KEY}
    payload = {
        'imei': imei,
        'device_type': cat,
        'money': total_fee,
        'duration': duration
    }
    succ = False
    try:
        r = requests.post(url, data=payload, headers=headers)
        if r.status_code == requests.codes.ok:
            succ = True
        return succ, r.text
    except:
        # print_exception_info()
        traceback.print_exc()
        return succ, r.text


def get_top_agent(agent):
    dbg('get_top_agent')
    
    return agent


def get_agent_admin(agent):
    dbg('get_top_agent')
    top_agent = get_top_agent(agent)
    god_agent = dbapi.get_god_agent(agent_id=agent.id)
    return god_agent


def get_god_info_common(agent):
    dbg('get_god_info_common')
    God = dbapi.God
    if 'God' in str(agent):
        god    = agent
        god_id = god.id
    else:
        # 1. 先查agent_info是否存在
        agent_info = dbapi.get_agent_info(agent_id=agent.id)
        if agent_info:
            return agent_info

        # 2. 若不存在，则查god_info
        while agent.hook_agent_id != 0:
            agent = dbapi.get_agent(id=agent.hook_agent_id)
        god_agent = dbapi.get_god_agent(agent_id=agent.id)
        god = dbapi.get_god(id=god_agent.god_id)
        god_id = god.id

    god_info = dbapi.get_god_info(god_id=god_id)
    if not god_info:
        god_info = dbapi.make_new_god_info(god_id)
        dbapi.db.session.commit()

    return god_info



"""
    计算需要改动的各级提成
    @params
        level           当前要改动的代理等级
        rate            当前代理需要改为的比例
        agent_levels    该设备涉及到的全部代理的等级
        rates_all       该设备的各级代理提成
"""
def calc_device_profit(level, rate, agent_levels, rates_all):
    dbg('calc_device_profit')
    levels = ('l1', 'l2', 'l3', 'l4')       # 各级代理的key

    delta = rates_all[level-1] - rate       # 计算当前代理变动的差值

    denominator = 0
    unchange_sum = 0
    update = {}

    for i in agent_levels:
        if i < level:
            # 计算需要改动的代理的当前分成总和（不含自己）
            denominator += rates_all[i-1]
            # 记录需要改动的代理的update键值对（不含自己）
            update[levels[i-1]] = rates_all[i-1]
        elif i > level:
            # 记录不需要改动的代理的分成总和
            unchange_sum += rates_all[i-1]

    count = 1
    num = len(update)
    cur_sum = 0
    tbd_key = ''
    # 计算各个代理新的分成
    for k in update:
        # 计算除最后一个的代理的分成
        if count != num:
            update[k] = round(update[k] + update[k]*delta/denominator, 3)
            cur_sum += update[k]
        # 获取最后一个代理的key
        else:
            tbd_key = k
        count += 1

    # 用减法计算最后一个代理的分成，为了保证100%
    update[tbd_key] = round(1 - (unchange_sum+cur_sum+rate), 3)
    # 如果最后一位代理的值不在0和1之间，说明需要修改的rate错误
    if update[tbd_key] < 0 or update[tbd_key] > 1:
        raise ApiError('rate not support')

    # 当前代理的分成
    update[levels[level-1]] = rate
    return update


# def calc_device_profit(device_id):
#     dbg('calc_device_profit')
#     rates_all = [1, 0, 0, 0]

#     # 计算各个上下级的比例（从总代理算起）
#     rates_up_low = []
#     device_distributions = dbapi.get_device_distribution(device_id=device_id)
#     for dd in device_distributions:
#         if dd.from_agent != 0:
#             rates_up_low.append(dd.rate)

#     for i, rate_ul in enumerate(rates_up_low):
#         rates_all[i] = round(rates_all[i] * rate_ul, 10)
#         cur_sum = 0
#         for rate_all in rates_all:
#             cur_sum += rate_all
#         rates_all[i+1] = 1 - cur_sum

#     return rates_all


def check_joinup_available(agent_id):
    dbg('check_joinup_available')
    info = {
        'wechat': 0,
        'ali': 0
    }
    db = dbapi.db
    Pay = dbapi.Pay
    Device = dbapi.Device
    DeviceDistribution = dbapi.DeviceDistribution
    order = db.session.query(Pay).join(Device, Pay.imei==Device.imei).\
        join(DeviceDistribution, Device.id==DeviceDistribution.device_id).\
        filter(DeviceDistribution.to_agent==agent_id).\
        filter(Pay.status==1).filter(Pay.deleted!=1).first()
    if not order:
        # 没有订单，可以随便对接
        info['wechat'] = 1
        info['ali'] = 1
    else:
        # 有订单，则微信不可对接，如果微信已对接，则支付宝可以对接
        agent_wechat = dbapi.get_agent_wechat(agent_id=agent_id)
        if not agent_wechat:
            agent_wechat = dbapi.make_new_agent_wechat(agent_id)
            dbapi.db.session.commit()
        if agent_wechat.wechat_config_id != 1 or agent_id == 1:
            info['ali'] = 1

    return info


def get_joinup_status(agent_id):
    dbg('get_joinup_status')
    info = {
        'wechat': 0,
        'ali': 0
    }
    agent_wechat = dbapi.get_agent_wechat(agent_id=agent_id)
    if agent_wechat:
        min_agent_wechat = dbapi.get_agent_wechat(wechat_config_id=agent_wechat.wechat_config_id, min=True)
        if min_agent_wechat.agent_id == agent_id:
            info['wechat'] = 1

    agent_ali = dbapi.get_agent_ali(agent_id=agent_id)
    if agent_ali:
        min_agent_ali = dbapi.get_agent_ali(ali_config_id=agent_ali.ali_config_id, min=True)
        if min_agent_ali.agent_id == agent_id:
            info['ali'] = 1

    return info


def get_top_wechat_agent_id(agent_id):
    dbg('get_top_wechat_agent_id')
    agent_wechat = dbapi.get_agent_wechat(agent_id=agent_id)
    if agent_wechat:
        min_agent_wechat = dbapi.get_agent_wechat(wechat_config_id=agent_wechat.wechat_config_id, min=True)
        return min_agent_wechat.agent_id


def check_refund_available(device, total_fee):
    dbg('check_refund_available')
    imei = device.imei
    rates = (device.l1, device.l2, device.l3, device.l4)
    dds = dbapi.get_device_distribution(imei=imei)
    for dd in dds:
        agent = dbapi.get_agent(id=dd.to_agent)
        if not agent:
            dbg('can not find agent: %d' % dd.to_agent)
            return False
        wallet = dbapi.get_wallet(user_id=agent.openluat_user_id, agent_id=agent.id)
        rate = rates[agent.level-1]
        fee = total_fee * rate
        dbg((agent.id, fee, wallet.withdrawable_balance))
        if fee > wallet.withdrawable_balance:
            return False

    return True


def refund_income(total_fee, imei):
    dbg('refund_income')
    device = dbapi.get_device(imei=imei)
    if not device:
        dbg('no device: %s' % imei)
        return
    dds = dbapi.get_device_distribution(device_id=device.id)
    rates = (device.l4, device.l3, device.l2, device.l1)
    for i, dd in enumerate(dds):
        if i == len(dds)-1 and device.salesman_agent_id != 0:
            # 包含业务员
            salesman_rates = (device.sl1, device.sl2, device.sl3)
            all_fee = total_fee * rates[i]
            fee_sum = 0
            ddss = dbapi.get_device_distribution_salesman(device_id=device.id)
            for iterm in ddss:
                 # 级业务员提成
                cur_agent = dbapi.get_agent(id=iterm.to_agent)
                if cur_agent:
                    salseman_remark = '业务员退款扣除提成slevel: %d' % cur_agent.slevel
                    fee = all_fee * salesman_rates[cur_agent.slevel-1]
                    receipt = -fee
                    make_refund_ticheng_wallet_receipt(cur_agent, receipt, salseman_remark)
                    fee_sum += fee

            # 退款扣除各所属代理商
            agent = dbapi.get_agent(id=dd.to_agent)
            if not agent:
                dbg('no agent: %d' % dd.to_agent)
                continue
            remark = '退款扣除提成'
            receipt = -(all_fee-fee_sum)
            make_refund_ticheng_wallet_receipt(agent, receipt, remark)

        else:
            # 不包含业务员
            agent = dbapi.get_agent(id=dd.to_agent)
            if not agent:
                dbg('no agent: %d' % dd.to_agent)
                continue
            receipt = -total_fee * rates[4-agent.level]
            remark = '退款扣除提成'
            make_refund_ticheng_wallet_receipt(agent, receipt, remark)


def make_refund_ticheng_wallet_receipt(agent, receipt, remark):
    dbg('make_refund_ticheng_wallet_receipt')
    user_id = agent.openluat_user_id
    agent_id = agent.id
    wallet = dbapi.get_wallet(user_id=user_id, agent_id=agent_id)
    wallet_id = wallet.id
    trade_type = dbapi.WALLET_TRADE_TYPE_REFUND_TICHENG
    withdrawable_balance = wallet.withdrawable_balance
    if wallet.withdrawable_balance > wallet.balance + receipt:
        withdrawable_balance = withdrawable_balance + receipt
        withdrawable_receipt = receipt
    else:
        withdrawable_receipt = 0
    wallet_receipt = dbapi.make_new_wallet_receipt(user_id, agent_id, wallet_id,
                                                   trade_type, receipt,
                                                   withdrawable_receipt, remark)
    dbg(wallet_receipt)
    balance = wallet.balance + receipt
    wallet = dbapi.update_wallet(wallet, balance=balance, withdrawable_balance=withdrawable_balance)
    dbg('update wallet: %d\treceipt: %f' % (wallet.id, receipt))
    db.session.add(wallet)


def get_online_income(online_income):
    if online_income:
        online_income = int(online_income)
    else:
        online_income = 0
    return online_income


def get_offline_coin_and_offline_income(offline_coin, product_min_money):
    if offline_coin:
        offline_coin = int(offline_coin)
    else:
        offline_coin = 0
    offline_income = offline_coin * product_min_money
    return offline_coin, offline_income


def gen_coupon_order_no(user_id, pay_mode):
    max_id  = dbapi.get_max_pay_id()
    str_max_id = '%04d' % max_id
    if len(str_max_id) > 4:
        str_max_id = str_max_id[-4:]
    trade_no = str(pay_mode) + str(dbapi.PRODUCT_CAT_COUPON) + datetime.now().strftime("%Y%m%d%H%M%S") + str_max_id
    return trade_no


def wechat_qrcode_make_new_pay(product, trade_no, user_id, imei=''):
    params = {
        'product_id': str(product.id),
        'body': product.title,
        'out_trade_no': trade_no,
        'total_fee': product.price,
        'spbill_create_ip': current_app.config['SELF_IP'],
        'notify_url': current_app.config['NOTIFY_URL'],
        'trade_type': 'NATIVE',
        'agent_id': product.agent_id
    }
    err, payRequest = wechatpay.get_native_pay_request(**params)
    dbg((err, payRequest))
    if not err:
        prepay_id = payRequest["prepay_id"]
        qrcode    = payRequest['code_url']
        body = ''
        pay = dbapi.make_new_pay(user_id, product.agent_id, imei, trade_no,
            product.id, product.title, body, product.cat, product.price, 
            prepay_id=prepay_id, qrcode=qrcode)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
        data = {
            'pay_request': payRequest,
            'trade_no'   : trade_no,
            'id'         : pay.id
        }
        return data
    else:
        return err


def wechat_qrcode_update(pay, product, trade_no, user_id, imei=''):
    params = {
        'product_id': str(product.id),
        'body': product.title,
        'out_trade_no': trade_no,
        'total_fee': product.price,
        'spbill_create_ip': current_app.config['SELF_IP'],
        'notify_url': current_app.config['NOTIFY_URL'],
        'trade_type': 'NATIVE',
        'agent_id': product.agent_id
    }
    err, payRequest = wechatpay.get_native_pay_request(**params)
    dbg((err, payRequest))
    if not err:
        prepay_id = payRequest["prepay_id"]
        qrcode    = payRequest['code_url']
        pay = dbapi.update_pay(pay, prepay_id=prepay_id, qrcode=qrcode)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
        return pay
    else:
        return pay


def get_coupon_img(advertiser_id, im, postfix):
    imag_filename = 'coupon_%d_%d.%s' % (advertiser_id, datetime.now().timestamp(), postfix)
    imag_filepath = os.path.join('app/static/img/coupon', imag_filename)
    coupon_img    = os.path.join('img/coupon', imag_filename)
    if not os.path.exists('app/static/img/coupon'):
        os.mkdir('app/static/img/coupon')
    dbg("save imag: %s" % imag_filepath)
    size = (300, 600)
    im = im.resize(size)
    im.save(imag_filepath)
    return coupon_img


def gen_coupon_prefix(text):
    sum_count = 0
    for b in text.encode('utf8'):
        sum_count += b
    prefix = hex(sum_count)[2:].upper()
    coupon = dbapi.get_coupon(prefix=prefix)
    max_loop = 10
    count = 0
    while coupon:
        if count == max_loop:
            return False
        sum_count += 1
        prefix = hex(sum_count)[2:].upper()
        coupon = dbapi.get_coupon(prefix=prefix)
        count += 1
    return prefix


if __name__ == '__main__':
    succ, res = request_machine_start('862991419827909', 0, 1, 6)
    if succ:
        print('ok')
    else:
        try:
            data = json.loads(res)
            print(data)
        except:
            traceback.print_exc()
            print('unkown')
