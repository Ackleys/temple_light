import os, time, json, traceback

import requests
from gevent import getcurrent

from app import celery

from app.database import api as dbapi

# error
import app.error as error
ApiError = error.ApiError


def dbg(msg):
    print("<pid:{0},greenlet:{1}>dbg:{2}".format(os.getpid(), id(getcurrent()), msg))


def print_exception_info():
    # dbg(type(sys.exc_info()[1]))
    # dbg(sys.exc_info()[1])
    # dbg(sys.exc_info()[-1].tb_lineno)
    traceback.print_exc()


@celery.task(bind=True)
def add_together(self, a, b):
    return a + b


@celery.task
def send_data_to_device(data, need_to_wait=True):
    topic = data['topic']
    imei  = data['imei']

    send_data = bytearray([0x54, data['device_type']])


    send_data += data['money'].to_bytes(4, 'big')
    send_data += data['duration'].to_bytes(4, 'big')
    send_data += data['high'].to_bytes(4, 'big')
    send_data += data['low'].to_bytes(4, 'big')
    send_data += data['pulse'].to_bytes(4, 'big')

    dbg(send_data)


    headers = {'Content-Type': 'application/json'}
    payload = {
        'code': 0,
        'msg' : ''
    }
    from ..tool import tools as tool
    try:
        result = tool.send_data_to_device(topic, imei, send_data, need_to_wait=need_to_wait, celery=True)
        if result['result'] == 0:
            payload['code'] = 8002
            payload['msg']  = '设备正在运行'
    except ApiError as e:
        dbg((e.msg, e.error_no))
        payload['code'] = e.error_no
        payload['msg']  = error.get_error_info(e.error_no)

    try:
        r = requests.post(data['async_url'], data=json.dumps(payload), headers=headers)
        dbg(r.text)
    except:
        print_exception_info()

    return 'ok'


@celery.task(bind=True)
def send_trans_data_to_server(self, imei, msg):
    try:
        cur_count = self.request.retries
        dbg(cur_count)
        time_list = (5, 15, 30, 60, 120)
        device = dbapi.get_device(imei=imei)
        if device:
            agent_setting = dbapi.get_agent_setting(agent_id=device.agent_id)
            if agent_setting and agent_setting.trans_url:
                r = requests.post(agent_setting.trans_url, json={'imei': imei, 'message': msg})
                if r.status_code == requests.codes.ok:
                    return 'ok'
                else:
                    dbg(r.text)
                    raise Exception('wrong data')
            else:
                dbg('no agent_setting or trans_url for agent_id: %d' % device.agent_id)
                raise Exception('url error')
        else:
            dbg('no device: %s' % imei)
            raise Exception('no device')
    except:
        print_exception_info()
        if cur_count < len(time_list):
            countdown = time_list[cur_count]
            raise self.retry(countdown=countdown, max_retries=5)
        else:
            return 'error'