#!/usr/bin/env python3
# coding: utf8
# 20170220 anChaOs


import json
import time
import requests
import string
import random
import traceback

from datetime import datetime

# Pillow
from PIL import Image

from flask import session, current_app

import app.tool as tool
from app.tool import dbg                    # for print
from app.tool import print_exception_info   # for traceback

# error
import app.error as error
ApiError = error.ApiError

# db
from app import db

# config
import config as config

# database functions
import app.database.api as dbapi

import app.third_party.wechatpay as wechatpay


def to_dict(self):
    return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


def check_alipay_available(imei):
    dbg('check_alipay_available')
    device = dbapi.get_device(imei=imei)
    if not device:
        dbg('no device')
        return False
    agent_id = device.agent_id
    if agent_id == 1:
        dbg('hezhou device')
        return True
    else:
        agent_wechat = dbapi.get_agent_wechat(agent_id=agent_id)
        if not agent_wechat:
            dbg('no agent_wechat')
            return False
        elif agent_wechat.wechat_config_id == 1:
            dbg('wechat config id: %d' % agent_wechat.wechat_config_id)
            return True
        else:
            agent_ali = dbapi.get_agent_ali(agent_id=agent_id)
            if not agent_ali:
                dbg('no agent ali')
                return False
            elif agent_ali.ali_config_id == 1:
                dbg('%d: alipay not allowed' % agent_ali.ali_config_id)
                return False
            else:
                dbg('%d: alipay allowed'% agent_ali.ali_config_id)
                return True




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


"""
    @参数说明
    duration 单位秒
"""


def launch_relay_signal_deivce_v2(imei, duration, device_type=0, high=500, low=4294967295):
    dbg((imei, duration, device_type))
    imei = imei
    duration = duration
    pulse = 1
    money = pulse
    device_type = device_type
    high = 500
    low = 4294967295   # 'ffffffff'

    mongodata = {
        'imei': imei,
        'datagram_type': 1,
        'device_type': device_type,
        'duration': duration,
        'high': high,
        'low': low,
        'pulse': pulse
    }

    data = bytearray([0x54, device_type])

    data += money.to_bytes(4, 'big')
    data += duration.to_bytes(4, 'big')
    data += high.to_bytes(4, 'big')
    data += low.to_bytes(4, 'big')
    data += pulse.to_bytes(4, 'big')

    dbg(data)
    try:
        result = tool.send_data_to_device(
            'deveventreq', imei, data, need_to_wait=True)
        if result and result['result']:
            mongodata['result'] = 0     # 成功
            dbapi.insert_datagram(mongodata)
            return True, json.dumps({'code': 0, 'msg': ''})
        else:
            mongodata['result'] = 1     # 设备正在运行
            dbapi.insert_datagram(mongodata)
            return False, json.dumps({'code': 8002, 'msg': '设备正在运行'})
    except error.ApiError as e:
        if e.error_no == 8001:
            mongodata['result'] = 2     # 设备连接超时
            dbapi.insert_datagram(mongodata)
            return False, json.dumps({'code': 8001, 'msg': '设备连接超时'})
        else:
            mongodata['result'] = 3     # server error
            dbapi.insert_datagram(mongodata)
            return False, json.dumps({'code': 99, 'msg': 'server error'})
    except:
        mongodata['result'] = 3     # server error
        dbapi.insert_datagram(mongodata)
        return False, json.dumps({'code': 99, 'msg': 'server error'})


def launch_pulse_signal_deivce(imei, pulse, high=50, low=50):
    dbg((imei, pulse, high, low))
    imei = imei
    pulse = pulse
    money = pulse
    device_type = 1
    duration = 5
    high = high
    low  = low

    mongodata = {
        'imei': imei,
        'datagram_type': 1,
        'device_type': device_type,
        'duration': duration,
        'high': high,
        'low': low,
        'pulse': pulse
    }

    data = bytearray([0x54, device_type])

    data += money.to_bytes(4, 'big')
    data += duration.to_bytes(4, 'big')
    data += high.to_bytes(4, 'big')
    data += low.to_bytes(4, 'big')
    data += pulse.to_bytes(4, 'big')

    dbg(data)
    try:
        result = tool.send_data_to_device(
            'deveventreq', imei, data, need_to_wait=True)
        if result and result['result']:
            mongodata['result'] = 0     # 成功
            dbapi.insert_datagram(mongodata)
            return True, json.dumps({'code': 0, 'msg': ''})
        else:
            mongodata['result'] = 1     # 设备正在运行
            dbapi.insert_datagram(mongodata)
            return False, json.dumps({'code': 8002, 'msg': '设备正在运行'})
    except error.ApiError as e:
        if e.error_no == 8001:
            mongodata['result'] = 2     # 设备连接超时
            dbapi.insert_datagram(mongodata)
            return False, json.dumps({'code': 8001, 'msg': '设备连接超时'})
        else:
            mongodata['result'] = 3     # server error
            dbapi.insert_datagram(mongodata)
            return False, json.dumps({'code': 99, 'msg': 'server error'})
    except:
        mongodata['result'] = 3     # server error
        dbapi.insert_datagram(mongodata)
        return False, json.dumps({'code': 99, 'msg': 'server error'})


def salesman_ticheng(device, agent, all_fee, remarks, cat):
    dbg('salesman_ticheng')

    rates = (device.sl1, device.sl2, device.sl3)

    ddss = dbapi.get_device_distribution_salesman(device_id=device.id)
    fee_sum = 0
    for dds in ddss:
        # 各级业务员提成
        cur_agent = dbapi.get_agent(id=dds.to_agent)
        if cur_agent:
            salseman_remarks = '业务员提成slevel: %d' % cur_agent.slevel
            fee     = all_fee * rates[cur_agent.slevel-1]
            make_receipt(cur_agent, fee, salseman_remarks, cat)
            fee_sum += fee

    # 所属代理商提成
    dbg('all_fee: %f' % all_fee)
    dbg('fee_sum: %f' % fee_sum)
    fee = (all_fee-fee_sum)
    make_receipt(agent, fee, remarks, cat)


def wechat_pay_receipt(pay):
    dbg('wechat_pay_receipt')
    device = dbapi.get_device(imei=pay.imei)
    if not device:
        dbg('no device: %s' % pay.imei)
        return

    device_distributions = dbapi.get_device_distribution(device_id=device.id)
    flows = []
    for device_distribution in device_distributions:
        cur_agent = dbapi.get_agent(id=device_distribution.to_agent)
        if cur_agent:
            flows.append(cur_agent)

    remarks = (('总代理收入', '总代理提成'), ('一级代理收入', '一级代理提成'),
               ('二级代理收入', '二级代理提成'), ('经销商收入',))

    agent_count = len(flows)
    if agent_count == 1:    # 总代理直接经营
        if device.salesman_agent_id == 0:
            dbg(remarks[0][0])
            owner_fee = pay.total_fee * device.l4
            make_receipt(flows[0], owner_fee, remarks[0][0], pay.cat)
        else:
            owner_fee = pay.total_fee * device.l4
            salesman_ticheng(device, flows[0], owner_fee, remarks[0][0], pay.cat)

    if agent_count == 2:    # 一级代理提成（省级代理）直接经营
        # 1. 总代理提成
        dbg(remarks[0][1])
        l4_fee = pay.total_fee * device.l4
        make_receipt(flows[0], l4_fee, remarks[0][1], pay.cat)

        if device.salesman_agent_id == 0:
            # 2. 一级代理收入
            dbg(remarks[1][0])
            owner_fee = pay.total_fee - l4_fee
            make_receipt(flows[1], owner_fee, remarks[1][0], pay.cat)
        else:
            owner_fee = pay.total_fee - l4_fee
            salesman_ticheng(device, flows[1], owner_fee, remarks[1][0], pay.cat)

    if agent_count == 3:    # 二级代理提成（省级代理）直接经营
        # 1. 总代理提成
        dbg(remarks[0][1])
        l4_fee = pay.total_fee * device.l4
        make_receipt(flows[0], l4_fee, remarks[0][1], pay.cat)

        # 2. 一级代理提成
        dbg(remarks[1][1])
        l3_fee = pay.total_fee * device.l3
        make_receipt(flows[1], l3_fee, remarks[1][1], pay.cat)

        if device.salesman_agent_id == 0:
            # 3. 二级代理收入
            dbg(remarks[2][0])
            owner_fee = pay.total_fee - l4_fee - l3_fee
            make_receipt(flows[2], owner_fee, remarks[2][0], pay.cat)
        else:
            owner_fee = pay.total_fee - l4_fee - l3_fee
            salesman_ticheng(device, flows[2], owner_fee, remarks[2][0], pay.cat)

    if agent_count == 4:    # 二级代理提成（省级代理）直接经营
        # 1. 总代理提成
        dbg(remarks[0][1])
        l4_fee = pay.total_fee * device.l4
        make_receipt(flows[0], l4_fee, remarks[0][1], pay.cat)

        # 2. 一级代理提成
        dbg(remarks[1][1])
        l3_fee = pay.total_fee * device.l3
        make_receipt(flows[1], l3_fee, remarks[1][1], pay.cat)

        # 3. 二级代理提成
        dbg(remarks[2][1])
        l2_fee = pay.total_fee * device.l2
        make_receipt(flows[2], l2_fee, remarks[2][1], pay.cat)
        
        if device.salesman_agent_id == 0:
            # 4. 经销商收入
            dbg(remarks[3][0])
            owner_fee = pay.total_fee - l4_fee - l3_fee - l2_fee
            make_receipt(flows[3], owner_fee, remarks[3][0], pay.cat)
        else:
            owner_fee = pay.total_fee - l4_fee - l3_fee - l2_fee
            salesman_ticheng(device, flows[3], owner_fee, remarks[3][0], pay.cat)


def make_receipt(agent, fee, remark, cat):
    dbg('make_receipt: %.2f' % fee)
    user_id = agent.openluat_user_id
    agent_id = agent.id
    withdrawable_receipt = fee
    # 如果是钱包充值，切代理设置中，充值不可取现
    if cat == 99 and not agent.withdrawable:
        withdrawable_receipt = 0
    wallet = dbapi.get_wallet(user_id=user_id, agent_id=agent_id)
    wallet_id = wallet.id
    trade_type = dbapi.WALLET_TRADE_TYPE_TICHENG
    receipt = fee
    wallet_receipt = dbapi.make_new_wallet_receipt(user_id, agent_id, wallet_id,
                                                   trade_type, receipt, withdrawable_receipt,
                                                   remark)

    balance = wallet.balance + fee
    withdrawable_balance = wallet.withdrawable_balance + withdrawable_receipt
    if withdrawable_balance > balance:
        withdrawable_balance = balance
    wallet = dbapi.update_wallet(wallet, balance=balance, withdrawable_balance=withdrawable_balance)
    db.session.add(wallet)



def wechat_make_new_pay(product, trade_no, agent_id, user_id, imei, trade_type):
    params = {
        'body': product.title,
        'out_trade_no': trade_no,
        'total_fee': product.price,
        'spbill_create_ip': current_app.config['SELF_IP'],
        'notify_url': current_app.config['NOTIFY_URL'],
        'openid': session['openid'],
        'trade_type': trade_type,
        'agent_id': agent_id
    }
    err, payRequest = wechatpay.get_jsapi_pay_request(**params)
    dbg((err, payRequest))
    if not err:
        prepay_id = payRequest["package"].split("=")[1]
        body = ''
        if product.cat == 0:
            record = dbapi.get_record(imei=imei, recent=1)
            if record and record.status == 0 and record.etime > datetime.now():
                raise ApiError('ERROR_PAY_TOO_FREQUENCE', error.ERROR_PAY_TOO_FREQUENCE)

            # last_pay = dbapi.get_last_pay(imei)
            # if last_pay:
            #     last_product = dbapi.get_product(product_id=last_pay.product_id)
            #     if last_product and datetime.now().timestamp() - last_pay.ctime.timestamp() <= last_product.value:
            #         raise ApiError('ERROR_PAY_TOO_FREQUENCE', error.ERROR_PAY_TOO_FREQUENCE)
        pay = dbapi.make_new_pay(user_id, product.agent_id, imei, trade_no,
            product.id, product.title, body, product.cat, product.price, 
            prepay_id=prepay_id)
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


def ali_make_new_pay(product, trade_no, agent_id, user_id, imei, return_url=config.MaFuAli.RETURN_URL):
    if product.cat == 0:
        record = dbapi.get_record(imei=imei, recent=1)
        if record and record.status == 0 and record.etime > datetime.now():
            raise ApiError('ERROR_PAY_TOO_FREQUENCE', error.ERROR_PAY_TOO_FREQUENCE)

        # last_pay = dbapi.get_last_pay(imei)
        # if last_pay:
        #     last_product = dbapi.get_product(product_id=last_pay.product_id)
        #     if last_product and datetime.now().timestamp() - last_pay.ctime.timestamp() <= last_product.value:
        #         raise ApiError('ERROR_PAY_TOO_FREQUENCE', error.ERROR_PAY_TOO_FREQUENCE)
    pay = dbapi.make_new_pay(user_id, product.agent_id, imei, trade_no,
        product.id, product.title, product.body, product.cat, product.price, 
        pay_mode=2)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise

    ali_config = dbapi.get_ali_config(agent_id=int(agent_id))
    appid      = ali_config.appid
    key_path   = ali_config.priv_path

    biz_content = {
        'body': product.body,
        'subject': product.title,
        'out_trade_no': trade_no,
        'total_amount': '%.2f' % (product.price/100),
        'product_code': 'QUICK_WAP_WAY',
    }
    data = {
        'app_id': appid,
        'method': 'alipay.trade.wap.pay',
        'return_url': return_url,
        'charset': 'utf-8',
        'sign_type': 'RSA2',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'version': '1.0',
        'notify_url': config.MaFuAli.NOTIFY_URL,
        'biz_content': json.dumps(biz_content),
    }
    _tmp = "&".join(['%s=%s' % (k, data[k]) for k in sorted(data)])
    try:
        sign = gen_sign256(key_path, _tmp)
    except:
        sign = tool.gen_sign(key_path, _tmp)
    data['sign'] = sign

    res = {
        'pay_request': data,
        'trade_no'   : trade_no,
        'id'         : pay.id
    }

    return res


def wallet_make_new_pay(product, trade_no, agent_id, user_id, imei):
    dbg('wallet_make_new_pay')
    wallet = dbapi.get_wallet(role=0, user_id=user_id, agent_id=agent_id)
    if product.price > wallet.balance:
        raise ApiError('ERROR_BALANCE_NOT_ENOUGH', error.ERROR_BALANCE_NOT_ENOUGH)

    if product.cat == 0:
        record = dbapi.get_record(imei=imei, recent=1)
        if record and record.status == 0 and record.etime > datetime.now():
            raise ApiError('ERROR_PAY_TOO_FREQUENCE', error.ERROR_PAY_TOO_FREQUENCE)

        # last_pay = dbapi.get_last_pay(imei)
        # if last_pay:
        #     last_product = dbapi.get_product(product_id=last_pay.product_id)
        #     if last_product and datetime.now().timestamp() - last_pay.ctime.timestamp() <= last_product.value:
        #         raise ApiError('ERROR_PAY_TOO_FREQUENCE', error.ERROR_PAY_TOO_FREQUENCE)
    pay = dbapi.make_new_pay(user_id, product.agent_id, imei, trade_no,
        product.id, product.title, product.body, product.cat, product.price, 
        pay_mode=3)
    pay.status = 1
    db.session.add(pay)
    
    wallet_id = wallet.id
    trade_type = dbapi.WALLET_TRADE_TYPE_EXPENDITURE
    receipt = -product.price
    remark = product.title
    withdrawable_receipt = 0
    wallet_receipt = dbapi.make_new_wallet_receipt(user_id, agent_id, wallet_id,
                                                   trade_type, receipt,
                                                   withdrawable_receipt, remark)

    balance = wallet.balance + receipt
    wallet = dbapi.update_wallet(wallet, balance=balance)

    # 更新可提现钱包
    wallet_pay_withdrawable_receipt(pay)

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise

    res = {
        'trade_no'   : trade_no,
        'id'         : pay.id,
        'pay_request': ''
    }

    return res


def wallet_pay_withdrawable_receipt(pay):
    dbg('wallet_pay_withdrawable_receipt')
    device = dbapi.get_device(imei=pay.imei)
    if not device:
        dbg('no device: %s' % pay.imei)
        return

    device_distributions = dbapi.get_device_distribution(device_id=device.id)
    flows = []
    for device_distribution in device_distributions:
        cur_agent = dbapi.get_agent(id=device_distribution.to_agent)
        if cur_agent:
            flows.append(cur_agent)

    remarks = (('总代理收入', '总代理提成'), ('一级代理收入', '一级代理提成'),
               ('二级代理收入', '二级代理提成'), ('经销商收入',))

    agent_count = len(flows)
    if agent_count == 1:    # 总代理直接经营
        if device.salesman_agent_id == 0:
            dbg(remarks[0][0])
            owner_fee = pay.total_fee * device.l4
            make_wallet_withdrawable_receipt(flows[0], owner_fee, remarks[0][0])
        else:
            owner_fee = pay.total_fee * device.l4
            salesman_ticheng_withdrawable(device, flows[0], owner_fee, remarks[0][0])

    if agent_count == 2:    # 一级代理提成（省级代理）直接经营
        # 1. 总代理提成
        dbg(remarks[0][1])
        l4_fee = pay.total_fee * device.l4
        make_wallet_withdrawable_receipt(flows[0], l4_fee, remarks[0][1])

        # 2. 一级代理收入
        if device.salesman_agent_id == 0:
            dbg(remarks[1][0])
            owner_fee = pay.total_fee - l4_fee
            make_wallet_withdrawable_receipt(flows[1], owner_fee, remarks[1][0])
        else:
            owner_fee = pay.total_fee - l4_fee
            salesman_ticheng_withdrawable(device, flows[1], owner_fee, remarks[1][0])

    if agent_count == 3:    # 二级代理提成（省级代理）直接经营
        # 1. 总代理提成
        dbg(remarks[0][1])
        l4_fee = pay.total_fee * device.l4
        make_wallet_withdrawable_receipt(flows[0], l4_fee, remarks[0][1])

        # 2. 一级代理提成
        dbg(remarks[1][1])
        l3_fee = pay.total_fee * device.l3
        make_wallet_withdrawable_receipt(flows[1], l3_fee, remarks[1][1])

        # 3. 二级代理收入
        if device.salesman_agent_id == 0:
            dbg(remarks[2][0])
            owner_fee = pay.total_fee - l4_fee - l3_fee
            make_wallet_withdrawable_receipt(flows[2], owner_fee, remarks[2][0])
        else:
            owner_fee = pay.total_fee - l4_fee - l3_fee
            salesman_ticheng_withdrawable(device, flows[2], owner_fee, remarks[2][0])

    if agent_count == 4:    # 二级代理提成（省级代理）直接经营
        # 1. 总代理提成
        dbg(remarks[0][1])
        l4_fee = pay.total_fee * device.l4
        make_wallet_withdrawable_receipt(flows[0], l4_fee, remarks[0][1])

        # 2. 一级代理提成
        dbg(remarks[1][1])
        l3_fee = pay.total_fee * device.l3
        make_wallet_withdrawable_receipt(flows[1], l3_fee, remarks[1][1])

        # 3. 二级代理提成
        dbg(remarks[2][1])
        l2_fee = pay.total_fee * device.l2
        make_wallet_withdrawable_receipt(flows[2], l2_fee, remarks[2][1])
        
        # 4. 经销商收入
        if device.salesman_agent_id == 0:
            dbg(remarks[3][0])
            owner_fee = pay.total_fee - l4_fee - l3_fee - l2_fee
            make_wallet_withdrawable_receipt(flows[3], owner_fee, remarks[3][0])
        else:
            owner_fee = pay.total_fee - l4_fee - l3_fee - l2_fee
            salesman_ticheng_withdrawable(device, flows[3], owner_fee, remarks[3][0])


def make_wallet_withdrawable_receipt(agent, fee, remark):
    dbg('make_wallet_withdrawable_receipt: %.2f' % fee)
    user_id = agent.openluat_user_id
    agent_id = agent.id
    wallet = dbapi.get_wallet(user_id=user_id, agent_id=agent_id)
    if wallet.balance == wallet.withdrawable_balance:
        return
    wallet_id = wallet.id
    trade_type = dbapi.WALLET_TRADE_TYPE_TICHENG
    receipt = 0
    withdrawable_receipt = fee
    wallet_receipt = dbapi.make_new_wallet_receipt(user_id, agent_id, wallet_id,
                                                   trade_type, receipt, withdrawable_receipt,
                                                   remark)

    withdrawable_balance = wallet.withdrawable_balance + withdrawable_receipt
    if withdrawable_balance > wallet.balance:
        withdrawable_balance = wallet.balance
    wallet = dbapi.update_wallet(wallet, withdrawable_balance=withdrawable_balance)
    db.session.add(wallet)


def salesman_ticheng_withdrawable(device, agent, all_fee, remarks):
    dbg('salesman_ticheng_withdrawable')

    rates = (device.sl1, device.sl2, device.sl3)

    ddss = dbapi.get_device_distribution_salesman(device_id=device.id)
    fee_sum = 0
    for dds in ddss:
        # 各级业务员提成
        cur_agent = dbapi.get_agent(id=dds.to_agent)
        if cur_agent:
            salseman_remarks = '业务员提成slevel: %d' % cur_agent.slevel
            fee     = all_fee * rates[cur_agent.slevel-1]
            make_wallet_withdrawable_receipt(cur_agent, fee, salseman_remarks)
            fee_sum += fee

    # 所属代理商提成
    dbg('all_fee: %f' % all_fee)
    dbg('fee_sum: %f' % fee_sum)
    fee = (all_fee-fee_sum)
    make_wallet_withdrawable_receipt(agent, fee, remarks)


def pay_refund(pay, product):
    dbg('pay_refund')
    imei = pay.imei
    wechat_config = dbapi.get_wechat_config(agent_id=product.agent_id)
    appid = wechat_config.appid
    mchid = wechat_config.mchid

    from app.admin.apis import refund_income

    max_id  = dbapi.get_max_refund_id()
    str_max_id = '%04d' % max_id
    if len(str_max_id) > 4:
        str_max_id = str_max_id[-4:]
    refund_no = 'R' + str(int(time.time())) + str_max_id
    if pay.pay_mode == 1:
        refund = wechat_refund(pay, refund_no, appid, mchid, product)
        if refund.status==1:
            refund_income(pay.total_fee, imei)
        else:
            raise ApiError('ERROR_REFUND', error.ERROR_REFUND)
    elif pay.pay_mode == 2:
        refund = ali_refund(pay, refund_no, product)
        if refund.status==1:
            refund_income(pay.total_fee, imei)
        else:
            raise ApiError('ERROR_REFUND', error.ERROR_REFUND)
    elif pay.pay_mode == 3:
        wallet_refund(pay, refund_no, product)


def wechat_refund(pay, refund_no, appid, mchid, product):
    dbg('wechat_refund')
    refund = dbapi.make_new_refund(pay.user_id, pay.id, refund_no, 
        pay.total_fee, pay.total_fee)
    db.session.commit()
    if refund.id:
        kwargs = {
            'appid': appid,
            'mchid': mchid,
            'trade_no': pay.trade_no,
            'refund_no': refund_no,
            'total_fee': pay.total_fee,
            'refund_fee': pay.total_fee,
            'agent_id': product.agent_id
        }
        err, res = wechatpay.refund_request(**kwargs)
        if not err:
            dbg(res)
            refund = dbapi.update_refund(refund, nofity_res=res, status=1)
            pay    = dbapi.update_pay(pay, status=3)
        else:
            dbg(err)
            refund = dbapi.update_refund(refund, nofity_res=err, status=2)
        db.session.commit()
    return refund


def ali_refund(pay, refund_no, product):
    dbg('ali_refund')
    refund = dbapi.make_new_refund(pay.user_id, pay.id, refund_no, 
        pay.total_fee, pay.total_fee)
    db.session.commit()
    if refund.id:

        ali_config = dbapi.get_ali_config(agent_id=int(pay.agent_id))
        appid      = ali_config.appid
        key_path   = ali_config.priv_path

        biz_content = {
        'out_trade_no': pay.trade_no,
        'refund_amount': '%.2f' % (product.price/100)
        }
        data = {
            'app_id': appid,
            'method': 'alipay.trade.refund',
            'return_url': 'http://wxapp.mafu.shop/pay',
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'biz_content': json.dumps(biz_content),
        }
        _tmp = "&".join(['%s=%s' % (k, data[k]) for k in sorted(data)])
        try:
            sign = gen_sign256(key_path, _tmp)
        except:
            sign = tool.gen_sign(key_path, _tmp)
        data['sign'] = sign
        r = requests.get('https://openapi.alipay.com/gateway.do', params=data)
        if r.status_code == requests.codes.ok:
            try:
                data = json.loads(r.text)
                dbg(data)
                res = data['alipay_trade_refund_response']
                if res['code'] == '10000' and res['fund_change'] == 'Y':
                    refund = dbapi.update_refund(refund, nofity_res=str(res), status=1)
                    pay    = dbapi.update_pay(pay, status=3)
                else:
                    refund = dbapi.update_refund(refund, nofity_res=str(res), status=2)
            except:
                refund = dbapi.update_refund(refund, nofity_res=r.text, status=2)
        else:
            refund = dbapi.update_refund(refund, nofity_res=r.text, status=2)
        db.session.commit()
    return refund


def wallet_refund(pay, refund_no, product):
    dbg('wallet_refund')

    user_id = pay.user_id
    wallet = dbapi.get_wallet(role=0, user_id=user_id, agent_id=pay.agent_id)

    refund_status = 1
    refund = dbapi.make_new_refund(user_id, pay.id, refund_no, 
        pay.total_fee, pay.total_fee, refund_status)
    pay    = dbapi.update_pay(pay, status=3)

    wallet_id = wallet.id
    trade_type = dbapi.WALLET_TRADE_TYPE_REFUND
    receipt = product.price
    withdrawable_receipt = 0
    remark = product.title + ' --- 退款'
    wallet_receipt = dbapi.make_new_wallet_receipt(user_id, pay.agent_id, wallet_id,
                                                   trade_type, receipt,
                                                   withdrawable_receipt, remark)

    balance = wallet.balance + receipt
    wallet = dbapi.update_wallet(wallet, balance=balance)

    db.session.commit()
    return refund


def gen_sign256(prive_path, data):
    from Crypto.PublicKey import RSA
    from Crypto.Hash import SHA256
    from Crypto.Signature import PKCS1_v1_5
    from base64 import decodebytes, encodebytes

    with open(prive_path) as f:
        key = RSA.importKey(f.read())
        signer = PKCS1_v1_5.new(key)
        sign = signer.sign(SHA256.new(data.encode("utf8")))
        signature = encodebytes(sign).decode("utf8").replace("\n", "")
        return signature


def check_sign256(pub_path, data, sign):
    from Crypto.PublicKey import RSA
    from Crypto.Hash import SHA256
    from Crypto.Signature import PKCS1_v1_5
    from base64 import decodebytes, encodebytes

    with open(pub_path) as f:
        key = RSA.importKey(f.read())
        verifier = PKCS1_v1_5.new(key)
        is_verify = verifier.verify(SHA256.new(data.encode("utf8")), 
            decodebytes(sign.replace("\n", "").encode("utf8")))
        return is_verify


def gen_sign(prive_path, data):
    from Crypto.PublicKey import RSA
    from Crypto.Hash import SHA
    from Crypto.Signature import PKCS1_v1_5
    from base64 import decodebytes, encodebytes

    with open(prive_path) as f:
        key = RSA.importKey(f.read())
        signer = PKCS1_v1_5.new(key)
        sign = signer.sign(SHA.new(data.encode("utf8")))
        signature = encodebytes(sign).decode("utf8").replace("\n", "")
        return signature


def gen_coupon_receipt_code(coupon_id, prefix):
    code = prefix + ''.join(random.choice(string.digits) for _ in range(7))
    coupon_receipt = dbapi.get_coupon_receipt(code=code)
    count = 0
    max_count = 5
    while coupon_receipt:
        if count == max_count:
            dbg('can not gen code')
            return None
        code = prefix + ''.join(random.choice(string.digits) for _ in range(7))
        coupon_receipt = dbapi.get_coupon_receipt(code=code)
        count += 1

    return code


def get_boxed_reverse_color(im_file):
    im_file = 'app/static/' + im_file
    im = Image.open(im_file)
    box = (200, 580, 300, 600)
    region = im.crop(box)
    colors = region.getcolors(maxcolors=2000)
    points, rs, gs, bs = 0, 0, 0, 0
    for num, color in colors:
        if len(color) == 3:
            r, g, b = color
        if len(color) == 4:
            r, g, b, a = color
        points += num
        rs += r
        gs += g
        bs += b
    re_r = 255 - int(rs/points)
    re_g = 255 - int(gs/points)
    re_b = 255 - int(bs/points)

    return [re_r, re_g, re_b]


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
