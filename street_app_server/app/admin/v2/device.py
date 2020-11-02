from flask import Blueprint, Flask, g
from flask_login import login_required, current_user
import app.database.api as dbapi
from app.database.model import Device, DeviceV2, DeviceAddress
from enum import IntEnum, Enum, auto
from flask_expects_json import expects_json
from app import db
from .common import pick, validate_resp, make_json, succeed
from .common import ApiError, BadResponse as BR
# jsonschema.exceptions.ValidationError

def init_bp(bp: Blueprint):
  @bp.route('/devices', methods=['POST'])
  @login_required
  @expects_json({
    'type': 'object',
    'properties': {
      **pick(props[DataProps.Device], 'imei', 'address', 'template', 'exp_resp'),
    },
    'additionalProperties': False,
    'minProperties': 4,
  })
  def create_device():  #TODO: 409错误
    device = Device(
      imei=g.data['imei'],
      address=DeviceAddress(address=g.data['address']),
      v2=DeviceV2(
        template=g.data['template'],
        exp_resp=g.data['exp_resp'],
      ),
    )
    current_user.agent.devices.append(device)
    return make_json({
      **pick(device, 'id', 'imei'),
      **get_device_state(device),
      'address': device.address.address,
      **pick(device.v2, ('template', ''), ('exp_resp', '')),
    })

  @bp.route('/devices/<int:device_id>', methods=['PATCH'])
  @login_required
  @expects_json({
    'type': 'object',
    'properties': {
      **pick(props[DataProps.Device], 'imei', 'address', 'template', 'exp_resp'),
    },
    'additionalProperties': False,
    'minProperties': 4,
  })
  def update_device(device_id: int):
    # 868956045184698
    device = Device.query.get(device_id)
    if not device or device.agent != current_user.agent:
      raise ApiError(Error.NotFound)

    device.imei = g.data['imei']
    device.address.address = g.data['address']
    if not device.v2:
      device.v2 = DeviceV2(
        template=g.data['template'],
        exp_resp=g.data['exp_resp'],
      )
    else:
      if 'template' in g.data:
        device.v2.template = g.data['template']
      if 'exp_resp' in g.data:
        device.v2.exp_resp = g.data['exp_resp']
    return make_json({
      **pick(device, 'id', 'imei'),
      **get_device_state(device),
      'address': device.address.address,
      **pick(device.v2, ('template', ''), ('exp_resp', '')),
    })

  @bp.route('/devices', methods=['GET'])
  @login_required
  @validate_resp({
    'type': 'array',
    'items': {
      'type': 'object',
      'properties': {
        **props[DataProps.Device],
      },
      'additionalProperties': False,
      'minProperties': 7,
    }
  })
  def get_devices():
    return make_json([
      {
        **pick(device, 'id', 'imei'),
        **get_device_state(device),
        'address': device.address.address,
        **pick(device.v2, ('template', ''), ('exp_resp', '')),
      } for device in current_user.agent.devices
    ])

 
  @bp.route('/devices/<int:device_id>', methods=['DELETE'])
  @login_required
  @succeed
  def delete_device(device_id: int):
    device = Device.query.get(device_id)
    if not device or device not in current_user.agent.devices:
      raise ApiError(Error.NotFound)
    
    db.session.delete(device)
    db.session.commit()

  ApiError.register_resp({
    Error.NotFound: BR(404, '设备不存在'),
  })


class CommState(IntEnum):
  Offline = 0
  Online = 1

def get_device_state(device: Device):
  comm_state: CommState = None
  signal: int = None
  status = dbapi.get_cws_device_status(device.imei)
  if status:
    comm_state = status.get('online', CommState.Offline)
  latest_report = dbapi.get_device_latestreport(device.imei)
  if not latest_report:
    comm_state = CommState.Offline
  else:
    if 'signal' in latest_report:
      signal = latest_report['signal']
  return {
    'signal': signal or 0,
    'comm_state': int(comm_state or CommState.Offline),
  }


class DataProps(Enum):
  Device = auto()

props = {
  DataProps.Device: {
    'id': {'type': 'integer'},
    'imei': {
      'type': 'string',
      'pattern': r'^\d{15}$',
    },
    'signal': {'type': 'integer'},
    'comm_state': {'type': 'integer'},
    'address': {'type': 'string'},
    'template': {'type': 'string'},
    'exp_resp': {'type': 'string'},
  }
}


class Error(IntEnum):
  NotFound = 100

