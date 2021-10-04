import sys
import logging
from .t2d_device import t2d_device
import re
import json

class t2d_devman:
    config = {}
    devices = {}
    def __init__(self, config):
        name = vars(sys.modules[__name__])['__package__']
        self.log = logging.getLogger(name)
        self.config = config
        self.init_devices()

    def init_devices(self):
        for devcfg in self.config['DEVICES']:
            self.devices[devcfg['uid']] = t2d_device(devcfg, self.config['DOMOTICZ'])
        self.log.info("Devices initialized.")


    def handle(self, msg):
        msg = msg.strip()
        match = re.findall('.*?(\{.+\})', msg)
        if match:
            try:
                j = json.loads(match[0])
                if 'bizCode' in j.keys():
                    logger.debug("bizCode ignored.")
                elif 'devId' in j.keys():
                    uid = j['devId']
                    code = j['status'][0]['code']
                    value = j['status'][0]['value']

                    if self.devices[uid]:
                        self.devices[uid].handle_msg(code, value)
                    else:
                        print("device not found!")
                else:
                    print("Unknown sequence!")
                    print(match[0])

            except ValueError:
                print("Message decode error!")
                print("-------- starts here ----------")
                print(msg)
                print("--------- ends here -----------")
        else:
            print("Unknown message!")
            print(msg)
