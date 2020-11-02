import os, json
from flask import Flask, Blueprint, jsonify, g, make_response
from werkzeug.exceptions import BadRequest
from .common import ApiError, make_json
from app.tool import dbg, print_exception_info

def init_app(app: Flask):
  bp = Blueprint('v2', __name__, url_prefix='/admin/v2')

  @bp.errorhandler(ApiError)
  def handle_api_error(e: ApiError):
    resp = e.resp()
    return jsonify(make_json(code=int(e.key), msg=resp.msg)), resp.status

  @bp.errorhandler(BadRequest)
  def handle_validation_error(e: BadRequest):
    return jsonify(make_json(code=233, msg=e.get_description())), 422

  @bp.errorhandler(Exception)
  def handle_base_exception(current_error):
      print_exception_info()
      return make_response(json.dumps({'code':99, 'msg':'server error'}), 500)

  from . import device

  device.init_bp(bp)
  app.register_blueprint(bp)

  return app

