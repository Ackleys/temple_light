from celery import Celery

from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from pymongo import MongoClient

from config import config

from flask_session import Session

session = Session()

# 使用127.0.0.1:27017 作为mongodb数据库的地址
mongodb = MongoClient(config.MONGODB_ADDRESS)
mongodb_wst = MongoClient(config.MONGODB_ADDRESS_WST)
db = SQLAlchemy()
lm = LoginManager()
lm.session_protection = 'strong'
lm.login_view = 'admin_auth.unlogin'

# celery
celery = Celery(__name__, broker=config.Config.CELERY_BROKER_URL)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config.config_list[config_name])
    config.config_list[config_name].init_app(app)

    app.config['SESSION_MONGODB'] = mongodb
    session.init_app(app)

    db.init_app(app)
    lm.init_app(app)
    # celery
    celery.conf.update(app.config)    # 更新 celery 的配置

    # ======= some blueprints ========
    from .main import main_blueprint
    from .api  import api_blueprint

    from .admin import admin_auth_blueprint
    from .admin import admin_device_blueprint
    from .admin import admin_economic_blueprint
    from .admin import admin_agent_blueprint
    from .admin import admin_god_blueprint
    from .admin import admin_event_blueprint
    from .admin import admin_openapp_blueprint
    from .admin import admin_advertiser_blueprint


    app.register_blueprint(main_blueprint)

    #app.register_blueprint(Blueprint('assets', __name__, static_url_path='/assets', static_folder=config.ASSETS_PATH))
    #app.register_blueprint(Blueprint('adminpage', __name__, static_url_path='/adminpage', static_folder=config.ADMINPAGE_PATH))

    app.register_blueprint(api_blueprint, url_prefix='/api')

    # admin
    app.register_blueprint(admin_auth_blueprint, url_prefix='/admin/auth')
    app.register_blueprint(admin_device_blueprint, url_prefix='/admin/device')
    app.register_blueprint(admin_economic_blueprint, url_prefix='/admin/economic')
    app.register_blueprint(admin_agent_blueprint, url_prefix='/admin/agent')
    app.register_blueprint(admin_god_blueprint, url_prefix='/admin/god')
    app.register_blueprint(admin_event_blueprint, url_prefix='/admin/event')
    app.register_blueprint(admin_openapp_blueprint, url_prefix='/admin/openapp')
    app.register_blueprint(admin_advertiser_blueprint, url_prefix='/admin/advertiser')

    return app

