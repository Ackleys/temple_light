#!/usr/bin/env python3
# -*- coding: utf-8 -*-  
"""
python3

device_data_worker

get device data from rabbitmq

xiongchen 20150614
create

"""

import sys
import os
import time
import datetime
import math
import json
import logging
import base64
import hashlib
import re
import traceback
import random

logging.basicConfig(level=logging.DEBUG)
#dbg = logging.debug

def dbg(msg):
    logging.debug("<pid:{0}>:{1}".format(os.getpid(), msg))

def print_exception_info():
    dbg(type(sys.exc_info()[1]))
    dbg(sys.exc_info()[1])
    dbg('line:%d' % sys.exc_info()[-1].tb_lineno)

# sqlalchemy
# http://sqlalchemy.org
from sqlalchemy import * # text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError, StatementError, TimeoutError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import sessionmaker
Base = declarative_base()

# mongodb
# http://api.mongodb.org/python/current/
from pymongo import MongoClient, ReturnDocument

# paho mqtt client
# https://www.eclipse.org/paho/clients/python/
import paho.mqtt.client as MQTT

# http requests
# http://www.python-requests.org/en/latest/
import requests

# multiprocessing
# https://docs.python.org/3/library/multiprocessing.html
from multiprocessing import Process, Pool

# http://amqp.readthedocs.org/en/latest/
# here amqpy is for sending/receiving messages through rabbitmq server.
from amqpy import Connection, Message, AbstractConsumer, Timeout

# airm2m config
from config import MONGODB_IP
from config import MYSQL_IP
from config import MYSQL_USER
from config import MYSQL_PASSWORD
from config import DATA_WORKER_NUM # for multiprocessing
from config import MQTT_BROKER_IP
from config import MQ_SERVER_IP
from config import MQTT_CLIENT_NAME
from config import BAIDUKEY
from config import GAODE_KEY
USE_MINIGPS = True

# urls
#APP_API_URL_XIAONIAO = "http://watch.airm2m.com/api"
COORDINATES_TO_ADDRESS_URL = "http://api.map.baidu.com/geocoder/v2/"
GAODE_LOCATING_URL = "http://apilocate.amap.com/position?"

XIAOMANONLINE_PROJECT_IDS = [10, 16, 17, 18, 19, 20, 21, 22, 23, 24]
WATCH_PROJECT_IDS = [13, 15]

PROJECTS_NEED_DISTANCE = [7, 8, 9, 11, 18, 20, 23, 24, 25]

#default东阳    #上海
DEFAULT_LAT = '29.305408'#'31.231'
DEFAULT_LNG = '120.170724'#'121.469'

# reply
FAIL = 0
OK = 1
REBOOT = 2
BUSY = 3
UNLOGGED = 4
NOTFOUND = 5
NOTVALID = 6
EXPIRED = 7
NORESULT = 8

# locating method
METHOD_GPS = 0
METHOD_BS = 1
METHOD_WIFI = 2
METHOD_HYBRID = 3

# alarm type
ALARM_ACC = 0
ALARM_SHAKING = 1
ALARM_LOWBATTERY = 2
ALARM_LOSINGEXTERNALPOWER = 3
ALARM_OVERSPEED = 4
ALARM_OUTOFCIRCLE = 5
ALARM_INCIRCLE = 6
ALARM_LOWBATTERYWARNING = 7
ALARM_OUTOFBORDER = 8
ALARM_INBORDER = 9
ALARM_MOVING = 10
ALARM_STOPPING = 11

IMEI_PATTERN = re.compile("^\d{15}$")

def bytes_to_int(array):
    try:
        return int.from_bytes(array, 'big', signed = False)
    except:
        print_exception_info()
        return 0

def bcd_to_str(bcd, len):
    string = ''
    value = 0
    
    for i in range(0, len):
        value = bcd[i] & 0x0F
        if value == 0xf:
            break
        string += str.format('%x' % value)
        value = bcd[i] >> 4
        if value == 0xf:
            break
        string += str.format('%x' % value)
    
    return string
    
def bcd_to_str2(bcd, len):
    string = ''
    value = 0
    for i in range(0, len):
        value = bcd[i] >> 4
        if value == 0xf:
            break
        string += str.format('%x' % value)
        value = bcd[i] & 0x0F
        if value == 0xf:
            break
        string += str.format('%x' % value)
    
    return string

#120.374741 -> 0x21 0x30 0x47 0x47 0xF1
#31.5147916 -> 0x30 0x51 0x41 0x97 0x61
#031.55555ff
def co_to_bcd(co_string):
    parts = co_string.split('.')
    
    padding = len(3 - parts[0])
    parts[0] = "0" * padding + parts[0]
        
    padding = len(7 - parts[1])
    parts[1] += "f" * padding
    
    co_string = parts[0] + parts[1]
    
    bcd = bytearray()
    for i in range(0, len(co_string), 2):
        bcd.append(int(co_string[i + 1], 16) * 16 + int(co_string[i], 16))
        
    return bcd

def phone_to_bcd(phone, **kwargs):
    #dbg('phone_to_bcd')
    bcd = bytearray()
    try:
        local_phone = phone
        length_org = len(local_phone)
        
        if "fixed_length" in kwargs:
            length_padding_f = kwargs['fixed_length']
        else:
            length_padding_f = length_org
        
        if length_padding_f % 2 == 1: # for filling 'f'
            length_padding_f += 1
        
        for i in range(length_org, length_padding_f):
            local_phone += 'f'
        
        for i in range(0, length_padding_f, 2):
            bcd.append(int(local_phone[i + 1], 16) * 16 + int(local_phone[i], 16))

        #dbg(bcd)
        return bcd
    except:
        dbg("phone_to_bcd wrong")
        print_exception_info()
        return ""

def imei_to_bcd(imei):
    #dbg('imei_to_bcd')
    bcd = bytearray()
    try:
        length = len(imei)
        if length != 15:
            return None;
        
        for i in range(length, 16):
            imei += 'f'
        
        for i in range(0, 16, 2):
            bcd.append(int(imei[i + 1], 16) * 16 + int(imei[i], 16))

        #dbg(bcd)
        return bcd
    except:
        dbg("imei_to_bcd wrong")
        print_exception_info()
        return None

def num_to_str(bcd, len):
    string = ''
    value = 0
    for i in range(0, len):
        value = bcd[i] >> 4
        string += str.format('%x' % value)
        value = bcd[i] & 0x0F
        string += str.format('%x' % value)
    
    return string

def transformLat(x, y):
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(y * math.pi) + 40.0 * math.sin(y / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(y / 12.0 * math.pi) + 320 * math.sin(y * math.pi / 30.0)) * 2.0 / 3.0
    return ret
    
def transformLon(x, y):
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(x * math.pi) + 40.0 * math.sin(x / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(x / 12.0 * math.pi) + 300.0 * math.sin(x / 30.0 * math.pi)) * 2.0 / 3.0
    return ret

def delta(lat, lon):
    # Krasovsky 1940
    # a = 6378245.0, 1/f = 298.3
    # b = a * (1 - f)
    # ee = (a^2 - b^2) / a^2
    a = 6378245.0; #  a: 卫星椭球坐标投影到平面地图坐标系的投影因子。
    ee = 0.00669342162296594323; #  ee: 椭球的偏心率。
    dLat = transformLat(lon - 105.0, lat - 35.0)
    dLon = transformLon(lon - 105.0, lat - 35.0)
    radLat = lat / 180.0 * math.pi;
    magic = math.sin(radLat)
    magic = 1 - ee * magic * magic
    sqrtMagic = math.sqrt(magic)
    dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * math.pi)
    dLon = (dLon * 180.0) / (a / sqrtMagic * math.cos(radLat) * math.pi)
    return (dLat, dLon)
    
def gcj_decrypt(gcjLat, gcjLon):
    d = delta(gcjLat, gcjLon)
    return (gcjLat - d[0], gcjLon - d[1])

#http://www.johndcook.com/python_longitude_latitude.html
#Computing the distance between two locations on Earth from coordinates
def distance_on_unit_sphere(lat1, long1, lat2, long2):#param float

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
        
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc * 6373000


class Device(Base): #(Device - User) many to many
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True)
    sn = Column(String(32), nullable=False, unique=True)
    imei = Column(String(32), nullable=False, unique=True)
    
    creatorid = Column(Integer, nullable=False, server_default="1")
    
    resetflag = Column(Integer, nullable=False, server_default="0")
    
    cut_power = Column(Integer, nullable=False, server_default="0")
    
    valid_time = Column(DateTime, nullable=True)
    
    expire_time = Column(DateTime, nullable=True)
    
    report_interval = Column(Integer(), nullable=False, server_default="20")#in seconds
    report_interval_init_flag = Column(Integer(), nullable=False, server_default="0")#true if user has did a setting
    
    cut_power_init_flag = Column(Integer(), nullable=False, server_default="0")#true if user has did a setting
    
    function_list_1 = Column(Integer(), nullable=False, server_default="0")#function_byte
    function_list_2 = Column(Integer(), nullable=False, server_default="0")#function_byte
    
    phone = Column(String(20), nullable=False, server_default="0")
    
    guarding = Column(Integer(), nullable=False, server_default="0")
    guarding_radius = Column(Integer(), nullable=False, server_default="100")
    masternumber = Column(String(128), nullable=False, server_default="0")
    
    device_type = Column(Integer(), nullable=False, server_default="0")
    name = Column(String(128), nullable=False, server_default="new device")
    
    fence = Column(String(128))
    gps_switch = Column(Integer(), nullable=False, server_default="1") # 1 on   0 off
    online = Column(Integer(), nullable=False, server_default="0") # 1 on   0 off
    # the settings in userdevice can be moved to here, depending on their fucking ideas.
    
    alarmonshaking = Column(Integer(), nullable=False, server_default="0")
    alarmonlowbattery = Column(Integer(), nullable=False, server_default="0")
    alarmonlowbatterywarning = Column(Integer(), nullable=False, server_default="0")
    alarmonlosingexternalpower = Column(Integer(), nullable=False, server_default="0")
    alarmonoverspeed = Column(Integer(), nullable=False, server_default="0")
    alarmoncrossingborder = Column(Integer(), nullable=False, server_default="0")
    alarmonacc = Column(Integer(), nullable=False, server_default="0")
    
    alarm_interval = Column(Integer(), nullable=False, server_default="2")
    
    lastshakingtime = Column(DateTime, nullable=False)
    lastlowbatterytime = Column(DateTime, nullable=False)
    lastlowbatterywarningtime = Column(DateTime, nullable=False)
    lastlosingexternalpowertime = Column(DateTime, nullable=False)
    lastcrossingbordertime = Column(DateTime, nullable=False)
    lastoverspeedtime = Column(DateTime, nullable=False)
    lastacctime = Column(DateTime, nullable=False)
    
    alarmonmoving = Column(Integer(), nullable=True, server_default="0")
    alarmonstopping = Column(Integer(), nullable=True, server_default="0")
    lastmovingtime = Column(DateTime, nullable=True)
    laststoppingtime = Column(DateTime, nullable=True)
    moving_status = Column(Integer(), nullable=True, server_default="0")
    
    guarding_lng = Column(String(20), nullable=False, server_default="121.53565")
    guarding_lat = Column(String(20), nullable=False, server_default="31.23945")
    guarding_radius = Column(Integer(), nullable=False, server_default="100")
    
    overspeed = Column(Integer(), nullable=False, server_default="200")
    
    alarming_mode = Column(Integer(), nullable=False, server_default="1")#2 sms 1 dial 3 all
    
    ban_hanlebar = Column(Integer(), nullable=False, server_default="0")
    lock_motor = Column(Integer(), nullable=False, server_default="0")
    control_power = Column(Integer(), nullable=False, server_default="0")
    buzzer_on = Column(Integer(), nullable=False, server_default="0")
    
    steps = Column(Integer(), nullable=False, server_default="0")
    step_time = Column(DateTime, nullable=False)
    
    heartbeat_interval = Column(Integer(), nullable=False, server_default="300")
    
    project = Column(Integer(), nullable=False, server_default="0")
    version = Column(String(24), nullable=False, server_default="0.0.0.0")
    locating_method = Column(Integer(), nullable=False, server_default="4")
    display_method = Column(Integer(), nullable=False, server_default="0")
    iccid = Column(String(32), nullable=False, server_default="")
    imsi = Column(String(32), nullable=False, server_default="")


class AlarmGenerator():
    need_to_check = True
    imei = ''
    worker = None
    lng = ''
    lat = ''
    battery = 0
    power = 0
    shaking = 0
    speed = 0
    moving_status = 0
    method = METHOD_GPS
    db_session = None
    #http_session = None
    
    def __init__ (self, imei = '', worker = 0, lng = '', lat = '', battery = 0, power = 0, shaking = 0, speed = 0, method = METHOD_GPS):
        self.need_to_check = True
        self.imei = imei
        self.lng = lng
        self.lat = lat
        self.battery = battery
        self.power = power
        self.shaking = shaking
        self.speed = speed
        self.method = method
        self.project = 0
        self.worker = worker # worker is DataWorker class, see below.
        self.db_session = worker.db_session
        #self.http_session = worker.http_session

# TODO: 主逻辑
class Consumer(AbstractConsumer):
    worker = None

    def __init__(self, channel, queue, worker):
        self.worker = worker
        super().__init__(channel, queue)

    def run(self, msg):
        dbg("worker #%d get rabbitmq message" % self.worker.worker_id)
        msg.ack()
        try:
            # dispatch messages
            dbg('msg.application_headers[topic]: %s' % msg.application_headers['topic'])
            self.worker.process_device_report(msg.body, msg.application_headers['imei'], msg.application_headers['topic'])
        except:
            print_exception_info()

# process messages
class DataWorker():
    worker_id = None
    dbengine = None
    DBSession = None

    db_session = None # mysql

    alarm_generator = None

    mongodb_client = None
    mongodb_cws_steps_hour = None
    mongodb_yaoyiyao = None
    
    http_session = None
    
    amqp_pos_conn = None
    amqp_pos_channel = None     # 注意这里都是amqp
    amqp_mqtt_conn = None
    amqp_mqtt_channel = None
    amqp_mqtt_consumer = None
    
    mqtt_client = None # paho client        
    
    project = None # device project id
    
    imei = None
    
    real_address_got = False
    real_address = "未知"
    baidu_lng = None
    baidu_lat = None
    lng = None
    lat = None
    
    def __init__(self, id):
        self.worker_id = id
        self.reinit_all()

    # 对于每个实例:
    # 创建一个MQTT的客户端mqtt_client(连接1883端口), id为web1_device_data_worker_{worker_id}, 获取频道并绑定至mqtt.q队列
    # 创建一个AMQP连接(amqp_mqtt_conn), 获取频道并绑定至pos.q队列, 以及mqtt.q队列, mqtt.q消费者是个派生类

    def reinit_all(self):
        self.reinit_mysql()
        self.reinit_mongodb()
        self.reinit_mqtt() #TODO: 注意一下
        self.amqp_reinit_pos_channel()
        self.amqp_reinit_mqtt_channel() #TODO: 注意一下
        self.http_session = requests.Session()
        self.alarm_generator = AlarmGenerator(worker = self)

    def reinit_mqtt(self):
        if self.mqtt_client:
            try:
                self.mqtt_client.disconnect()
            except:
                print_exception_info()
        
        self.mqtt_client = MQTT.Client(client_id = MQTT_CLIENT_NAME + '_device_data_worker_%d' % self.worker_id)
        result = self.mqtt_client.connect(MQTT_BROKER_IP)
        if result != 0:
            dbg("reinit_mqtt error")
            return False
        else:
            dbg("reinit_mqtt ok")

    def reinit_mysql(self):
        try:
            db = 'mysql+mysqlconnector://' + MYSQL_USER + ':' + MYSQL_PASSWORD + '@' + MYSQL_IP + ':3306/CWS_APP'
            self.dbengine = create_engine(db, echo = False, pool_size = 512, max_overflow = 0, pool_timeout = 0, pool_recycle = 5)
            Base.metadata.create_all(self.dbengine)

            DBSession = sessionmaker(bind = self.dbengine)
            self.db_session = DBSession()
            dbg(self.db_session)
            
        except:
            print_exception_info()

    def amqp_reinit_pos_channel(self):  # TODO: 这个是pos频道
        #conn = Connection()  # connect to guest:guest@localhost:5672 by default
        self.amqp_pos_conn = Connection(host = MQ_SERVER_IP)
        self.amqp_pos_channel = self.amqp_pos_conn.channel()

        # declare an exchange and queue, and bind the queue to the exchange
        self.amqp_pos_channel.exchange_declare('pos.exchange', 'direct', durable = True, auto_delete = False)
        self.amqp_pos_channel.queue_declare('pos.q', durable = True, auto_delete = False)
        
        self.amqp_pos_channel.queue_bind('pos.q', exchange = 'pos.exchange', routing_key = 'pos.q')

    def amqp_reinit_mqtt_channel(self):
        #conn = Connection()  # connect to guest:guest@localhost:5672 by default
        self.amqp_mqtt_conn = Connection(host = MQ_SERVER_IP)
        self.amqp_mqtt_channel = self.amqp_mqtt_conn.channel()

        # declare an exchange and queue, and bind the queue to the exchange
        self.amqp_mqtt_channel.exchange_declare('mqtt.exchange', 'direct', durable = True, auto_delete = False)
        self.amqp_mqtt_channel.queue_declare('mqtt.q', durable = True, auto_delete = False)
        
        self.amqp_mqtt_channel.queue_bind('mqtt.q', exchange = 'mqtt.exchange', routing_key = 'mqtt.q')

        self.amqp_mqtt_consumer = Consumer(self.amqp_mqtt_channel, 'mqtt.q', self)
        self.amqp_mqtt_consumer.declare()
    
    def reinit_mongodb(self):
        dbg("reinit_mongodb")
        self.mongodb_client = MongoClient("mongodb://" + MONGODB_IP + ":27017")
        self.mongodb_cws_steps_hour = self.mongodb_client.cws.steps_hour
        self.mongodb_yaoyiyao = self.mongodb_client.cws.yaoyiyao
    
    # coordinates to address(baidu)
    def get_real_address(self, lng, lat):
        dbg("get_real_address real_address_got = %r" % self.real_address_got)
        if self.real_address_got:
            return self.real_address, self.baidu_lng, self.baidu_lat
        
        self.real_address = "未知"
        self.baidu_lng = None
        self.baidu_lat = None
        
        if lng == '0' or lat == '0':
            return self.real_address, self.baidu_lng, self.baidu_lat
        
        try:
            query_string = (COORDINATES_TO_ADDRESS_URL + "?&ak=" + BAIDUKEY + "&location=%s,%s&output=json&coordtype=wgs84ll") % (lat, lng)
            http_result = self.http_session.get(query_string, timeout = 6)
            #dbg(http_result.status_code)
            jsonstr = http_result.text

            if http_result.status_code == 200:
                try:
                    res = json.loads(jsonstr)
                except:
                    dbg("exce json.loads")
                    print_exception_info()
                
                if res['status'] == 0:
                    #dbg("baidu conversion ok")
                    #lng = res["result"][0]["x"]
                    #lat = res["result"][0]["y"]
                    dbg("got address")
                    self.real_address = res["result"]["formatted_address"]
                    self.baidu_lng = res["result"]["location"]["lng"]
                    self.baidu_lat = res["result"]["location"]["lat"]
                    self.real_address_got = True
                    #dbg(address)
                else:
                    dbg("no address")
            else:
                dbg("no address")
        except Exception:
            dbg("exce get_real_address")
            print_exception_info()
        finally:
            return self.real_address, self.baidu_lng, self.baidu_lat

    def publish_mqtt_msg(self, topic, msg, imei):
        dbg('worker #%d publish_mqtt_msg' % self.worker_id)
        try:
            result, mid = self.mqtt_client.publish("/v1/device/{0}/{1}".format(imei, topic), msg, qos = 1)
            if result != MQTT.MQTT_ERR_SUCCESS:
                dbg("error result %d, mid %d" % (result, mid))
                return False
            else:
                dbg('publish_mqtt_msg ok')
                return True
        except:
            print_exception_info()
            self.reinit_mqtt()
            
        return False

    def add_new_device(self, imei, project):
        dbg('add_new_device %r project = %r' % (imei, project))

        device = self.db_session.execute("select id from CWS_APP.devices where imei = '%s'" % imei).fetchone()
        if device is not None:
            return
        
        dbg("add_new_device")
        
        old_time = datetime.datetime(2000,1,1)#datetime.datetime.now()
        future_time = datetime.datetime(2100,1,1)#datetime.datetime.now()
        
        sn = imei
        valid_time = old_time
        expire_time = future_time
        phone = imei
        device_name = imei
        dbg("sn %s, imei %s, valid_time %s, expire_time %s" % (sn, imei, valid_time, expire_time))
        
        if not IMEI_PATTERN.match(imei):
            dbg("add_new_device pattern error")
            return False
        
        newdevice = Device(sn = sn, imei = imei, name = device_name, creatorid = 1, valid_time = valid_time,expire_time = expire_time, phone = phone)

        newdevice.lastshakingtime = old_time
        newdevice.lastlowbatterytime = old_time
        newdevice.lastlowbatterywarningtime = old_time
        newdevice.lastlosingexternalpowertime = old_time
        newdevice.lastcrossingbordertime = old_time
        newdevice.lastoverspeedtime = old_time
        newdevice.lastacctime = old_time
        newdevice.lastmovingtime = old_time
        newdevice.laststoppingtime = old_time
        newdevice.step_time = old_time
        newdevice.steps = 0
        newdevice.heartbeat_interval = 300
        newdevice.project = project
        newdevice.version = '0.0.0.0'
        newdevice.alarming_mode = 2
        newdevice.locating_method = 4
        newdevice.display_method = 1
        newdevice.iccid = ''
        newdevice.imsi = ''
        newdevice.overspeed = 70
        
        if project == 0xd or project == 0xe or project == 0xf:
            newdevice.alarmonlowbattery = 1
        
        if project in XIAOMANONLINE_PROJECT_IDS: # xiaomanonline 9321m
            newdevice.guard = 0
            newdevice.alarmoncrossingborder = 0
            newdevice.alarmonshaking = 1
            newdevice.alarmonlosingexternalpower = 0
            newdevice.alarmonlowbattery = 1
            newdevice.alarmonmoving = 1
            newdevice.alarmonstopping = 1
        
        try:
            self.db_session.add(newdevice)
            dbresult = self.db_session.execute("select id, imei from street_machine.device where imei = '%s'" % (imei)).fetchone()
            if not dbresult:
                self.db_session.execute(text("insert into street_machine.device (imei ,ctime, utime) values (%s, now(), now())" % imei))
            self.db_session.commit()
            
            dbg(newdevice.id)
            
            if project != 0xc:
                device_time = datetime.datetime.now()  # FIXED: 调用错误
                self.update_latestreport(device_time, imei, DEFAULT_LNG, DEFAULT_LAT, 'status', 0, 0, 0, 0, 0, 0, 0, 0, 0, '0', '0', '0', '0', 0, 0, 0)

                self.update_device_status(imei = imei, power = 0)
        except IntegrityError:
            dbg("add_new_device error 1")
            print_exception_info()
            self.db_session.rollback()
            return
        except:
            dbg("add_new_device error 2")
            self.db_session.rollback()
            print_exception_info()
            return


    def update_device_status(self, imei, **kwargs):
        dbg("update_device_status")
        try:
            # get current
            current_record = self.mongodb_client.cws.device_status.find_one({'imei':imei})

            # as previous
            self.alarm_generator.device_status_previous = current_record

            '''
            # set to previous
            if current_record is not None:
                current_record.pop('_id')
                current_record.pop('imei')
                update = {'$set':current_record}
                
                self.mongodb_client.cws.device_status_previous.find_one_and_update({'imei':imei}, update, upsert = True)
            '''
            # update current
            kwargs['time'] = datetime.datetime.now()
            update = {'$set':kwargs}
            new_record = self.mongodb_client.cws.device_status.find_one_and_update({'imei':imei}, update, upsert = True, return_document = ReturnDocument.AFTER)

            self.alarm_generator.device_status = new_record
            self.device_status = new_record
        except:
            print_exception_info()

    def process_extra_data(self, imei, data, data_len, index, shake): # protocol 3.19
        # extra
        device_time = None
        need_wifi_result = 0
        moving_status = 0
        charging = 0
        shutdown_reason = 0
        delayed_seconds = 0
        
        while index < data_len:
            list_id = data[index]
            list_len = bytes_to_int(data[index + 1:index + 3]) # data[index + 1] * 256 + data[index + 2]
            index += 3
            
            if list_id == 0:
                temperature = str((int(data[index] * 256 + data[index + 1]) - 32768) / 100) # 32768 for padding
                dbg("temperature is %s" % temperature)
                try:
                    pass
                except:
                    dbg("temperature error")
                    print_exception_info()
            elif list_id == 1:
                steps = data[index] * 256 + data[index + 1]
                #dbg("steps = %d" % steps)
            elif list_id == 0x2: # need wifi result
                need_wifi_result = data[index]
            elif list_id == 0x4:
                # should be 4 bytes
                # time.time() = 1462514842 (0x572c349a)
                device_time = (data[index] << 24) + (data[index + 1] << 16) + (data[index + 2] << 8) + data[index + 3]
            elif list_id == 0x5:
                #device_status = self.mongodb_client.cws.device_status.find_one({'imei':imei})
                
                try:
                    moving_status = self.device_status['moving_status']
                except:
                    moving_status = 0
                    
                if moving_status == 1:
                    if data[index] == 0 and shake == 0:
                        moving_status = 0
                        self.moving_status_changed = True
                elif moving_status == 0:
                    if data[index] == 1 and shake == 1:
                        moving_status = 1
                        self.moving_status_changed = True
                
                dbg("moving_status is %d" % moving_status)
            elif list_id == 0x6:
                charging = data[index]
                dbg("charging is %d" % charging)
                
                self.update_device_status(imei = imei, charging = charging)
            elif list_id == 0x7:
                shutdown_reason = data[index]
                dbg("shutdown_reason is %d" % shutdown_reason)
            elif list_id == 0x8: # press button
                dbg("press button %d" % (data[index] & 0b1111111))
                long_press = data[index] >> 7
                key = data[index] & 0b1111111
                if key == 0:
                    key_name = 'power'
                else:
                    key_name = 'status'
            elif list_id == 0x9:
                dbg("check upiot iccid")
                pass
            elif list_id == 0xa: # upiot pin_status
                dbg("upiot pin_status")
                pass
            elif list_id == 0xb: # device delayed_seconds
                dbg("device delayed_seconds")
                try:
                    delayed_seconds = bytes_to_int(data[index:index + 2])
                    dbg('delayed_seconds = %d' % delayed_seconds)
                except:
                    print_exception_info()
            
            index += list_len
                
        if device_time is None:
            device_time = int(time.time())
            
        device_time -= delayed_seconds
            
        return device_time, need_wifi_result, moving_status, charging, shutdown_reason, delayed_seconds

    def update_latestreport(self, device_time, imei, lng, lat, status, dir, speed, power, acc, gpson, sleep, signal, satellites, battery, cell, lac, mcc, mnc, method, heartbeat, charging):
        dbg("update_latestreport")
        try:
            # fix discard_non_gps
            if self.project != 18 and 'discard_non_gps' in self.device_status and self.device_status['discard_non_gps'] == 1:
                dbg('fix %s' % imei)
                self.update_device_status(imei = imei, discard_non_gps = 0)
                self.device_status['discard_non_gps'] = 0
        
            if 'discard_non_gps' in self.device_status and self.device_status['discard_non_gps'] == 1 and method != METHOD_GPS:
                return
            
            dbg("do update")
            
            stayed_time = 0 # fake, for later use.
            
            if isinstance(device_time, int):
                device_time = datetime.datetime.fromtimestamp(device_time)
                
            #now_time = datetime.datetime.now()
            
            record = self.db_session.execute(text("select id from CWS_APP.latestreport where method = :method and imei = :imei"), {'imei':imei, 'method':method}).fetchone()

            # 主键 id 整数 递增
            # imei

            if record is None:
                self.db_session.execute(text("insert into CWS_APP.latestreport value(default, :imei, :lng, :lat, :time, :status, :dir, :speed, :power, :acc, :gpson, :sleep, :signal, :satellites, :battery, :cell, :lac, :mcc, :mnc, :method, :heartbeat, :stayed_time, :charging)"), {'imei':imei, 'lng':lng, 'lat':lat, 'time':device_time, 'status':status, 'dir':dir, 'speed':speed, 'power':power, 'acc':acc, 'gpson':gpson, 'sleep':sleep, 'signal':signal, 'satellites':satellites, 'battery':battery, 'cell':cell, 'lac':lac, 'mcc':mcc, 'mnc':mnc, 'method':method, 'heartbeat':heartbeat, 'stayed_time':stayed_time, 'charging':charging})
            else:
                if lng and lat:
                    self.db_session.execute(text("update CWS_APP.latestreport set lng = :lng, lat = :lat, time = :time, status = :status, dir = :dir, speed = :speed, power = :power, acc = :acc, gpson = :gpson, sleep = :sleep, latestreport.signal = :signal, satellites = :satellites, battery = :battery, cell = :cell, lac = :lac, mcc = :mcc, mnc = :mnc, heartbeat = :heartbeat, stayed_time = :stayed_time, charging = :charging where imei = :imei and method = :method"), {'imei':imei, 'lng':lng, 'lat':lat, 'time':device_time, 'status':status, 'dir':dir, 'speed':speed, 'power':power, 'acc':acc, 'gpson':gpson, 'sleep':sleep, 'signal':signal, 'satellites':satellites, 'battery':battery, 'cell':cell, 'lac':lac, 'mcc':mcc, 'mnc':mnc, 'method':method, 'heartbeat':heartbeat, 'stayed_time':stayed_time, 'charging':charging})
                else:
                    self.db_session.execute(text("update CWS_APP.latestreport set time = :time, status = :status, dir = :dir, speed = :speed, power = :power, acc = :acc, gpson = :gpson, sleep = :sleep, latestreport.signal = :signal, satellites = :satellites, battery = :battery, cell = :cell, lac = :lac, mcc = :mcc, mnc = :mnc, heartbeat = :heartbeat, stayed_time = :stayed_time, charging = :charging where imei = :imei and method = :method"), {'imei':imei, 'time':device_time, 'status':status, 'dir':dir, 'speed':speed, 'power':power, 'acc':acc, 'gpson':gpson, 'sleep':sleep, 'signal':signal, 'satellites':satellites, 'battery':battery, 'cell':cell, 'lac':lac, 'mcc':mcc, 'mnc':mnc, 'method':method, 'heartbeat':heartbeat, 'stayed_time':stayed_time, 'charging':charging}) 
            self.db_session.commit()
        except:
            print_exception_info()
            
    def save_pos(self, pos_dict):
        dbg("save_pos")
        try:
            if 'discard_non_gps' in self.device_status and self.device_status['discard_non_gps'] == 1 and pos_dict['method'] != METHOD_GPS:
                return
            
            imei = pos_dict['imei']
            #device_status = self.mongodb_client.cws.device_status.find_one({'imei':imei})
            
            if self.device_status is None:
                dbg('self.device_status is None')
                return
            
            stayed_time = 0
            if pos_dict['moving_status'] == 1:  # calculate stayed_time
                if 'moving_status' not in self.device_status:
                    pass
                else:
                    if self.device_status['moving_status'] == 0: # start moving
                        stayed_time = (datetime.datetime.now() - self.device_status['stopping_time']).seconds
                        #self.mongodb_client.cws.device_status.update_one({'imei':imei}, {'$set':{'moving_status':1}})
                        self.update_device_status(imei = imei, moving_status = 1)
            else:
                if 'moving_status' not in self.device_status or self.device_status['moving_status'] == 1: # moving -> stopping
                    #self.mongodb_client.cws.device_status.update_one({'imei':imei}, {'$set':{'stopping_time':datetime.datetime.now(), 'moving_status':0}})
                    self.update_device_status(imei = imei, stopping_time = datetime.datetime.now(), moving_status = 0)

            pos_dict['stayed_time'] = stayed_time
            
            dbg("do save")
            
            self.amqp_pos_channel.basic_publish(Message(json.dumps(pos_dict)), exchange = 'pos.exchange', routing_key = 'pos.q')
            
            pos_dict['address'] = self.get_real_address(pos_dict['lng'], pos_dict['lat'])[0]
        except:
            print_exception_info()

    #class GPRSServer(DatagramServer):
    def process_device_report(self, data_org, imei, topic):
        try:
            dbg('=================================================')
            dbg('=== %s: process_device_report imei = %s' % (time.ctime(), imei))
            
            self.real_address_got = False
            self.imei = imei
            self.moving_status_changed = False
            self.device_status = None

            mnc = ""
            mcc = ""
            lng = '0'
            lat = '0'
            
            result = NORESULT
            logtext = '%s' % (time.ctime())
            version = ""
            sn = ""
            report_interval = None
            shutdown = 0
            airplane_mode = 0
            startup = 0
            

            data = bytearray(data_org)
            data_string = ""
            for b in data:
                data_string += " %02X" % b
            dbg(data_string)        
            
            data_len = len(data)
            dbg("real len = %d" % data_len)
        
            command = data[0]
            logtext += ' topic %s imei %s command %d' % (topic, imei, command)
            
            dbg('topic %s imei %s command %d ' % (topic, imei, command))
            
            if not IMEI_PATTERN.match(imei):
                dbg("IMEI_PATTERN error")
                return False
                
            record = self.db_session.execute(text("select project, iccid from CWS_APP.devices where imei = :imei"), {'imei':imei}).fetchone()
            
            if record is not None:
                self.project = record['project']
                self.iccid = record['iccid']
                
            self.device_status = self.mongodb_client.cws.device_status.find_one({'imei':imei})
            self.alarm_generator.device_status = self.device_status
            
            # check commands
            if command == 7: # protocol 3.9 gps lbs 2   minigps
                self.alarm_generator.need_to_check = True
                dbg('command 7')
                direction = 0
                speed = 0
                mcc = 0
                mnc = 0
                
                #lng 11-15
                lng = bcd_to_str(data[1:6], 5)
                lng = lng[0:3] + '.' + lng[3:]

                #lat 16-20
                lat = bcd_to_str(data[6:11], 5)
                lat = lat[0:3] + '.' + lat[3:]

                lng = lng.lstrip('0')
                lat = lat.lstrip('0')
                
                direction = bytes_to_int(data[11:13]) # data[11] * 256 + data[12]
                speed = data[13]
                
                lac_num = data[14]
                
                dbg("lng %s lat %s lac_num %d" % (lng, lat, lac_num))

                method = METHOD_GPS
                #cells
                cells = []
                index = 15
                    
                for i in range(lac_num):
                    #dbg(data[index])
                    #dbg(data[index + 1])
                    #dbg(data[index + 2])
                    #dbg(data[index + 3])
                    #dbg(data[index + 4])
                    lac = bytes_to_int(data[index:index + 2]) # data[index] * 256 + data[index + 1]
                    if mcc == 0:
                        mcc = (data[index + 2] >> 4) * 4096 + (data[index + 2] & 0x0F) * 256 + (data[index + 3] >> 4) * 16 + (data[index + 3] & 0x0F)
                        mnc = data[index + 4]# * 16 + 4 + (data[index + 4] & 0x0F)
                        dbg('mcc %X mnc %X' % (mcc, mnc))
                    index += 5
                    cell_num = (data[index] >> 5) + 1
                        
                    for j in range(cell_num):
                        signal = data[index] & 31 #[4:0]
                        cell = bytes_to_int(data[index + 1:index + 3]) # data[index + 1] * 256 + data[index + 2]
                        cells.append((lac, cell, signal, mcc, mnc))
                        index += 3
                        
                ta = data[index]
                index += 1
                    
                #shake power acc gpson sleep
                shake = (data[index] >> 0) & 0x1
                power = (data[index] >> 1) & 0x1
                acc =   (data[index] >> 2) & 0x1
                gpson = (data[index] >> 3) & 0x1
                sleep = (data[index] >> 4) & 0x1
                airplane_mode = (data[index] >> 5) & 0x1
                shutdown = (data[index] >> 6) & 0x1
                index += 1
                        
                #gsmSignal  satellites
                gsmSignal = data[index] & 0x1F
                satellites = (data[index] >> 5) + (data[index + 1] >> 7) * 8
                index += 1
                        
                #battery
                battery = (data[index] & 0x7F) * 256 + data[index + 1]
                #dbg('battery %d' % (battery))
                index += 2
                
                # extra. protocol 3.19
                device_time, need_wifi_result, moving_status, charging, shutdown_reason, delayed_seconds = self.process_extra_data(imei, data, data_len, index, shake)
                    
                cells_num = len(cells)
                if cells_num > 7:
                    cells_num = 7
                        
                cell_string = ""
                for i in range(0, cells_num):
                    cell_string += "-%X-%X" % (cells[i][0], cells[i][1])
                    
                cell_signal_string = ""
                for i in range(0, cells_num):
                    cell_signal_string += "-%X-%X-%X" % (cells[i][0], cells[i][1], cells[i][2])
                logtext += ' charging %d shake %d mcc %s mnc %s power %d acc %d gpson %d sleep %d gsmSignal %d satellites %d battery %d cells %s' % (charging, shake, mcc, mnc, power, acc, gpson, sleep, gsmSignal, satellites, battery, cell_string)

                if lng != "0" and lng != "." and lat != "0" and lat != ".":
                    '''
                    if mcc:
                        try:
                            dbg('report to minigps')

                            query_string = "http://dataonline.cc/ds?x=%X-%X%s&l=%s,%s" % (mcc, mnc, cell_string, lat, lng)
                            dbg(query_string)
                            http_result = self.http_session.get(query_string, timeout = 6)
                            dbg(http_result.text)
                        except:
                            dbg('report to minigps error')
                            print_exception_info()
                    '''
                    
                    self.update_latestreport(device_time, imei, lng, lat, 'fake_status', direction, speed, power, acc, gpson, sleep, gsmSignal, satellites, battery, '0', '0', '0', '0', method, 0, charging)

                    kwargs = {'power':power}
                    
                    pos_dict = {'time':device_time, 'imei':imei, 'lng':lng, 'lat':lat, 'dir':direction, 'speed':speed, 'shake':shake, 'power':power, 'acc':acc, 'satellites':satellites, 'battery':battery, 'gpson':gpson, 'sleep':sleep, 'signal':gsmSignal, 'method':method, 'heartbeat':0, 'param':("%X-%X%s" % (mcc, mnc, cell_string)), 'moving_status':moving_status, 'charging':charging, 'project':self.project}
                        
                    self.save_pos(pos_dict)
                    
                    if self.project == 18 and method == METHOD_GPS:
                        kwargs['discard_non_gps'] = 1
                    self.update_device_status(imei = imei, **kwargs)
                else:
                    try:
                        dbg('query gaode')
                        query_string = GAODE_LOCATING_URL + "accesstype=0&cdma=0&imei=%s" % (imei)
                        
                        macs_string = "&macs="
                        #for mac in macs:
                        #    macs_string += "|%s,%d,fake" % (mac[0], mac[1])

                        bts_string = '&bts='
                        if cells_num:
                            bts_string += '%d,%d,%d,%d,%d' % (cells[0][3], cells[0][4], cells[0][0], cells[0][1], cells[0][2] * 2 - 113)
                        
                        nearbts_string = "&nearbts="
                        if cells_num >= 2:
                            for bs in cells[1:]:
                                nearbts_string += '|%d,%d,%d,%d,%d' % (bs[3], bs[4], bs[0], bs[1], bs[2] * 2 - 113)
                        
                        query_string += macs_string + bts_string + nearbts_string + '&serverip=118.31.2.124&output=json&key=' + GAODE_KEY
                            
                        dbg(query_string)
                        http_result = self.http_session.get(query_string, timeout = 6)
                        jsonstr = http_result.text
                        dbg("gaode pos:")
                        dbg(jsonstr)
                        res = json.loads(jsonstr)
                        
                        if res["status"] == "1" and res['info'] == 'OK' and res['result']['type'] != '0':
                            lo = lng = res['result']["location"]
                            lo = lo.split(',')
                            lng = lo[0]
                            lat = lo[1]
                            dbg('cell found at gaode %s %s' % (lng, lat))
                            method = METHOD_GPS
                            if res['result']['type'] == '2':
                                method = METHOD_WIFI
                            elif res['result']['type'] == '3':
                                method = METHOD_HYBRID
                            elif res['result']['type'] == '4':
                                method = METHOD_BS
                            
                            wgs_pos = gcj_decrypt(float(lat), float(lng))
                            lat = '%.7f' % wgs_pos[0]
                            lng = '%.7f' % wgs_pos[1]

                            self.update_latestreport(device_time, imei, lng, lat, 'fake_status', 0, 0, power, acc, gpson, sleep, gsmSignal, satellites, battery, 'fake', 'fake', 'fake', 'fake', method, 0, charging)

                            kwargs = {'power':power}
                            
                            result = OK
                                
                            # update pos  
                            pos_dict = {'time':device_time, 'imei':imei, 'lng':lng, 'lat':lat, 'dir':direction, 'speed':speed, 'shake':shake, 'power':power, 'acc':acc, 'satellites':satellites, 'battery':battery, 'gpson':gpson, 'sleep':sleep, 'signal':gsmSignal, 'method':method, 'heartbeat':0, 'param':(macs_string + bts_string + nearbts_string), 'moving_status':moving_status, 'charging':charging, 'project':self.project}
                        
                            self.save_pos(pos_dict)
                            
                            if self.project == 18 and method == METHOD_GPS:
                                kwargs['discard_non_gps'] = 1
                            self.update_device_status(imei = imei, **kwargs)
                        else:
                            dbg('gaode query error')
                            lng = 0
                            lat = 0
                            method = METHOD_GPS
                            self.update_latestreport(device_time, imei, lng, lat, 'fake_status', 0, 0, power, acc, gpson, sleep, gsmSignal, satellites, battery, 'fake', 'fake', 'fake', 'fake', method, 0, charging)

                            kwargs = {'power':power}
                            
                            result = OK
                                
                            # update pos  
                            pos_dict = {'time':device_time, 'imei':imei, 'lng':lng, 'lat':lat, 'dir':direction, 'speed':speed, 'shake':shake, 'power':power, 'acc':acc, 'satellites':satellites, 'battery':battery, 'gpson':gpson, 'sleep':sleep, 'signal':gsmSignal, 'method':method, 'heartbeat':0, 'param':(macs_string + bts_string + nearbts_string), 'moving_status':moving_status, 'charging':charging, 'project':self.project}
                        
                            self.save_pos(pos_dict)
                            
                            if self.project == 18 and method == METHOD_GPS:
                                kwargs['discard_non_gps'] = 1
                            self.update_device_status(imei = imei, **kwargs)
                    except:
                        print_exception_info()
            
                # alarm check
                self.alarm_generator.shaking = shake
                self.alarm_generator.power = power
                self.alarm_generator.battery = battery
                self.alarm_generator.lng = lng
                self.alarm_generator.lat = lat
                self.alarm_generator.speed = 0
                self.alarm_generator.method = method
                self.alarm_generator.acc = acc
                self.alarm_generator.imei = imei
                self.alarm_generator.moving_status = moving_status
                
                self.lng = lng
                self.lat = lat

            elif command == 0xE: # protocol 3.18 info
                dbg("protocol 3.18 info")
                self.alarm_generator.need_to_check = False
                
                need_to_make_new_device = False
                
                startup = 1
                
                dbresult = self.db_session.execute("select id, project, iccid from CWS_APP.devices where imei = '%s'" % (imei)).fetchone()
                
                update = {'$set':{'bb_status':0}}
                self.mongodb_client.cws.device_info.update_one({'imei':imei}, update, upsert = True)
                
                #except NoResultFound:
                #    need_to_make_new_device = True
                if not dbresult:
                    need_to_make_new_device = True
                else:
                    device_id = dbresult['id']
                
                index = 1
                while index < data_len:
                    dbg("index = %d data_len = %d" % (index, data_len))
                    item_id = data[index]
                    item_len = data[index + 1] * 256 + data[index + 2]
                    dbg("item_len = %d" % (item_len))
                    index += 3
                    
                    if item_id == 0: # project id
                        dbg("project id")
                        self.project = bytes_to_int(data[index:index + 2]) # data[index] * 256 + data[index + 1]
                        if need_to_make_new_device and self.project == 0xc or self.project == 0xd or self.project == 0xe or self.project == 0xf or self.project == 100 or self.project in XIAOMANONLINE_PROJECT_IDS or self.project == 25:
                            self.add_new_device(imei, self.project)
                        try:
                            dbg("update project id %d %s" % (self.project, imei))
                            dbresult = self.db_session.execute("update CWS_APP.devices set project = %d where imei = '%s'" % (self.project, imei))
                            self.db_session.commit()
                        except:
                            dbg("command == 0xE error 1")
                            print_exception_info()
                        index += 2
                        pass
                    elif item_id == 1: # heartbeat_interval
                        dbg("heartbeat_interval")
                        heartbeat_interval = bytes_to_int(data[index:index + 2]) # data[index] * 256 + data[index + 1]
                        try:
                            dbresult = self.db_session.execute("update CWS_APP.devices set heartbeat_interval = %d where imei = '%s'" % (heartbeat_interval, imei))
                        except:
                            print_exception_info()
                        index += 2
                    elif item_id == 2: # version
                        dbg("version")
                        version = ""
                        if (data[index] & 0xf) != 0xf:
                            version += "%d" % (data[index] & 0xf)
                            if ((data[index] >> 4) & 0xf) != 0xf:
                                version += ".%d" % ((data[index] >> 4) & 0xf)
                                if (data[index + 1] & 0xf) != 0xf:
                                    version += ".%d" % (data[index + 1] & 0xf)
                                    if ((data[index + 1] >> 4) & 0xf) != 0xf:
                                        version += ".%d" % ((data[index + 1] >> 4) & 0xf)
                        try:
                            dbresult = self.db_session.execute("update CWS_APP.devices set version = '%s' where imei = '%s'" % (version, imei))
                            
                            update = {'$set':{'lua_version':version}}
                            self.mongodb_client.cws.device_info.find_one_and_update({'imei':imei}, update, upsert = True)
                        except:
                            print_exception_info()
                        index += 2
                    elif item_id == 3: # gps_support
                        dbg("gps_support")
                        gps_support = bytes_to_int(data[index:index + 2]) # data[index] * 256 + data[index + 1]
                        index += 1
                    elif item_id == 4: # iccid
                        dbg("iccid")
                        iccid = ''
                        for i in range(0, item_len):
                            iccid += chr(data[index + i])
                        dbg("iccid = %s" % iccid)
                        try:
                            dbresult = self.db_session.execute("update CWS_APP.devices set iccid = '%s' where imei = '%s'" % (iccid, imei))
                        except:
                            print_exception_info()
                        index += item_len
                    elif item_id == 0xd: # imsi
                        dbg("imsi")
                        imsi = ''
                        for i in range(0, item_len):
                            imsi += chr(data[index + i])
                        dbg("imsi = %s" % imsi)
                        try:
                            dbresult = self.db_session.execute("update CWS_APP.devices set imsi = '%s' where imei = '%s'" % (imsi, imei))
                        except:
                            print_exception_info()
                        index += item_len
                    elif item_id == 8: # projeczt name, baseband_version
                        dbg("project name, baseband_version")
                        try:
                            project_name = data[index:(index + item_len)].decode('ascii')

                            update = {'$set':{'project_name':project_name, 'baseband_version':project_name}}
                            self.mongodb_client.cws.device_info.find_one_and_update({'imei':imei}, update, upsert = True)
                        except:
                            print_exception_info()
                            
                        index += item_len

                    self.db_session.commit()
                
                dbg('protocol 4.22 send time')
                
                # protocol 4.22 send time
                now_time = datetime.datetime.now()
                msg = bytearray([0x3c, 0, now_time.year - 2000, now_time.month, now_time.day, now_time.hour, now_time.minute, now_time.second])
                self.publish_mqtt_msg("set", msg, imei)
                
                # protocol 4.22 sms number
                msg = bytearray([0x3c, 0x4]) + phone_to_bcd("106905994540444")
                self.publish_mqtt_msg("set", msg, imei)

            # added by anChaOs
            elif command == 0x1B: # protocol 3.33 coin check
                dbg('protocol 3.33 coin check')
                self.alarm_generator.need_to_check = False

                coin_time = datetime.datetime(year=data[1] + 2000, 
                    month=data[2], day=data[3], hour=data[4], 
                    minute=data[5], second = data[6])

                coin = bytes_to_int(data[7:8])

                self.db_session.execute(text("insert into street_machine.offline_coin value(default, :imei, :coin_time, :coin, now(), now(), 0)"), {'imei': imei, 'coin_time': coin_time, 'coin': coin})

                msg = bytearray([0x55, 0x00])
                self.publish_mqtt_msg("coincheck", msg, imei)

                self.db_session.commit()
            
            # command over #

            dbg(logtext + '\n==== done')
            #self.db_session.close()
            self.db_session.commit()
        
        except:
            print_exception_info()
            self.db_session.commit()

    def start_working(self):
        try:
            # Start a mqtt client in new thread. I assume that it's thread safe. Maybe there are problems here.
            self.mqtt_client.loop_start()
        except:
            print_exception_info()
        
        # Infinite loop that sucking messages from rabbitmq
        while True:
            try:
                dbg("%s data worker #%d drain_events" % (time.ctime(), self.worker_id))
                self.amqp_mqtt_conn.drain_events(timeout = 60)
                
                # We can take a break here doing some other things
            except Timeout:
                pass
            except KeyboardInterrupt:
                dbg("over")
                break
            except:
                print_exception_info()
                self.reinit_all()

def process_function(worker_id):
    try:
        data_worker = DataWorker(worker_id)
        data_worker.start_working()
    except:
        print_exception_info()

if __name__ == '__main__':
    # make different ids for workers
    worker_ids = [id for id in range(1, DATA_WORKER_NUM + 1)]
    
    pool = Pool(processes = DATA_WORKER_NUM)
    
    try:
        # start all processes
        pool.map(process_function, worker_ids)
        pool.join()
    except:
        print_exception_info()
    
    dbg("pool.terminate")
    pool.terminate()
