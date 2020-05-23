#!/usr/bin/env python3
# -*- coding: utf-8 -*-  
"""
python3

mqtt_client_status

xiongchen 20170207
create

"""

#TODO: 与mqtt_client_status.x有关的代码

import paho.mqtt.client as mqtt
import time
import datetime
import logging
import traceback
import threading

logging.basicConfig(level = logging.DEBUG)
dbg = logging.debug

def print_execption_info():
    #dbg(type(sys.exc_info()[1]))
    #dbg(sys.exc_info()[1])
    traceback.print_exc()
    
from config import MQ_SERVER_IP, MQTT_BROKER_IP, MYSQL_IP, MYSQL_USER, MYSQL_PASSWORD

from sqlalchemy.orm import sessionmaker
from sqlalchemy import * # text
db = 'mysql+mysqlconnector://' + MYSQL_USER + ':' + MYSQL_PASSWORD + '@' + MYSQL_IP + ':3306/CWS_APP'
dbengine = create_engine(db, echo = False, pool_size = 512, max_overflow = 0, pool_timeout = 0, pool_recycle = 5)

DBSession = sessionmaker(bind = dbengine)
db_session = DBSession()

# mongo
from pymongo import MongoClient   
from config import MONGODB_IP

mongodb_client = None
mongodb_mqtt_client_status_table = None # todo: to detect dead device with wrong status(say online but actually dead, this will cause sending msg relentlessly)

def mongodb_reinit():
    global mongodb_client
    global mongodb_mqtt_client_status_table
    
    dbg("mongodb_reinit")
    mongodb_client = MongoClient("mongodb://" + MONGODB_IP + ":27017")
    mongodb_mqtt_client_status_table = mongodb_client.mqtt.client_status

from amqpy import Connection, Message

amqp_conn = None
amqp_channel = None
def amqp_reinit():
    global amqp_conn
    global amqp_channel
    amqp_conn = Connection(host = MQ_SERVER_IP) # mqtt broker 1
    amqp_channel = amqp_conn.channel()

    # declare an exchange and queue, and bind the queue to the exchange
    amqp_channel.exchange_declare('mqtt_client_status.e', 'direct', durable = True, auto_delete = False)
    amqp_channel.queue_declare('mqtt_client_status.q', durable = True, auto_delete = False)
    amqp_channel.queue_bind('mqtt_client_status.q', exchange = 'mqtt_client_status.e', routing_key = 'mqtt_client_status.k')


def tick_func():
    dbg('tick func is running')
    while True:
        dbg('querying expired devices')
        # {'$and': [{"online": 1 }, {'time': {'$lt', datetime.datetime.now() - datetime.timedelta(seconds=60*3)}}]}
        # {'client_name': imei, 'status': 1, 'time': datetime.datetime.now()})
        devices = mongodb_client.cws.device_status.find({'online': 1, 'time': {'$lt': datetime.datetime.now() - datetime.timedelta(seconds=60*3)}})
        # devices = mongodb_client.cws.device_status.find({'$and': [{"online": 1}, {'time': {'$lt': datetime.datetime.now() - datetime.timedelta(seconds=60*3)}}]})
        # 我们要得到的是client_name
        imeis = [device['imei'] for device in devices]
        if len(imeis) > 0:
            dbg('offlined devices:' + str(imeis))

        mongodb_mqtt_client_status_table.update_many({'client_name': {'$in': imeis}}, {'$set': {'status': 0}}, upsert=True)
        # mongodb_client.mqtt.status_record.update_many({'client_name': {'$in': imeis}, 'status': 0, 'time': datetime.datetime.now()})
        mongodb_client.cws.device_status.update_many({'imei': {'$in': imeis}}, {'$set': {'online': 0}}, upsert=True)

        time.sleep(10)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    dbg("xcc Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    try:
        #client.subscribe("/device/+/devdata")
        client.subscribe("$SYS/brokers/+/clients/+/+")  # TODO 这里订阅了上线和离线消息
    except:
        print_execption_info()

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    dbg(msg.topic + " -> " + str(msg.payload))
    dbg(type(msg.payload))
    
def on_status_changed(client, userdata, msg):
    dbg("on_status_changed %s" % (time.ctime()))
    dbg(msg.topic + " -> " + str(msg.payload))
    #dbg(type(msg.payload))
    #for b in bytearray(msg.payload):
    #    print("%02X" % b)
    
    # $SYS/brokers/emqttd_1884@127.0.0.1/clients/wfffffff/connected -> b'{"clientid":"wfffffff","username":"undefined","ipaddress":"59.172.80.27","session":false,"protocol":3,"connack":0,"ts":1486391181}'
    # $SYS/brokers/emqttd_1884@127.0.0.1/clients/wfffffff/disconnected -> b'{"clientid":"wfffffff","reason":"normal","ts":1486391186}'
        
    client_name, status = msg.topic.split('/')[4:6]
    mq_msg = None

    # cws.device_status['online']
    # 0 mqtt disconnected
    # 1 online
    # 2 sleep
    # 3 normal shutdown
    # 4 low-battery shutdown
    # 5 shutdown by timer
    # 6 shutdown remotely
    
    if status == 'connected':
        #1.connected(set mongodb and check offline msg)
        mq_msg = bytearray([0, 1])

        mongodb_mqtt_client_status_table.update_one({'client_name':client_name}, {'$set':{'status':1}}, upsert = True)
        mongodb_client.mqtt.status_record.insert_one({'client_name':client_name, 'status':1, 'time':datetime.datetime.now()})
        
        if client_name.isdigit() and len(client_name) == 15:
            try:
                dbg('update devices')
                db_session.execute('update devices set online = 1 where imei = "%s"' % client_name)
                db_session.commit()
                
                mongodb_client.cws.device_status.update_one({'imei':client_name}, {'$set':{'online':1}}, upsert = True)
            except:
                print_execption_info()

    elif status == 'disconnected':
        #2.disconnected(set mongodb)
        mq_msg = bytearray([0, 1])

        mongodb_mqtt_client_status_table.update_one({'client_name':client_name}, {'$set':{'status':0}}, upsert = True)
        mongodb_client.mqtt.status_record.insert_one({'client_name':client_name, 'status':0, 'time':datetime.datetime.now()})

        if client_name.isdigit() and len(client_name) == 15:
            record = mongodb_client.cws.device_status.find_one({"imei":client_name})
            if record is not None and 'online' in record:
                current_online_status = record['online']
                dbg('current state = %d' % current_online_status)
                if current_online_status in [0, 3, 4, 5, 6]: # ok
                    pass
                else:
                    dbg('warning. {0} disconnected from state {1}'.format(client_name, current_online_status))

                    online = 0

                    # get project
                    main_device = db_session.execute(text("select project from devices where imei = :imei"), {'imei':client_name}).fetchone()

                    # check battery
                    if main_device is not None:
                        dbg('project = %d' % main_device['project'])
                        if main_device['project'] == 18:
                            latest_report = db_session.execute(text("select battery from latestreport where imei = :imei order by time desc"), {'imei':client_name}).fetchone()

                            if latest_report is not None:
                                if latest_report['battery'] <= 3600:
                                    dbg('battery <= 3600')
                                    online = 4

                                    mongodb_client.cws.device_shutdown_record.insert_one({'imei':client_name, 'reason':4, 'time':datetime.datetime.now(), 'mqtt_disconn':1})

                    mongodb_client.cws.device_status.update_one({'imei':client_name}, {'$set':{'online':online, 'power':0, 'charging':0}}, upsert = True)

                try:
                    dbg('update devices')
                    db_session.execute('update devices set online = 0 where imei = "%s"' % client_name)
                    db_session.commit()
                except:
                    print_execption_info()

    print('client name ->', client_name)

    try:
        mq_msg += client_name.encode('ascii')
        result = amqp_channel.basic_publish(Message(mq_msg), exchange = 'mqtt_client_status.e', routing_key = 'mqtt_client_status.k')
    except UnicodeEncodeError:
        pass
    dbg('result = %r' % result)

if __name__ == '__main__':
    dbg('======================================================')
    dbg('======================================================')
    dbg('======================================================')
    dbg('======================================================')
    dbg('======================================================')
    dbg('======================================================')
    dbg('======================================================')
    dbg('======================================================')
    dbg('================ mqtt_client_status ==================')
    dbg('======================================================')
    dbg('======================================================')
    dbg('======================================================')
    dbg('======================================================')
    dbg('======================================================')
    dbg('======================================================')
    dbg('======================================================')
    dbg('======================================================')
    dbg('======================================================')
    
    try:
        mongodb_reinit()
        amqp_reinit()
    except:
        print_execption_info()
        raise

    try:
        client = mqtt.Client(client_id = "mqtt_client_status_1883")
        client.username_pw_set('guest', 'guest')
        
        client.on_connect = on_connect
        client.on_message = on_message
        
        # $SYS/brokers/emqttd_1884@127.0.0.1/clients/wfffffff/connected -> b'{"clientid":"wfffffff","username":"undefined","ipaddress":"59.172.80.27","session":false,"protocol":3,"connack":0,"ts":1486391181}'
        # $SYS/brokers/emqttd_1884@127.0.0.1/clients/wfffffff/disconnected -> b'{"clientid":"wfffffff","reason":"normal","ts":1486391186}'
        client.message_callback_add("$SYS/brokers/+/clients/+/+", on_status_changed)

        client.connect(MQTT_BROKER_IP, 1883, 60)

        p = threading.Thread(target=tick_func)
        p.setDaemon(True)
        p.start()

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        client.loop_forever()
    except:
        print_execption_info()
        raise
