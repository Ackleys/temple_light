import os
from .config import DOMAIN


class MaFuAli():
    if os.environ.get("production"):
        NAME = '码夫支付'
        APP_ID = ''
        RETURN_URL = 'http://%s/pay/' % DOMAIN
        NOTIFY_URL = 'http://%s/api/ali_notify' % DOMAIN
        REDIRECT_URI = 'http://%s/ali_oauth/' % DOMAIN
        KEY_PATH = '/airm2m_data/airm2m/projects/street_app_server/keys/pro/alipay/merchant/rsa_private_key.pem'
    else:
        NAME = '沙箱码夫支付'
        APP_ID = ''
        RETURN_URL = 'http://%s/pay/' % DOMAIN
        NOTIFY_URL = 'http://%s/api/ali_notify' % DOMAIN
        REDIRECT_URI = 'http://%s/ali_oauth/' % DOMAIN
        KEY_PATH = '/airm2m_data/airm2m/projects/street_app_server/keys/dev/alipay/merchant/rsa_private_key.pem'
