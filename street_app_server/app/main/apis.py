#!/usr/bin/env python3
# coding: utf8
# 20170220 anChaOs


import json, requests, string, random

from app.tool import dbg                    # for print
from app.tool import print_exception_info   # for traceback

def to_dict(self):
  return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}