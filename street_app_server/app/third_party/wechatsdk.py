#!/usr/bin/env python3
# coding: utf8
# 20170220 anChaOs

import json, time, hashlib, random, string
import requests

from app.tool import dbg                    # for print
from app.tool import print_exception_info   # for traceback

# database functions
import app.database.api as dbapi

import config as config


def nonce_str_gen():
    nonce = list(string.digits + string.ascii_uppercase)
    random.shuffle(nonce)
    return ''.join(nonce[:16])


"""
    @微信网页身份授权

        *   `微信公众号` 网页授权 (https://mp.weixin.qq.com/wiki)

"""
def gen_auth_url(appid, redirect_uri, state="STATE"):
    urlbase  = "https://open.weixin.qq.com/connect/oauth2/authorize"
    dbg(("[Redirect] %s\n%s", redirect_uri))
    params = {
        "appid": appid,
        "redirect_uri" : redirect_uri,    # urllib.quote_plus(AuthCodeHandler)
        "response_type": "code",
        "scope": "snsapi_userinfo",       # snsapi_base | snsapi_userinfo
        "state": state,
        "connect_redirect": 1
    }
    # 排序params
    str_params = '&'.join(['%s=%s' % (key.lower(), params[key])
                           for key in sorted(params)])
    auth_url = urlbase + "?" + str_params + "#wechat_redirect"
    return auth_url


def get_auth_access_token(appid, appsecret, code):
    url    = "https://api.weixin.qq.com/sns/oauth2/access_token"
    params = {
        "appid" : appid,
        "secret": appsecret,
        "code"  : code,
        "grant_type": "authorization_code"
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        result = json.loads(r.text)
        if "errcode" not in result:
            return True, result
        else:
            return False, r.text
    else:
        return False, r.text


def get_auth_user_info(appid, appsecret, code):
    succ, res = get_auth_access_token(appid, appsecret, code)
    if not succ:
        return (False, res)
    url    = "https://api.weixin.qq.com/sns/userinfo"
    params = {
        "access_token": res['access_token'],
        "openid"      : res['openid'],
        "lang"        : "zh_CN"
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        user_info = json.loads(r.content.decode("utf8"))
        if "errcode" not in user_info:
            return True, user_info
        else:
            return False, r.text
    else:
        return False, r.text


"""
    @微信开发接口文档
        http://mp.weixin.qq.com/wiki/16/992df48524118c3e89945856694b30cc.html

"""
def request_access_token(appid, appsecret):
    params = {
        "grant_type": "client_credential",
        "appid" : appid,
        "secret": appsecret
    }
    url = "https://api.weixin.qq.com/cgi-bin/token"
    r   = requests.get(url, params=params)
    if r.status_code == 200:
        result = json.loads(r.text)
        if "access_token" in result:
            access_token = result['access_token']
            expires_in   = result['expires_in']
            succ = dbapi.update_access_token(appid, access_token, expires_in)
            if succ:
                return True, result['access_token']
            else:
                return False, 'save access_token error'
        else:
            return False, r.text
    else:
        return False, r.text


def get_access_token(appid, appsecret):
    token = dbapi.get_access_token(appid)
    if token:
        access_token = token['access_token']
        expires_in   = token['expires_in']
        utime        = token['utime']
        delay        = 300  # 缓冲时间300秒，5分钟
        timepass     = int(time.time()) - utime
        if timepass < (int(expires_in) - delay):
            # 未超时，token有效
            return access_token

    succ, data = request_access_token(appid, appsecret)
    if not succ:
        dbg("[WeChat API] `access_token` 获取失败: %s"  % data)
        return None
    else:
        return data


"""
    @微信开发接口文档
        http://mp.weixin.qq.com/wiki/

"""
def request_jsapi_ticket(appid):
    access_token = get_access_token(appid)
    print(access_token)
    if not access_token:
        return False, 'no access_token'
    params = {
        "access_token": access_token,
        "type" : "jsapi"
    }
    url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket"
    r   = requests.get(url, params=params)
    if r.status_code == 200:
        result = json.loads(r.text)
        if "ticket" in result:
            ticket = result['ticket']
            expires_in = result['expires_in']
            succ = dbapi.update_jsapi_ticket(appid, ticket, expires_in)
            if succ:
                return True, result['ticket']
            else:
                return False, 'save ticket error'
        else:
            return False, r.text
    else:
        return False, r.text


def get_jsapi_ticket(appid):
    ticket = dbapi.get_jsapi_ticket(appid)
    if ticket:
        jsapi_ticket = ticket['jsapi_ticket']
        expires_in   = ticket['expires_in']
        utime        = ticket['utime']
        delay        = 300  # 缓冲时间300秒，5分钟
        timepass     = int(time.time()) - utime
        if timepass < (int(expires_in) - delay):
            # 未超时，token有效
            return jsapi_ticket

    succ, data = request_jsapi_ticket()
    if not succ:
        dbg("[WeChat API] `jsapi_ticket` 获取失败: %s" % data)
        return None
    else:
        return data


def generate_jssdk_data(url):
    jsapi_ticket = get_jsapi_ticket()
    if not jsapi_ticket:
        return None
    nonceStr = nonce_str_gen()
    timestamp = int(time.time())
    ret = {
        'nonceStr'      : nonceStr,
        'jsapi_ticket'  : jsapi_ticket,
        'timestamp'     : timestamp,
        'url'           : url
    }

    def get_sign(ret):
        s = '&'.join(['%s=%s' % (key.lower(), ret[key])
                           for key in sorted(ret)])
        ret['signature'] = hashlib.sha1(
            s.encode('utf-8')).hexdigest()

        return ret

    return get_sign(ret)


"""
    @微信网页身份授权
        https://mp.weixin.qq.com/wiki

"""
def get_wechat_user_info(appid, appsecret, openid):
    url = 'https://api.weixin.qq.com/cgi-bin/user/info'
    access_token = get_access_token(appid, appsecret)
    if not access_token:
        return None
    params = {
        "access_token": access_token,
        "openid"      : openid,
        "lang"        : "zh_CN"
    }
    r = requests.get(url, params=params)
    if r.status_code == 200:
        result = r.json()
        if "subscribe" in result:
            return result
        else:
            dbg("获取用户信息错误: %s" % r.text)
            return None
    else:
        dbg("获取用户信息错误: %s" % r.text)
        return None