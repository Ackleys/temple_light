#!/usr/bin/env python3
# coding: utf8
# 20170425 anChaOs

import base64, json, requests, time, traceback
from base64 import b64decode, b64encode
from datetime import datetime

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature

MAX_ENCRYPT_SIZE = 117
MAX_DECRYPT_SIZE = 128


class PrivateKey(object):
    @classmethod
    def init_from_file(cls, key_path, password=None):
        key_file = open(key_path, "rb")
        return cls(key_file.read(), password=password)

    def __init__(self, path, password=None):
        with open(path, 'rb') as key_file:
            self.priv = serialization.load_pem_private_key(
                key_file.read(), password=password, backend=default_backend())
            self.pub = self.priv.public_key()

    def sign(self, msg):
        sign = self.priv.sign(
            msg,
            padding.PKCS1v15(),
            hashes.SHA1()
        )
        return sign

    def sign256(self, msg):
        sign = self.priv.sign(
            msg,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return sign

    def _verify(self, signature, msg):
        verify = self.pub.verify(
            signature,
            msg,
            padding.PKCS1v15(),
            hashes.SHA1()
        )
        return verify

    def verify(self, signature, msg):
        try:
            self._verify(signature, msg)
            return True
        except InvalidSignature as e:
            print(str(e))
            return False

    def encrypt(self, msg):
        cipher = ''.encode('utf-8')
        str_msg = msg.decode('utf-8')
        if len(str_msg) <= MAX_ENCRYPT_SIZE:
            cipher = self.pub.encrypt(
                msg,
                padding.PKCS1v15()
            )
        else:
            offset = 0
            while offset < len(str_msg):
                end = offset + MAX_ENCRYPT_SIZE
                cipher += self.encrypt(str_msg[offset: end].encode('utf-8'))
                offset = end
        return cipher

    def decrypt(self, cipher):
        plain = ''.encode('utf-8')
        if len(cipher) <= MAX_DECRYPT_SIZE:
            plain = self.priv.decrypt(
                cipher,
                padding.PKCS1v15()
            )
        else:
            offset = 0
            while offset < len(cipher):
                end = offset + MAX_DECRYPT_SIZE
                plain += self.decrypt(cipher[offset: end])
                offset = end
        return plain


class PublicKey(object):
    def __init__(self, path):
        with open(path, 'rb') as key_file:
            self.pub = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )

    def encrypt(self, msg):
        cipher = ''.encode('utf-8')
        str_msg = msg.decode('utf-8')
        if len(str_msg) <= MAX_ENCRYPT_SIZE:
            cipher = self.pub.encrypt(
                msg,
                padding.PKCS1v15()
            )
        else:
            offset = 0
            while offset < len(str_msg):
                end = offset + MAX_ENCRYPT_SIZE
                cipher += self.encrypt(str_msg[offset: end].encode('utf-8'))
                offset = end
        return cipher

    def verify(self, sign, msg):
        try:
            self.pub.verify(sign, msg, padding.PKCS1v15(), hashes.SHA1())
            return True
        except InvalidSignature as e:
            print(str(e))
            return False


def gen_sign256(prive_path, data):
    priv_key = PrivateKey(prive_path)
    sign = priv_key.sign256(data.encode('utf-8'))
    signature = base64.b64encode(sign).decode('utf-8')
    print(signature)
    return signature


def gen_sign(prive_path, data):
    priv_key = PrivateKey(prive_path)
    sign = priv_key.sign(data.encode('utf-8'))
    signature = base64.b64encode(sign).decode('utf-8')
    print(signature)
    return signature


def test():
    prive_path = 'rsa_private_key.pem'
    pub_path   = 'rsa_public_key.pem'
    priv_key = PrivateKey(prive_path)
    pub_key  = PublicKey(pub_path)

    # data = 'app_id=2017092708958253&biz_content={"body": "\u6d4b\u8bd5\u5546\u54c1", "subject": "\u6d4b\u8bd5\u6807\u9898", "out_trade_no": "test123456", "total_amount": 0.01, "product_code": "QUICK_WAP_WAY"}&charset=utf-8&method=alipay.trade.wap.pay&notify_url=http://wxapp.mafu.shop/api/alinotifytest&return_url=http://wxapp.mafu.shop/alitest&sign_type=RSA2&timestamp=2017-09-27 18:28:21&version=1.0'
    biz_content = {
        'body': '测试商品',
        'subject': '测试标题',
        'out_trade_no': 'test123456',
        'total_amount': 0.01,
        'product_code': 'QUICK_WAP_WAY',
    }
    data = {
        'app_id': '2017092708958253',
        'method': 'alipay.trade.wap.pay',
        'return_url': 'http://wxapp.mafu.shop/alitest',
        'charset': 'utf-8',
        'sign_type': 'RSA',
        'timestamp': '2017-09-27 18:28:21',
        'version': '1.0',
        'notify_url': 'http://wxapp.mafu.shop/api/alinotifytest',
        'biz_content': json.dumps(biz_content)
    }

    _tmp = "&".join(['%s=%s' % (k, data[k]) for k in sorted(data)])
    data = _tmp

    # sign 
    sign = priv_key.sign(data.encode('utf-8'))
    signature = base64.b64encode(sign).decode('utf-8')
    print(signature)

    # verify
    byte_sign = base64.b64decode(signature)
    verify    = pub_key.verify(byte_sign, data.encode('utf-8'))
    print(verify)

    # # encrypt
    # cipher = pub_key.encrypt(data.encode('utf-8'))
    # cipher_text = base64.b64encode(cipher).decode('utf-8')
    # print(cipher_text)

    # # decrypt
    # cipher = base64.b64decode(cipher_text)
    # new_data = priv_key.decrypt(cipher).decode('utf-8')
    # print(data, new_data)


if __name__ == '__main__':
    # test()
    gen_sign('../../keys/pro/alipay/merchant/rsa_private_key.pem', 'a=123')