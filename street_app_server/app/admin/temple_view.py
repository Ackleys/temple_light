from . import admin_temple_blueprint
from app.admin.device_views import agent_id_required
import re

import os, json
from flask import session, jsonify, g, make_response
from flask_login import login_required, current_user

from app.tool import dbg, print_exception_info
import app.error as error
ApiError = error.ApiError

from app import db

import config as config
from flask_expects_json import expects_json

from random import randint
from base64 import b64decode

from app.database.model import Temple, Hall, Light, Duration
import app.database.api as dbapi

@admin_temple_blueprint.errorhandler(ApiError)
def handle_api_error(current_error):
    dbg((current_error.msg, current_error.error_no))
    error_info = error.get_error_info(current_error.error_no)
    return make_response(jsonify({'code':current_error.error_no, 'msg':error_info[0]}), error_info[1])


@admin_temple_blueprint.errorhandler(Exception)
def handle_base_exception(current_error):
    print_exception_info()
    return make_response(json.dumps({'code':99, 'msg':'server error'}), 500)


@admin_temple_blueprint.route('', methods=["GET"])
@login_required
@agent_id_required
def get_temple():
  dbg('GET temple')

  temple = current_user.cur_agent.temple
  if not temple:
    raise ApiError('ERROR_TEMPLE_NOT_FOUND', error.ERROR_TEMPLE_NOT_FOUND)

  reply ,status_code = {'code': 0, 'msg': ''}, 200
  reply['data'] = {
    'id': temple.id,
    'name': temple.name,
    'contactName': temple.contact_name,
    'contactInfo': int(temple.contact_info),
    'bannerImgUrl': os.path.join(config.V2_IMG_URL, temple.image),
    'createTime': '2017-5-13',
  }
  return make_response(jsonify(reply), status_code)

@admin_temple_blueprint.route('', methods=["POST"])
@login_required
@agent_id_required
@expects_json({
  'type': 'object',
  'properties': {
    'name': {
      'type': 'string',
      'minLength': 1,
      'maxLength': 64,
    },
    'contactName': {
      'type': 'string',
      'minLength': 1,
      'maxLength': 64,
    },
    'contactInfo': {
      'type': 'string',
    },
    'bannerImgUrl': {
      'type': 'string',
    },
  },
  'required': ['name', 'contactName', 'contactInfo', 'bannerImgUrl'],
})
def create_temple():
  dbg('POST temple')
  temple = current_user.cur_agent.temple
  if temple:
    raise ApiError('ERROR_TEMPLE_ALREADY_EXISTS', error.ERROR_TEMPLE_ALREADY_EXISTS)

  temple = Temple(
    name=g.data['name'],
    image=create_image(g.data['bannerImgUrl']),
    contact_name=g.data['contactName'],
    contact_info=g.data['contactInfo'],
    agent_id=current_user.cur_agent.id
  )
  db.session.add(temple)
  db.session.commit()

  reply ,status_code = {'code': 0, 'msg': ''}, 200
  reply['data'] = {
    'id': temple.id,
    'name': temple.name,
    'contactName': temple.contact_name,
    'contactInfo': int(temple.contact_info),
    'bannerImgUrl': os.path.join(config.V2_IMG_URL, temple.image),
    'createTime': '2017-5-13',
  }
  return make_response(jsonify(reply), status_code)

@admin_temple_blueprint.route('', methods=["PATCH"])
@login_required
@agent_id_required
@expects_json({
  'type': 'object',
  'properties': {
    'name': {
      'type': 'string',
      'minLength': 1,
      'maxLength': 64,
    },
    'contactName': {
      'type': 'string',
      'minLength': 1,
      'maxLength': 64,
    },
    'contactInfo': {
      'type': 'integer',
    },
    'bannerImgUrl': {
      'type': 'string',
    },
  },
})
def update_temple():
  dbg('PATCH temple')

  temple = current_user.cur_agent.temple
  if not temple:
    raise ApiError('ERROR_TEMPLE_NOT_FOUND', error.ERROR_TEMPLE_NOT_FOUND)

  if 'name' in g.data:
    temple.name = g.data['name']
  if 'contactName' in g.data:
    temple.contact_name = g.data['contactName']
  if 'contactInfo' in g.data:
    temple.contact_info = g.data['contactInfo']
  if 'bannerImgUrl' in g.data:
    try:
      file_name = create_image(g.data['bannerImgUrl'])
      try_delete_image(temple.image)
      temple.image = file_name
    except ValueError:
      ...

  db.session.commit()
  
  reply ,status_code = {'code': 0, 'msg': ''}, 200
  reply['data'] = {
    'id': temple.id,
    'name': temple.name,
    'contactName': temple.contact_name,
    'contactInfo': int(temple.contact_info),
    'bannerImgUrl': os.path.join(config.V2_IMG_URL, temple.image),
    'createTime': '2017-5-13',
  }
  return make_response(jsonify(reply), status_code)


@admin_temple_blueprint.route('/halls', methods=["POST"])
@login_required
@agent_id_required
@expects_json({
  'type': 'object',
  'properties': {
    'name': {
      'type': 'string',
      'minLength': 1,
      'maxLength': 128,
    },
    'relatedDeviceImei': {
      'type': 'number'
    },
  },
  'required': ['name', 'relatedDeviceImei'],
})
def create_hall():
  dbg('POST hall')
  temple = current_user.cur_agent.temple
  if not temple:
    raise ApiError('ERROR_TEMPLE_NOT_FOUND', error.ERROR_TEMPLE_NOT_FOUND)

  device = dbapi.get_device(imei=str(g.data['relatedDeviceImei']))
  if not device:
    raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)

  hall = Hall(
    name=g.data['name'],
    temple_id=temple.id,
    device_id=device.id,
  )
  db.session.add(hall)
  db.session.commit() #TODO IMEI重复

  reply ,status_code = {'code': 0, 'msg': ''}, 200
  reply['data'] = {
    'id': hall.id,
    'name': hall.name,
    'status': 'running', #TODO
    'relatedDeviceImei': int(hall.device.imei),
    'daily': { #TODO
      'flow': 0,
      'income': 0,
    },
  }
  return make_response(jsonify(reply), status_code)


@admin_temple_blueprint.route('/halls/<hall_id>', methods=["PATCH"])
@login_required
@agent_id_required
@expects_json({
  'type': 'object',
  'properties': {
    'name': {
      'type': 'string',
      'minLength': 1,
      'maxLength': 128,
    },
    'relatedDeviceImei': {
      'type': 'number'
    },
  },
})
def update_hall(hall_id):
  dbg('PATCH hall')
  temple = current_user.cur_agent.temple
  if not temple:
    raise ApiError('ERROR_TEMPLE_NOT_FOUND', error.ERROR_TEMPLE_NOT_FOUND)

  hall = Hall.query.get(hall_id)
  if hall.temple != temple:
    raise ApiError('ERROR_HALL_NOT_FOUND', error.ERROR_HALL_NOT_FOUND)

  if 'name' in g.data:
    hall.name = g.data['name']
  if 'relatedDeviceImei' in g.data:
    device = dbapi.get_device(imei=str(g.data['relatedDeviceImei']))
    if not device:
      raise ApiError('ERROR_DEVICE_NOT_FOUND', error.ERROR_DEVICE_NOT_FOUND)
    hall.device = device #NOTE: 测试

  db.session.commit()

  reply ,status_code = {'code': 0, 'msg': ''}, 200
  reply['data'] = {
    'id': hall.id,
    'name': hall.name,
    'status': 'running', #TODO
    'relatedDeviceImei': int(hall.device.imei),
    'daily': { #TODO
      'flow': 0,
      'income': 0,
    },
  }
  return make_response(jsonify(reply), status_code)

@admin_temple_blueprint.route('/halls', methods=["GET"])
@login_required
@agent_id_required
def get_halls():
  dbg('GET halls')
  temple = current_user.cur_agent.temple
  if not temple:
    raise ApiError('ERROR_TEMPLE_NOT_FOUND', error.ERROR_TEMPLE_NOT_FOUND)

  reply ,status_code = {'code': 0, 'msg': ''}, 200
  reply['data'] = [{
    'id': hall.id,
    'name': hall.name,
    'status': 'running', #TODO
    'relatedDeviceImei': int(hall.device.imei),
    'daily': { #TODO
      'flow': 0,
      'income': 0,
    },
  } for hall in temple.halls]
  return make_response(jsonify(reply), status_code)

@admin_temple_blueprint.route('/halls/<hall_id>', methods=["GET"])
@login_required
@agent_id_required
def get_hall(hall_id):
  dbg('GET hall')
  temple = current_user.cur_agent.temple
  if not temple:
    raise ApiError('ERROR_TEMPLE_NOT_FOUND', error.ERROR_TEMPLE_NOT_FOUND)

  hall = Hall.query.get(hall_id)
  if not hall or hall.temple != temple:
    raise ApiError('ERROR_HALL_NOT_FOUND', error.ERROR_HALL_NOT_FOUND)

  reply ,status_code = {'code': 0, 'msg': ''}, 200
  reply['data'] = {
    'id': hall.id,
    'name': hall.name,
    'status': 'running', #TODO
    'relatedDeviceImei': int(hall.device.imei),
    'daily': { #TODO
      'flow': 0,
      'income': 0,
    },
  }
  return make_response(jsonify(reply), status_code)

@admin_temple_blueprint.route('/halls/<hall_id>', methods=["DELETE"])
@login_required
@agent_id_required
def delete_hall(hall_id):
  dbg('DELETE hall')
  temple = current_user.cur_agent.temple
  if not temple:
    raise ApiError('ERROR_TEMPLE_NOT_FOUND', error.ERROR_TEMPLE_NOT_FOUND)

  hall = Hall.query.get(hall_id)
  if not hall or hall.temple != temple:
    raise ApiError('ERROR_HALL_NOT_FOUND', error.ERROR_HALL_NOT_FOUND)
  
  db.session.delete(hall)
  db.session.commit()
  reply ,status_code = {'code': 0, 'msg': ''}, 200
  return make_response(jsonify(reply), status_code)

@admin_temple_blueprint.route('/halls/<hall_id>/lights', methods=["POST"])
@login_required
@agent_id_required
@expects_json({
  'type': 'object',
  'properties': {
    'name': {
      'type': 'string',
      'minLength': 1,
      'maxLength': 64,
    },
    'price': {
      'type': 'number'
    },
    'imageUrl': {
      'type': 'string',
    }
  },
  'required': ['name', 'price', 'imageUrl'],
})
def create_lights(hall_id):
  dbg('POST light')
  temple = current_user.cur_agent.temple
  if not temple:
    raise ApiError('ERROR_TEMPLE_NOT_FOUND', error.ERROR_TEMPLE_NOT_FOUND)

  hall = Hall.query.get(hall_id)
  if not hall or hall.temple != temple:
    raise ApiError('ERROR_HALL_NOT_FOUND', error.ERROR_HALL_NOT_FOUND)

  light = Light(
    name=g.data['name'],
    price=g.data['price'],
    image=create_image(g.data['imageUrl']),
    hall=hall,
  )
  db.session.add(light)
  db.session.commit()

  reply ,status_code = {'code': 0, 'msg': ''}, 200
  reply['data'] = {
    'id': light.id,
    'name': light.name,
    'price': light.price,
    'imageUrl': os.path.join(config.V2_IMG_URL, light.image),
  }
  return make_response(jsonify(reply), status_code)


@admin_temple_blueprint.route('/halls/<hall_id>/lights/<light_id>', methods=["PATCH"])
@login_required
@agent_id_required
@expects_json({
  'type': 'object',
  'properties': {
    'name': {
      'type': 'string',
      'minLength': 1,
      'maxLength': 64,
    },
    'price': {
      'type': 'number'
    },
    'imageUrl': {
      'type': 'string',
    }
  },
})
def update_lights(hall_id, light_id):
  dbg('PATCH light')
  temple = current_user.cur_agent.temple
  if not temple:
    raise ApiError('ERROR_TEMPLE_NOT_FOUND', error.ERROR_TEMPLE_NOT_FOUND)

  hall = Hall.query.get(hall_id)
  if not hall or hall.temple != temple:
    raise ApiError('ERROR_HALL_NOT_FOUND', error.ERROR_HALL_NOT_FOUND)

  light = Light.query.get(light_id)
  if not light or light.hall != hall:
    raise ApiError('ERROR_LIGHT_NOT_FOUND', error.ERROR_LIGHT_NOT_FOUND)

  if 'name' in g.data:
    light.name = g.data['name']
  if 'price' in g.data:
    light.price = g.data['price']
  if 'imageUrl' in g.data:
    try:
      file_name = create_image(g.data['imageUrl'])
      try_delete_image(light.image)
      light.image = file_name
    except ValueError:
      ...
  db.session.commit()
  reply ,status_code = {'code': 0, 'msg': ''}, 200
  reply['data'] = {
    'id': light.id,
    'name': light.name,
    'price': light.price,
    'imageUrl': os.path.join(config.V2_IMG_URL, light.image),
  }
  return make_response(jsonify(reply), status_code)

@admin_temple_blueprint.route('/halls/<hall_id>/lights', methods=["GET"])
@login_required
@agent_id_required
def get_lights(hall_id):
  dbg('GET lights')
  temple = current_user.cur_agent.temple
  if not temple:
    raise ApiError('ERROR_TEMPLE_NOT_FOUND', error.ERROR_TEMPLE_NOT_FOUND)

  hall = Hall.query.get(hall_id)
  if not hall or hall.temple != temple:
    raise ApiError('ERROR_HALL_NOT_FOUND', error.ERROR_HALL_NOT_FOUND)

  reply ,status_code = {'code': 0, 'msg': ''}, 200
  reply['data'] = [{
    'id': light.id,
    'name': light.name,
    'price': light.price,
    'imageUrl': os.path.join(config.V2_IMG_URL, light.image),
  } for light in hall.lights]
  return make_response(jsonify(reply), status_code)

@admin_temple_blueprint.route('/halls/<hall_id>/lights/<light_id>', methods=["GET"])
@login_required
@agent_id_required
def get_light(hall_id, light_id):
  dbg('GET light')
  temple = current_user.cur_agent.temple
  if not temple:
    raise ApiError('ERROR_TEMPLE_NOT_FOUND', error.ERROR_TEMPLE_NOT_FOUND)

  hall = Hall.query.get(hall_id)
  if not hall or hall.temple != temple:
    raise ApiError('ERROR_HALL_NOT_FOUND', error.ERROR_HALL_NOT_FOUND)

  light = Light.query.get(light_id)
  if not light or light.hall != hall:
    raise ApiError('ERROR_LIGHT_NOT_FOUND', error.ERROR_LIGHT_NOT_FOUND)

  reply ,status_code = {'code': 0, 'msg': ''}, 200
  reply['data'] = {
    'id': light.id,
    'name': light.name,
    'price': light.price,
    'imageUrl': os.path.join(config.V2_IMG_URL, light.image),
  }
  return make_response(jsonify(reply), status_code)

@admin_temple_blueprint.route('/halls/<hall_id>/lights/<light_id>', methods=["DELETE"])
@login_required
@agent_id_required
def delete_light(hall_id, light_id):
  dbg('DELETE light')
  temple = current_user.cur_agent.temple
  if not temple:
    raise ApiError('ERROR_TEMPLE_NOT_FOUND', error.ERROR_TEMPLE_NOT_FOUND)

  hall = Hall.query.get(hall_id)
  if not hall or hall.temple != temple:
    raise ApiError('ERROR_HALL_NOT_FOUND', error.ERROR_HALL_NOT_FOUND)

  light = Light.query.get(light_id)
  if not light or light.hall != hall:
    raise ApiError('ERROR_LIGHT_NOT_FOUND', error.ERROR_LIGHT_NOT_FOUND)

  db.session.delete(light)
  db.session.commit()

  reply ,status_code = {'code': 0, 'msg': ''}, 200
  return make_response(jsonify(reply), status_code)

@admin_temple_blueprint.route('/halls/<hall_id>/durations', methods=["POST"])
@login_required
@agent_id_required
@expects_json({
  'type': 'object',
  'properties': {
    'name': {
      'type': 'string',
      'minLength': 1,
      'maxLength': 32,
    },
    'rate': {
      'type': 'number'
    },
  },
  'required': ['name', 'rate'],
})
def create_durations(hall_id):
  dbg('POST duration')
  temple = current_user.cur_agent.temple
  if not temple:
    raise ApiError('ERROR_TEMPLE_NOT_FOUND', error.ERROR_TEMPLE_NOT_FOUND)

  hall = Hall.query.get(hall_id)
  if not hall or hall.temple != temple:
    raise ApiError('ERROR_HALL_NOT_FOUND', error.ERROR_HALL_NOT_FOUND)

  duration = Duration(
    name=g.data['name'],
    duration=g.data['rate'],
    hall=hall,
  )
  db.session.add(duration)
  db.session.commit()

  reply ,status_code = {'code': 0, 'msg': ''}, 200
  reply['data'] = {
    'id': duration.id,
    'name': duration.name,
    'rate': duration.duration,
  }
  return make_response(jsonify(reply), status_code)

@admin_temple_blueprint.route('/halls/<hall_id>/durations/<duration_id>', methods=["PATCH"])
@login_required
@agent_id_required
@expects_json({
  'type': 'object',
  'properties': {
    'name': {
      'type': 'string',
      'minLength': 1,
      'maxLength': 32,
    },
    'rate': {
      'type': 'number'
    },
  },
})
def update_durations(hall_id, duration_id):
  dbg('PATCH duration')
  temple = current_user.cur_agent.temple
  if not temple:
    raise ApiError('ERROR_TEMPLE_NOT_FOUND', error.ERROR_TEMPLE_NOT_FOUND)

  hall = Hall.query.get(hall_id)
  if not hall or hall.temple != temple:
    raise ApiError('ERROR_HALL_NOT_FOUND', error.ERROR_HALL_NOT_FOUND)

  duration = Duration.query.get(duration_id)
  if not duration or duration.hall != hall:
    raise ApiError('ERROR_DURATION_NOT_FOUND', error.ERROR_DURATION_NOT_FOUND)

  if 'name' in g.data:
    duration.name = g.data['name']
  if 'rate' in g.data:
    duration.duration = g.data['rate']
  db.session.commit()
  reply ,status_code = {'code': 0, 'msg': ''}, 200
  reply['data'] = {
    'id': duration.id,
    'name': duration.name,
    'rate': duration.duration,
  }
  return make_response(jsonify(reply), status_code)

@admin_temple_blueprint.route('/halls/<hall_id>/durations', methods=["GET"])
@login_required
@agent_id_required
def get_durations(hall_id):
  dbg('GET durations')
  temple = current_user.cur_agent.temple
  if not temple:
    raise ApiError('ERROR_TEMPLE_NOT_FOUND', error.ERROR_TEMPLE_NOT_FOUND)

  hall = Hall.query.get(hall_id)
  if not hall or hall.temple != temple:
    raise ApiError('ERROR_HALL_NOT_FOUND', error.ERROR_HALL_NOT_FOUND)

  reply ,status_code = {'code': 0, 'msg': ''}, 200
  reply['data'] = [{
    'id': duration.id,
    'name': duration.name,
    'rate': duration.duration,
  } for duration in hall.durations]
  return make_response(jsonify(reply), status_code)

@admin_temple_blueprint.route('/halls/<hall_id>/durations/<duration_id>', methods=["GET"])
@login_required
@agent_id_required
def get_duration(hall_id, duration_id):
  dbg('GET duration')
  temple = current_user.cur_agent.temple
  if not temple:
    raise ApiError('ERROR_TEMPLE_NOT_FOUND', error.ERROR_TEMPLE_NOT_FOUND)

  hall = Hall.query.get(hall_id)
  if not hall or hall.temple != temple:
    raise ApiError('ERROR_HALL_NOT_FOUND', error.ERROR_HALL_NOT_FOUND)

  duration = Duration.query.get(duration_id)
  if not duration or duration.hall != hall:
    raise ApiError('ERROR_DURATION_NOT_FOUND', error.ERROR_DURATION_NOT_FOUND)

  reply ,status_code = {'code': 0, 'msg': ''}, 200
  reply['data'] = {
    'id': duration.id,
    'name': duration.name,
    'rate': duration.duration,
  }
  return make_response(jsonify(reply), status_code)

@admin_temple_blueprint.route('/halls/<hall_id>/durations/<duration_id>', methods=["DELETE"])
@login_required
@agent_id_required
def delete_duration(hall_id, duration_id):
  dbg('DELETE duration')
  temple = current_user.cur_agent.temple
  if not temple:
    raise ApiError('ERROR_TEMPLE_NOT_FOUND', error.ERROR_TEMPLE_NOT_FOUND)

  hall = Hall.query.get(hall_id)
  if not hall or hall.temple != temple:
    raise ApiError('ERROR_HALL_NOT_FOUND', error.ERROR_HALL_NOT_FOUND)

  duration = Duration.query.get(duration_id)
  if not duration or duration.hall != hall:
    raise ApiError('ERROR_LIGHT_NOT_FOUND', error.ERROR_LIGHT_NOT_FOUND)

  db.session.delete(duration)
  db.session.commit()

  reply ,status_code = {'code': 0, 'msg': ''}, 200
  return make_response(jsonify(reply), status_code)

def create_image(base64_url):
  match = re.match(r'^data:image/(\w+);base64,(.*)$', base64_url)
  if not match:
    raise ValueError('incorrect base64 url format')
  ext_name = match.group(1)
  data = b64decode(match.group(2))
  while True:
    file_name = f'{randint(10000000, 99999999)}.{ext_name}'
    file_path = os.path.join(config.V2_IMG_PATH, file_name)
    if not os.path.exists(file_name):
      break
  with open(file_path, 'wb') as f:
    f.write(data)
  return file_name

def try_delete_image(image_name):
  file_path = os.path.join(config.V2_IMG_PATH, image_name)
  if os.path.exists(file_path):
    os.remove(file_path)
