#!/usr/bin/env python3
# -*- coding: utf-8 -*-  
"""
python3

mqtt_to_mq

xiongchen 20150614
create

"""

import paho.mqtt.client as mqtt
import time
import logging
import sys
import traceback

logging.basicConfig(level=logging.DEBUG)
dbg = logging.debug

def print_execption_info():
    #dbg(type(sys.exc_info()[1]))
    #dbg(sys.exc_info()[1])
    try:
        traceback.print_exc()
    except:
        pass
    
from config import MQ_SERVER_IP, MQTT_BROKER_IP

from amqpy import Connection, Message

amqp_conn = None
amqp_channel = None
def amqp_reinit():
    global amqp_conn
    global amqp_channel
    dbg('amqp_reinit')
    amqp_conn = Connection(host = MQ_SERVER_IP) # mqtt broker 1
    amqp_channel = amqp_conn.channel()

    # declare an exchange and queue, and bind the queue to the exchange
    amqp_channel.exchange_declare('mqtt.exchange', 'direct', durable = True, auto_delete = False)
    amqp_channel.queue_declare('mqtt.q', durable = True, auto_delete = False)
    amqp_channel.queue_bind('mqtt.q', exchange = 'mqtt.exchange', routing_key = 'mqtt.q')

    # device coin check
    amqp_channel.exchange_declare('coincheck.exchange', 'direct', durable = True, auto_delete = False)
    amqp_channel.queue_declare('coincheck.q', durable = True, auto_delete = False)
    amqp_channel.queue_bind('coincheck.q', exchange = 'coincheck.exchange', routing_key = 'coincheck.q')

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    dbg("xcc Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    try:
        #client.subscribe("/device/+/devdata")
        client.subscribe("/v1/device/+/devdata")

        # device coin check
        client.subscribe("/v1/device/+/coincheck")
        print('subscribe ok')
    except:
        print_execption_info()

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    dbg(msg.topic + " -> " + str(msg.payload))
    dbg(type(msg.payload))
    
def on_devdata(client, userdata, msg):
    dbg("on_devdata %s" % (time.ctime()))
    dbg(msg.topic + " -> " + str(msg.payload))
    dbg(type(msg.payload))
    #for b in bytearray(msg.payload):
    #    print("%02X" % b)
    imei = msg.topic.split('/')[3]
    dbg(imei)
    #process_devdata(msg.payload, imei, 'fake_address')
    amqp_channel.basic_publish(Message(msg.payload, application_headers = {'imei':imei, 'topic':'devdata'}), exchange = 'mqtt.exchange', routing_key = 'mqtt.q')

def on_coin_check(client, userdata, msg):
    dbg("on_coin_check %s" % (time.ctime()))
    dbg(msg.topic + " -> " + str(msg.payload))
    dbg(type(msg.payload))
    #for b in bytearray(msg.payload):
    #    print("%02X" % b)
    imei = msg.topic.split('/')[3]
    dbg(imei)
    # amqp_channel.basic_publish(Message(msg.payload, application_headers = {'topic':msg.topic}), exchange = 'coincheck.exchange', routing_key = 'coincheck.q')
    amqp_channel.basic_publish(Message(msg.payload, application_headers = {'imei':imei, 'topic':'coincheck'}), exchange = 'mqtt.exchange', routing_key = 'mqtt.q')

if __name__ == '__main__':
    dbg('======================================================')
    dbg('======================================================')
    dbg('======================================================')
    dbg('======================================================')
    dbg('======================================================')
    dbg('======================================================')
    dbg('======================================================')
    dbg('======================================================')
    dbg('==================== mqtt_to_mq ======================')
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
        client = mqtt.Client(client_id = "mqtt_to_mq")
        client.on_connect = on_connect
        client.on_message = on_message
        
        client.message_callback_add("/v1/device/+/devdata", on_devdata)
        client.message_callback_add("/v1/device/+/coincheck", on_coin_check)

        dbg('connect MQTT_BROKER_IP %s' % MQTT_BROKER_IP)
        client.connect(MQTT_BROKER_IP, 1883, 60)
        
        try:
            amqp_reinit()
        except:
            print_execption_info()
            raise

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        client.loop_forever()
    except:
        print_execption_info()
