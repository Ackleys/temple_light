#!/usr/bin/env python3
# coding: utf8
# 20170220 anChaOs

from flask import Blueprint

api_blueprint = Blueprint('api', __name__)

# this should at last
from . import views