import os

# 下面是主要数据库服务器的地址
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'root'
MYSQL_IP = 'placeholder'
DOMAIN = 'server.fzstack.com'  # 这里要填写域名

MONGODB_ADDRESS  = "mongodb://placeholder:27017"
MONGODB_ADDRESS_WST  = "mongodb://placeholder:27017"
USER_MYSQL_URI = 'mysql+mysqlconnector://%s:%s@%s/CWS_APP' % (MYSQL_USER, MYSQL_PASSWORD, MYSQL_IP)

ASSETS_PATH = '/root/projects/fw-share/streetweb/assets'
ADMINPAGE_PATH = '/root/projects/fw-share/streetweb'

V2_IMG_URL = '/static/img/v2'

from .wechat_config import *
from .ali_config import *

if os.environ.get("production"):
    print('"[Environ] 正式环境 ..."')
    WECHAT_LIST = {
        1: MaFu,
        3: MaFu,
        5: MaFu
    }

    MaFuAli = MaFuAli

    BIND_WECHAT_URL = 'http://%s/bindwechat/' % DOMAIN

    DEFAULT_PASSWORD = '888888'
    SECONDS_PER_MINITE = 60
    WECHAT_PAY_KEY_PATH = '/root/projects/fw-share/street_app_server/keys/pro'
    WECHAT_PAY_OUT_HOST = 'placeholder'

    ALI_PAY_KEY_PATH = '/root/projects/fw-share/street_app_server/keys/pro/alipay'

    PROJECT_TAG = "street_machine"
    DEVICE_MQTT_WAITING_TIME = 16
    MQTT_BROKER_IP = 'placeholder'

    # agent setting
    MIN_WTIHDRAW = 100
    L1 = 0.05
    L2 = 0.1
    L3 = 0.15
    WITHDRAW_FEE = 0.006

    # god
    DEFAULT_LOGO = 'img/logo/logo.png'
    DEFAULT_TITLE = '符网共享设备管理平台'

else:
    print('"[Environ] 测试环境 ..."')
    WECHAT_LIST = {
        1: HeZhouWuLian,
        3: HeZhouWuLian,
        5: HeZhouWuLian
    }

    MaFuAli = MaFuAli

    BIND_WECHAT_URL = 'http://%s/bindwechat/' % DOMAIN

    DEFAULT_PASSWORD = '888888'
    SECONDS_PER_MINITE = 1

    # 下面的两个支付密钥
    WECHAT_PAY_KEY_PATH = '/root/projects/fw-share/street_app_server/keys/dev'
    WECHAT_PAY_OUT_HOST = 'placeholder'

    ALI_PAY_KEY_PATH = '/root/projects/fw-share/street_app_server/keys/dev/alipay'

    PROJECT_TAG = "street_machine_test"
    DEVICE_MQTT_WAITING_TIME = 16
    MQTT_BROKER_IP = 'placeholder'

    # agent setting
    MIN_WTIHDRAW = 200
    L1 = 0.05
    L2 = 0.1
    L3 = 0.15
    WITHDRAW_FEE = 0.006

    # god
    DEFAULT_LOGO = 'img/logo/logo.png'
    DEFAULT_TITLE = '符网共享设备管理平台'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'NeverToldYou1234567890'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'mongodb'
    SESSION_KEY_PREFIX = 'street_' # 不同项目用不同前缀
    SESSION_USE_SIGNER = True
    SESSION_MONGODB_DB = 'common_data'
    SESSION_MONGODB_COLLECT = 'street_session'

    # celery
    CELERY_BROKER_URL = 'pyamqp://guest@placeholder//' 
    CELERY_RESULT_BACKEND = 'redis://placeholder:6379/0' 
    CELERY_TASK_SERIALIZER = 'json'

    @staticmethod
    def init_app(app):
        pass

# 下面是默认配置, 里面的SQLALCHEMY_DATABASE_URI就是我们要配的服务器地址
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'mysql+mysqlconnector://%s:%s@%s/street_machine?charset=utf8mb4' % (MYSQL_USER, MYSQL_PASSWORD, MYSQL_IP)
    print('database addr %s' % SQLALCHEMY_DATABASE_URI)
    SQLALCHEMY_POOL_RECYCLE = 5
    SELF_IP = '127.0.0.1'
    NOTIFY_URL = 'http://%s/api/pay/notify/' % DOMAIN
    SQLALCHEMY_BINDS = {
        'CWS_APP': 'mysql+mysqlconnector://%s:%s@%s/CWS_APP' % (MYSQL_USER, MYSQL_PASSWORD, MYSQL_IP),
        'openluat_users'  : 'mysql+mysqlconnector://%s:%s@%s/openluat_user?charset=utf8' % (MYSQL_USER, MYSQL_PASSWORD, MYSQL_IP),
        'users' : 'mysql+mysqlconnector://%s:%s@%s/street_machine?charset=utf8mb4' % (MYSQL_USER, MYSQL_PASSWORD, MYSQL_IP),
    }
   

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'mysql+mysqlconnector://%s:%s@%s/street_machine?charset=utf8mb4' % (MYSQL_USER, MYSQL_PASSWORD, MYSQL_IP)
    SELF_IP = '127.0.0.1'
    NOTIFY_URL = 'http://%s/api/pay/notify/' % DOMAIN
    SQLALCHEMY_BINDS = {
        'CWS_APP': 'mysql+mysqlconnector://%s:%s@%s/CWS_APP' % (MYSQL_USER, MYSQL_PASSWORD, MYSQL_IP),
        'openluat_users'  : 'mysql+mysqlconnector://%s:%s@%s/openluat_user?charset=utf8' % (MYSQL_USER, MYSQL_PASSWORD, MYSQL_IP),
        'users' : 'mysql+mysqlconnector://%s:%s@%s/street_machine?charset=utf8mb4' % (MYSQL_USER, MYSQL_PASSWORD, MYSQL_IP),
    }

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+mysqlconnector://%s:%s@%s/street_machine?charset=utf8mb4' % (MYSQL_USER, MYSQL_PASSWORD, MYSQL_IP)
    SELF_IP = '127.0.0.1'
    NOTIFY_URL = 'http://%s/api/pay/notify/' % DOMAIN
    SQLALCHEMY_BINDS = {
        'CWS_APP': 'mysql+mysqlconnector://%s:%s@%s/CWS_APP' % (MYSQL_USER, MYSQL_PASSWORD, MYSQL_IP),
        'openluat_users'  : 'mysql+mysqlconnector://%s:%s@%s/openluat_user?charset=utf8' % (MYSQL_USER, MYSQL_PASSWORD, MYSQL_IP),
        'users' : 'mysql+mysqlconnector://%s:%s@%s/street_machine?charset=utf8mb4' % (MYSQL_USER, MYSQL_PASSWORD, MYSQL_IP),
    }

config_list = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
