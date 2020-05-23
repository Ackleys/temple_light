from .config import DOMAIN

class HeZhouWuLian():
    NAME = '合宙物联'
    APP_ID = ''
    APP_SECRET = ''
    WECHAT_MCH_ID = ''
    WECHAT_MCH_KEY = ''
    REDIRECT_URI = 'http://%s/login/' % DOMAIN
    REDIRECT_BIND_URL = 'http://%s/bindwechat/' % DOMAIN
    JUMP_URL = 'your jump url'  # 这里是登陆以后的跳转，是否使用取决于你自己的需求
    TEMPLATE = {
        "CAUTION": ""
    }
    API_URL = 'http://api.xiaomanzaixian.com/common/'
    VERIFICATION_SMS = "您的验证码为:{0},请尽快确认!"


class MaFu():
    NAME = '码夫支付'
    APP_ID = ''
    APP_SECRET = ''
    WECHAT_MCH_ID = ''
    WECHAT_MCH_KEY = ''
    REDIRECT_URI = 'http://%s/login/' % DOMAIN
    REDIRECT_BIND_URL = 'http://%s/bindwechat/' % DOMAIN
    JUMP_URL = 'your jump url'  # 这里是登陆以后的跳转，是否使用取决于你自己的需求
    TEMPLATE = {
        "CAUTION": ""
    }
    API_URL = 'http://api.xiaomanzaixian.com/common/'
    VERIFICATION_SMS = "您的验证码为:{0},请尽快确认!"