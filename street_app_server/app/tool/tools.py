#!/usr/bin/env python3
# coding: utf8
# 20170220 anChaOs

import os, time, zipfile, traceback, requests, hashlib

# paho mqtt client
# https://www.eclipse.org/paho/clients/python/
import paho.mqtt.client as MQTT
import config as config

from gevent import getcurrent
from gevent.event import AsyncResult
from gevent.timeout import Timeout

import app.tasks.event as tasks_event

import app.error as error


def compress(zip_file, input_dir):
  f_zip = zipfile.ZipFile(zip_file, 'w')
  for root, dirs, files in os.walk(input_dir):
    for f in files:
      # 获取文件相对路径，在压缩包内建立相同的目录结构
      abs_path = os.path.join(os.path.join(root, f))
      rel_path = os.path.relpath(abs_path, os.path.dirname(input_dir))
      f_zip.write(abs_path, rel_path, zipfile.ZIP_STORED)


def extract(zip_file, output_dir):
  f_zip = zipfile.ZipFile(zip_file, 'r')

  # # 解压所有文件到指定目录
  # f_zip.extractall(output_dir)

  # 逐个解压文件到指定目录
  for f in f_zip.namelist():
    f_zip.extract(f, output_dir)


#dbg = print
def dbg(msg):
    print("<pid:{0},greenlet:{1}>dbg:{2}".format(os.getpid(), id(getcurrent()), msg))


def print_exception_info():
    # dbg(type(sys.exc_info()[1]))
    # dbg(sys.exc_info()[1])
    # dbg(sys.exc_info()[-1].tb_lineno)
    traceback.print_exc()


def gen_imei15(imei14):
    if len(imei14) != 14:
        raise ValueError('imei len error: %s' % imei14)
    i = 0
    res = 0
    while i < 14:
        odd  = int(imei14[i])
        i   += 1
        even = int(imei14[i])
        temp = '%02d' % (even * 2)
        res += odd + int(temp[0]) + int(temp[1])
        i   += 1

    res %= 10
    res  = str(10 - res)[-1]
    return imei14 + str(res)


def make_paixing_sign(url, imei, message):
    key = "&key=D5391A0D2733431781D4BCB34417A7D5"
    _tmp = "%s?imei=%s&message=%s%s" % (url, imei,message, key)
    print(_tmp)
    m = hashlib.md5()
    m.update(_tmp.encode("utf8"))
    return m.hexdigest().upper()


if __name__ == '__main__':
    imei = '862991419827909'
    imei14 = imei[:-1]
    print(imei14)
    print(gen_imei15(imei14))


mqtt_client = None
def on_connect(client, userdata, rc):
    dbg("client_id = {0}_api_flask_pid_{1} on_connect".format(config.PROJECT_TAG, os.getpid()))
    re = mqtt_client.subscribe("/v1/device/+/deveventrsp/+")
    dbg("subscribe result = {}".format(re))

    re = mqtt_client.subscribe("/v1/+/c_trans")
    dbg("subscribe result = {}".format(re))

    re = mqtt_client.subscribe("/v1/+/common/c_trans")
    dbg("subscribe result = {}".format(re))


# mqtt实时命令
# 每个进程会起一个mqtt client。当app某个操作需要等待设备回复时，会起一个gevent的AsyncResult，并阻塞等待。
# 如果收到回复，会用token找到对应的AsyncResult，跳回对应的http请求。
# 如果超时，直接回复超时错误。
async_event_dict = {}
def on_message(client, userdata, message):
    dbg("on_message")
    try:
        dbg(message.payload)
        items = message.topic.split('/')
        dbg(items)
        if len(items) > 4 and items[4] == "deveventrsp":
            if 'fake_token' in message.topic:
                return
            global async_event_dict 
            dbg('len(async_event_dict) = %d' % len(async_event_dict))
            dbg(async_event_dict)
            dbg("receive {0}, topic = {1}".format(message.payload, message.topic))
            try:
                token = int(items[5])
            except ValueError:
                dbg('value err')
                return
            if token not in async_event_dict:
                dbg('not in async dict')
                return
            if message.payload[0] == 0xc: # protocol 3.15
                if message.payload[1] == 0x54: # payment notification
                    data = {}
                    # [2] result
                    data['result'] = message.payload[2]
                    dbg('%r start set' % async_event_dict[token])
                    if isinstance(async_event_dict[token], AsyncResult):
                        async_event_dict[token].set(data)
                    else:
                        async_event_dict[token] = data
                    dbg('%r set succ' % async_event_dict[token])

        if items[3] == "c_trans":
            if message.payload[0] == 0x1c: # protocol 3.5
                imei = items[2]
                data = message.payload[1:]
                send_data = str(data, encoding="utf-8")
                dbg(send_data)
                url = 'https://www.idenx.cn/wxAPI/GprsReturn'
                params = {
                    'message': send_data,
                    'sign'  : make_paixing_sign(url, imei, send_data)
                }
                res = requests.post(url, params=params)
                dbg(res.text)

        if len(items) > 4 and items[4] == 'c_trans':
            if message.payload[0] == 0x1c: # protocol 3.5
                imei = items[2]
                key_word = items[3]
                data = message.payload[1:]
                try:
                    send_data = data.decode('utf-8')
                except:
                    send_data = str(data)

                dbg('tasks_event.send_trans_data_to_server.delay(imei, send_data)')
                tasks_event.send_trans_data_to_server.apply_async(args=(imei, send_data), max_retries=5)
    except:
        print_exception_info()


def reinit_mqtt():
    dbg("reinit_mqtt")
    global mqtt_client
    if mqtt_client:
        try:
            re = mqtt_client.disconnect()
            dbg("disconnect result = {}".format(re))
        except:
            print_exception_info()
    
    dbg("client_id = {0}_api_flask_pid_{1}".format(config.PROJECT_TAG, os.getpid()))
    mqtt_client = MQTT.Client(client_id = '{0}_api_flask_pid_{1}'.format(config.PROJECT_TAG, os.getpid()))
    result = mqtt_client.connect(config.MQTT_BROKER_IP)
    if result != 0:
        dbg("reinit_mqtt error")
        return False
    else:
        dbg("reinit_mqtt ok")
    
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.loop_start()

def publish_mqtt_msg(topic, msg, qos = 0):
    global mqtt_client
    dbg("publish_mqtt_msg topic = %s" % (topic))
    try:
        result, mid = mqtt_client.publish(topic, msg, qos = qos)
        if result != MQTT.MQTT_ERR_SUCCESS:
            dbg("error result %d, mid %d" % (result, mid))
            return False
        
        dbg('publish_mqtt_msg ok')
    except:
        print_exception_info()
        
        # reinit and try once more
        reinit_mqtt()
        
        try:
            dbg(msg)
            result, mid = mqtt_client.publish(topic, msg, qos = qos)
            if result != MQTT.MQTT_ERR_SUCCESS:
                dbg("error result %d, mid %d" % (result, mid))
                return False
            
            dbg('publish_mqtt_msg ok')
        except:
            print_exception_info()
            return False
        return True
        
    return True


def wait_device_mqtt(greenlet_id):
    global async_event_dict
    mqtt_event = AsyncResult()
    async_event_dict[greenlet_id] = mqtt_event
    dbg("wait_device_mqtt. len(async_event_dict) = %d" % len(async_event_dict))
    try:
        # 起gevent事件并等待
        dbg('%r start get' % mqtt_event)
        result = mqtt_event.get(timeout=config.DEVICE_MQTT_WAITING_TIME)
        return result
    except Timeout:
        #print_exception_info()
        dbg("wait_device_mqtt except Timeout")
        raise error.ApiError("timeout", error.ERROR_TIMEOUT)
    finally:
        if greenlet_id in async_event_dict:
            dbg("del %r" % greenlet_id)
            del async_event_dict[greenlet_id]

def wait_device_mqtt_celery(greenlet_id):
    global async_event_dict
    async_event_dict[greenlet_id] = None
    dbg("wait_device_mqtt. len(async_event_dict) = %d" % len(async_event_dict))

    # 起gevent事件并等待
    for i in range(config.DEVICE_MQTT_WAITING_TIME):
        if async_event_dict[greenlet_id] != None:
            if greenlet_id in async_event_dict:
                data = async_event_dict[greenlet_id]
                dbg("del %r" % greenlet_id)
                del async_event_dict[greenlet_id]
            return data
        time.sleep(1)

    dbg("wait_device_mqtt except Timeout")
    if greenlet_id in async_event_dict:
        dbg("del %r" % greenlet_id)
        del async_event_dict[greenlet_id]
    raise error.ApiError("timeout", error.ERROR_TIMEOUT)

# 发送mqtt给设备
def send_data_to_device(topic, imei, data, need_to_wait=True, celery=False):
    dbg("send_data_to_device")

    # get greenlet id as key
    current_greenlet_id = id(getcurrent())

    mqtt_result = publish_mqtt_msg("/v1/device/{0}/{1}/{2}".format(imei, topic, current_greenlet_id), data)

    if need_to_wait:
        if not celery:
            result = wait_device_mqtt(current_greenlet_id)
            dbg('wait_device_mqtt result: %s' % result)
        else:
            result = wait_device_mqtt_celery(current_greenlet_id)
            dbg('wait_device_mqtt_celery result: %s' % result)
        
    else:
        result = 0
    
    return result


# 发送透传数据给设备
def send_trans_data_to_device(topic, imei, data, need_to_wait=False):
    dbg("send_trans_data_to_device")

    mqtt_result = publish_mqtt_msg("/v1/{0}/{1}".format(imei, topic), data)


# 发送新透传数据给设备
def send_key_word_trans_data_to_device(topic, imei, key_word, data, need_to_wait=False):
    dbg("send_key_word_trans_data_to_device")

    mqtt_result = publish_mqtt_msg("/v1/{0}/{1}/{2}".format(imei, key_word, topic), data)