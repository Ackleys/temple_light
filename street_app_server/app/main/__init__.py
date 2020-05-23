#!/usr/bin/env python3
# coding: utf8
# 20170220 anChaOs

from flask import Blueprint

main_blueprint = Blueprint('main', __name__)

# this should at last
from . import views