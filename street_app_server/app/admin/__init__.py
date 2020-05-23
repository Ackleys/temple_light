#!/usr/bin/env python3
# coding: utf8
# 20170220 anChaOs

from flask import Blueprint

admin_auth_blueprint = Blueprint('admin_auth', __name__)
admin_device_blueprint = Blueprint('admin_device', __name__)
admin_economic_blueprint = Blueprint('admin_economic', __name__)
admin_agent_blueprint = Blueprint('admin_agent', __name__)
admin_god_blueprint = Blueprint('admin_god', __name__)
admin_event_blueprint = Blueprint('admin_event', __name__)
admin_openapp_blueprint = Blueprint('admin_openapp', __name__)
admin_advertiser_blueprint = Blueprint('admin_advertiser', __name__)

# this should at last
from . import auth_views
from . import device_views
from . import economic_views
from . import agent_views
from . import god_views
from . import event_views
from . import openapp_views
from . import advertiser_views