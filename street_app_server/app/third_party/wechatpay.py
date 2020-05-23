#!/usr/bin/env python3
# coding: utf8
# 20170425 anChaOs

import json, time, string, hashlib, random, os
import xml.dom.minidom

import requests

from app.tool import dbg                    # for print
from app.tool import print_exception_info   # for traceback

# import ..tool.xmltodict as xmltodict
from app.tool import xmltodict

import config as config

# database functions
import app.database.api as dbapi


def nonce_str_gen():
    # nonce = list(string.digits + string.ascii_uppercase)
    # random.shuffle(nonce)
    # return ''.join(nonce[:16])
    return ''.join(random.choice(string.digits+string.ascii_uppercase) for _ in range(16))


def params_sign(dict_data, key):
    _tmp = "&".join(['%s=%s' % (k, dict_data[k]) for k in sorted(dict_data)])
    _sign_tmp = "%s&key=%s" %(_tmp, key)
    m = hashlib.md5()
    m.update(_sign_tmp.encode("utf8"))
    return m.hexdigest().upper()


def dict_to_xml(dict_data):
    impl = xml.dom.minidom.getDOMImplementation()
    dom = impl.createDocument(None, 'root', None)
    root = dom.createElement('xml')
    for k, v in dict_data.items():
        item = dom.createElement(k)
        text = dom.createTextNode(str(v))
        item.appendChild(text)
        root.appendChild(item)
    return root.toprettyxml()


def xml_to_dict(xml_string):
    try:
        xml_dict = dict(xmltodict.parse(xml_string, process_namespaces=True))
    except:
        print_exception_info()
        xml_dict = {}

    if "xml" not in xml_dict:
        xml_dict = {}
    else:
        xml_dict = xml_dict["xml"]

    return dict(xml_dict)


def get_unifiedorder(body="", device_info="WEB",
    out_trade_no=None, total_fee=1,
    spbill_create_ip='127.0.0.1',
    notify_url='', trade_type="",
    product_id=None, openid=None, attach="", agent_id="1", 
    **kwargs):
    """
        @统一下单:
            https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_1
    """
    assert type(total_fee) in (int, float)
    assert(trade_type in ("APP", "NATIVE", "JSAPI"))

    wechat_config = dbapi.get_wechat_config(agent_id=int(agent_id))
    appid = wechat_config.appid
    mchid = wechat_config.mchid

    url    = "https://api.mch.weixin.qq.com/pay/unifiedorder"
    params = {
        "appid" : appid,
        "mch_id": mchid,
        "device_info": device_info,
        "nonce_str": nonce_str_gen(),
        "body": body,
        "out_trade_no": out_trade_no,
        "total_fee": str(int(total_fee)), # 单位: 分 
        "spbill_create_ip": spbill_create_ip,
        "time_start": time.strftime(r"%Y%m%d%H%M%S"),
        "notify_url": notify_url, # 异步支付状态通知
        "trade_type": trade_type
    }
    dbg(params)
    if product_id:  # trade_type=NATIVE时（即扫码支付），此参数必传
        params['product_id'] = product_id
    if openid:      # trade_type=JSAPI时（即公众号支付），此参数必传
        params['openid'] = openid
    if attach:
        params['attach'] = attach

    wechat_config = dbapi.get_wechat_config(agent_id=int(agent_id))
    key = wechat_config.mchkey
    sign_str       = params_sign(params, key)
    params['sign'] = sign_str

    # cert=('./key/apiclient_cert.pem', './key/apiclient_key.pem')
    xml_data  = dict_to_xml(params).encode('utf-8')
    r         = requests.post(url, data=xml_data)
    resp_data = r.content.decode('utf-8')
    xml_dict  = xml_to_dict(resp_data)

    try:
        assert("return_code" in xml_dict)
        assert(xml_dict["return_code"] == "SUCCESS")
    except:
        return (xml_dict, None)

    return (None, xml_dict)


def get_orderquery(out_trade_no=None, **kwargs):
    """
        @查询订单:
            https://pay.weixin.qq.com/wiki/doc/api/app/app.php?chapter=9_2&index=4
    """

    url    = "https://api.mch.weixin.qq.com/pay/orderquery"
    params = {
        "appid" : config.WECHAT_PAY_APPID,
        "mch_id": config.WECHAT_PAY_MCHID,
        "out_trade_no": out_trade_no,
        "nonce_str": nonce_str_gen()
    }

    sign_str       = params_sign(params)
    params['sign'] = sign_str

    xml_data  = dict_to_xml(params).encode('utf-8')
    r         = requests.post(url, data=xml_data)
    resp_data = r.content.decode('utf-8')
    xml_dict  = xml_to_dict(resp_data)

    try:
        assert "return_code" in xml_dict
        assert xml_dict["return_code"] == "SUCCESS"
    except:
        return (xml_dict, None)

    return (None, xml_dict)


def get_app_pay_request(**kwargs):
    err, unifiedorder = get_unifiedorder(**kwargs)
    if err is not None:
        return (err, None)
    try:
        assert("result_code" in unifiedorder)
        assert(unifiedorder["result_code"] == "SUCCESS")
        assert("prepay_id" in unifiedorder)
        assert(len(unifiedorder["prepay_id"]) > 0)
    except:
        dbg("[api.get_pay_request] unifiedorder error.\n\t%s" % str(unifiedorder))
        return (payRequest, None)

    payRequest = {
        "appid"    : unifiedorder["appid"],
        "partnerid": unifiedorder["mch_id"],
        "prepayid" : unifiedorder["prepay_id"],
        "package"  : "Sign=WXPay",
        "noncestr" : nonce_str_gen(),
        "timestamp": str(int(time.time()))
    }
    sign_str = params_sign(payRequest)
    payRequest['sign'] = sign_str
    return (None, payRequest)


def get_jsapi_pay_request(**kwargs):
    err, unifiedorder = get_unifiedorder(**kwargs)
    if err is not None:
        return (err, None)
    try:
        assert("result_code" in unifiedorder)
        assert(unifiedorder["result_code"] == "SUCCESS")
        assert("prepay_id" in unifiedorder)
        assert(len(unifiedorder["prepay_id"]) > 0)
    except:
        dbg("[api.get_pay_request] unifiedorder error.\n\t%s" % str(unifiedorder))
        return (unifiedorder, None)

    payRequest = {
        "appId"    : unifiedorder["appid"],
        "timeStamp": str(int(time.time())),
        "nonceStr" : nonce_str_gen(),
        "package"  : "prepay_id=%s" %(unifiedorder["prepay_id"]),
        "signType" : "MD5"
    }
    wechat_config = dbapi.get_wechat_config(agent_id=kwargs['agent_id'])
    key = wechat_config.mchkey
    sign_str = params_sign(payRequest, key)
    payRequest['paySign'] = sign_str
    return (None, payRequest)


def get_native_pay_request(**kwargs):
    err, unifiedorder = get_unifiedorder(**kwargs)
    if err is not None:
        return (err, None)
    try:
        assert("result_code" in unifiedorder)
        assert(unifiedorder["result_code"] == "SUCCESS")
        assert("prepay_id" in unifiedorder)
        assert(len(unifiedorder["prepay_id"]) > 0)
        assert("code_url" in unifiedorder)
        assert(len(unifiedorder["code_url"]) > 0)
    except:
        error_data = str(unifiedorder).encode('utf-8')
        dbg("[api.get_pay_request] unifiedorder error.\n\t%s" % str(error_data))
        return (unifiedorder, None)

    payRequest = {
        "code_url" : unifiedorder["code_url"],
        "prepay_id": unifiedorder["prepay_id"]
    }
    return (None, payRequest)


def refund_request(appid=None, mchid=None, trade_no=None, refund_no=None, 
    total_fee=None, refund_fee=None, agent_id=None, *args, **kwargs):
    url = "https://api.mch.weixin.qq.com/secapi/pay/refund"

    dict_data = {
        "appid": appid,
        "mch_id": mchid,
        "nonce_str": nonce_str_gen(),
        "out_trade_no": trade_no,
        "out_refund_no": refund_no, # 退款单 编号
        "total_fee" : int(total_fee),    # 支付金额 Int ( 单位: 分 )
        "refund_fee": int(refund_fee),   # 退款金额 Int ( 单位: 分 )
    }
    wechat_config = dbapi.get_wechat_config(agent_id=int(agent_id))
    key = wechat_config.mchkey
    dict_data['sign'] = params_sign(dict_data, key)
    data = dict_to_xml(dict_data).encode('utf-8')
    cert = (
        # os.path.join('C:\gitwork\street_app_server\keys\dev', 'apiclient_cert.pem'),
        # os.path.join('C:\gitwork\street_app_server\keys\dev', 'apiclient_key.pem'),
        os.path.join(wechat_config.key_path, 'apiclient_cert.pem'),
        os.path.join(wechat_config.key_path, 'apiclient_key.pem'),
    )
    dbg(cert)

    r = requests.post(url, data=data, cert=cert)
    """
        return_code: 
        return_msg: 
        
        result_code:
    """
    resp_data = r.content.decode('utf-8')
    r.close()

    if r.status_code != 200:
        return (r.content.decode("utf8"), None)

    xml_dict = xml_to_dict(resp_data)

    if "result_code" not in xml_dict or "result_code" not in xml_dict or xml_dict['result_code'] == 'FAIL':
        return (r.content.decode("utf8"), None)

    return (None, r.content.decode("utf8"))


def pay_to_user(openid=None, trade_no=None, money=None, desc=None,
        agent_id=None, **kwargs):
    # 单位: 分
    assert (isinstance(money, int) or isinstance(money, float))
    assert (isinstance(trade_no, str) or isinstance(trade_no, unicode) )
    assert (isinstance(openid, str) or isinstance(openid, unicode) )
    assert (isinstance(desc, str) or isinstance(desc, unicode) )

    MIN_MONEY = 100 # 单位： 分
    if money < MIN_MONEY:
        money = MIN_MONEY

    wechat_config = dbapi.get_wechat_config(agent_id=int(agent_id))
    appid = wechat_config.appid
    mchid = wechat_config.mchid

    param_dict = {
        'mch_appid': appid,
        'mchid': mchid,
        'nonce_str': nonce_str_gen(),
        'partner_trade_no': trade_no,
        'openid': openid,
        'check_name': 'NO_CHECK',
        'amount': int(money),
        'desc': desc,
        'spbill_create_ip': config.WECHAT_PAY_OUT_HOST
    }
    
    dbg("Pay To User:")
    dbg(param_dict)

    wechat_config = dbapi.get_wechat_config(agent_id=int(agent_id))
    key = wechat_config.mchkey
    param_dict['sign'] = params_sign(param_dict, key)
    url  = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/promotion/transfers'
    data = dict_to_xml(param_dict).encode('utf-8')

    cert = (
        os.path.join(wechat_config.key_path, 'apiclient_cert.pem'),
        os.path.join(wechat_config.key_path, 'apiclient_key.pem'),
    )
    print(cert)

    r = requests.post(url, data=data, cert=cert)
    resp_data = r.content.decode('utf-8')
    r.close()

    if r.status_code != 200:
        return (r.content.decode("utf8"), None)

    xml_dict = xml_to_dict(resp_data)
    print(xml_dict)
    print(resp_data)

    if "result_code" not in xml_dict or xml_dict['result_code'] == 'FAIL':
        return (r.content, None)

    return (None, xml_dict)