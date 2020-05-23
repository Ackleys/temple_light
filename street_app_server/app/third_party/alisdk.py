#!/usr/bin/env python3
# coding: utf8
# 20170220 anChaOs

import json, time, hashlib, random, string
from datetime import datetime
import requests

import app.tool as tool
from app.tool import dbg                    # for print
from app.tool import print_exception_info   # for traceback

# database functions
import app.database.api as dbapi


import config as config


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


"""
    @ URL拼接

        *   `支付宝生活号` 网页授权 (https://docs.alipay.com/fw/api/105942)

"""
def gen_auth_url(app_id, scope, redirect_uri, state=""):
    urlbase  = "https://openauth.alipay.com/oauth2/publicAppAuthorize.htm"
    dbg(("[Redirect] %s\n%s", redirect_uri))
    params = {
        "app_id": app_id,
        "scope" : scope,                 # auth_base | auth_user
        "redirect_uri" : redirect_uri,
        "state" : state
    }
    # 排序params
    str_params = '&'.join(['%s=%s' % (key.lower(), params[key])
                           for key in sorted(params)])
    auth_url = urlbase + "?" + str_params
    return auth_url


"""
    @ 使用auth_code换取接口access_token及用户userId

        *   `支付宝生活号` 网页授权 (https://docs.alipay.com/fw/api/105942)

"""
def get_auth_access_token(app_id, auth_code, key_path):
    dbg('get_auth_access_token')
    url = 'https://openapi.alipay.com/gateway.do'
    data = {
        'app_id': app_id,
        'method': 'alipay.system.oauth.token',
        'charset': 'utf-8',
        'sign_type': 'RSA2',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'version': '1.0',
        'grant_type': 'authorization_code',
        'code': auth_code
    }
    _tmp = "&".join(['%s=%s' % (k, data[k]) for k in sorted(data)])
    dbg(key_path)
    try:
        sign = gen_sign256(key_path, _tmp)
    except:
        sign = tool.gen_sign(key_path, _tmp)
    data['sign'] = sign

    r = requests.get(url, params=data)
    if r.status_code == 200:
        result = json.loads(r.text)
        if "error_response" not in result:
            return True, result
        else:
            return False, result
    else:
        return False, r.text


"""
    @ 调用接口获取用户信息

        *   `支付宝生活号` 网页授权 (https://docs.alipay.com/fw/api/105942)

"""
def get_auth_user_info(app_id, auth_code, key_path):
    dbg('get_auth_user_info')
    succ, res = get_auth_access_token(app_id, auth_code, key_path)
    if not succ:
        return (False, res)
    url = 'https://openapi.alipay.com/gateway.do'
    data = {
        'app_id': app_id,
        'method': 'alipay.user.info.share',
        'charset': 'utf-8',
        'sign_type': 'RSA2',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'version': '1.0',
        'grant_type': 'authorization_code',
        'code': auth_code,
        'auth_token': res['alipay_system_oauth_token_response']['access_token']
    }
    _tmp = "&".join(['%s=%s' % (k, data[k]) for k in sorted(data)])
    try:
        sign = gen_sign256(key_path, _tmp)
    except:
        sign = tool.gen_sign(key_path, _tmp)
    data['sign'] = sign

    r = requests.get(url, params=data)
    if r.status_code == 200:
        result = json.loads(r.text)
        if "error_response" not in result:
            return True, result
        else:
            return False, result
    else:
        return False, r.text
