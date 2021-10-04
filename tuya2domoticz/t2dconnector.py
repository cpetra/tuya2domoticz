import os
import sys
import logging
from tuya_connector import (
    TuyaOpenAPI,
    TuyaOpenPulsar,
    TuyaCloudPulsarTopic,
    TUYA_LOGGER,
)
import json
import re
import requests
import urllib.request
from datetime import datetime
import time
from . import t2d_devman

API_ENDPOINT = "https://openapi.tuya{}.com"
MQ_ENDPOINT = "wss://mqe.tuya{}.com:8285/"

class t2dconnector:
    config = {}
    uid = ""
    def __init__(self, config):
        name = vars(sys.modules[__name__])['__package__']
        self.log = logging.getLogger(name)
        self.log.info("Initializing tuya connector.")
        self.config = config

        # Init openapi and connect
        self.openapi = TuyaOpenAPI(API_ENDPOINT.format(config['REGION']), config['ACCESS_ID'], config['ACCESS_KEY'])
        response = self.openapi.connect()
        if response['success'] != True:
            self.log.error("Error connecting to tuya cloud, please check parameters.")
            self.log.info(response)
            exit(1)

    #detect_devices(openapi, config, filename):

    def get_uid(self, devuid):
        response = self.openapi.get("/v1.0/devices/{}".format(devuid), dict())
        if response['success'] == False:
            self.log.error("Error getting device " + devuid)
            self.log.info(response)
            exit(1)
        return response['result']['uid']

    def set_device(self, uid, name):
        found = False
        for dev in self.config['DEVICES']:
            if dev['uid'] == uid:
                dev['name'] = name
                found = True

        if found == False:
            self.config['DEVICES'].append({'uid' : uid, 'name' : name, 'domoticz_id' : '-1', 'domoticz_id_battery' : '-1'})

        return found == False

    def detect_devices(self):

        self.uid = self.get_uid(self.config['DEVICES'][0]['uid'])

        response = self.openapi.get("/v1.0/users/{}/devices".format(self.uid), dict())
        if response['success'] == False:
            self.log.error("Error getting devices ")
            self.log.info(response)
            exit(1)

        foundnew = False
        for d in response['result']:
            if self.set_device(d['uuid'], d['name']):
                foundnew = True

        if foundnew == False:
            self.log.info("Did not find new devices.")

    def onMessage(self, msg):
        self.devm.handle(msg)

    def run(self, devm):
        self.devm = devm
        self.open_pulsar = TuyaOpenPulsar(
            self.config['ACCESS_ID'],
            self.config['ACCESS_KEY'],
            MQ_ENDPOINT.format(self.config['REGION']
            ), TuyaCloudPulsarTopic.PROD
        )

        self.open_pulsar.add_message_listener(lambda msg: self.onMessage(msg))
        self.log.info("Starting pulsar listener.")
        self.open_pulsar.start()

    def stop(self):
        self.open_pulsar.stop()
        self.log.info("Pulsar listener stopped.")
