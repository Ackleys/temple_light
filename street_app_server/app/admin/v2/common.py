from functools import wraps
from jsonschema import validate
from typing import Dict, Any, NamedTuple
from app import db

class BadResponse(NamedTuple):
  status: int
  msg: str

class ApiError(Exception):
  __responses: Dict[Any, BadResponse] = { }
  @classmethod
  def register_resp(cls, resp_dict: Dict[Any, BadResponse]):
    
    cls.__responses = {**cls.__responses, **resp_dict}

  def __init__(self, key):
    self.key = key

  def resp(self):
    return self.__responses[self.key]

def pick(obj, *args):
  d = {}
  for k in args:
    val = k # 第二个值是默认值
    def_val = None
    if type(k) in (tuple, list):
      val = k[0]
      def_val = k[1]
    try:
      attr_val = obj[k] if type(obj) is dict else getattr(obj, val)
      d[val] = attr_val if attr_val is not None else def_val
    except:
      d[val] = def_val
  return d

def make_json(data_dict: dict=None, *, code=0, msg=None):
  return {
    'code': code,
    **({'data': data_dict} if data_dict is not None else {}),
    **({'msg': msg} if msg is not None else {}),
  }

def succeed(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    func(*args, **kwargs)
    db.session.commit()
    return make_json(code=0, msg='OK')
  return wrapper

def validate_resp(data_schema=None, *, msg_required=False):
  def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
      # TODO: 根据不同情况获取json对象
      json_dict = func(*args, **kwargs)
      validate(instance=json_dict, schema={
        'type': 'object',
        'properties': {
          'code': {'type': 'integer'},
          'msg': {'type': 'string'},
          **({'data': data_schema} if data_schema is not None else {}),
        },
        'required': [
          'code', 
          *(['data'] if data_schema is not None else []), 
          *(['msg'] if msg_required else [])
        ],
        'additionalProperties': False,
      })
      return json_dict
    return wrapper
  return decorator
