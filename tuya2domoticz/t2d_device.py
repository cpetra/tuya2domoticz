import sys
import logging
import requests
import urllib.request
from datetime import datetime
import time
import json
import re

class t2d_device:
    config = {}
    domoticzip = ""
    def __init__(self, config, domoticzip):
        self.config = config
        self.domoticzip = domoticzip
        name = vars(sys.modules[__name__])['__package__']
        self.log = logging.getLogger(name)
        self.log.info(config)


    def handle_msg(self, code, value):
        t = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if code == 'watersensor_state':
            ret = self.send_alert_water_leakage(value)
        elif code == 'battery_state':
            ret = self.send_alert_battery(value)
        else:
            # although this is not validated, it might work.
            ret = self.send_alert_generic(value)

        self.log.info("{}: uid: {}, code: {}, value: {}, sent status: {}".format(t, self.config['uid'], code, value, ret))

    def send_domoticz(self, url):
        try:
            request = urllib.request.urlopen(url)
            r = str(request.read())
            r = r.replace("\\n", "")
            r = r.replace("\\t", "")
            r = r.strip()
            match = re.findall('.*?(\{.+\})', r)
            if match:
                j = json.loads(match[0])
                return j['status']
        except ValueError:
            print("Error decoding result")
        except urllib.error.URLError:
            print("Error sending request")
        except urllib.error.HTTPError:
            print("Error communicating with server")

        return "Error"

    # Send generic alert (good for water_leakage, might work for others too)
    def send_alert_generic(self, value):
        did = self.config['domoticz_id']

        if int(did) < 0:
            print("Domoticz ID not set, bailout.")
            return

        if value == 'alarm':
            code = '4' # red
        elif value == 'normal':
            code = '1' # green
        else:
            code = '0' # gray

        url = 'http://{}/json.htm?type=command&param=udevice&idx={}&nvalue={}&svalue={}'.format(self.domoticzip, did, code, value)
        return self.send_domoticz(url)

    # Send water leakage alert
    def send_alert_water_leakage(self, value):
        return self.send_alert_generic(value)

    # Send Battery alert
    def send_alert_battery(self, value):
        did = self.config['domoticz_id_battery']
        if int(didb) < 0:
            print("Domoticz battery ID not set, bailout.")
            return
        if value == 'high':
            code = '1' # green
        elif value == 'low':
            code = '4' # red
        else:
            code = '2' # yellow

        url = 'http://{}/json.htm?type=command&param=udevice&idx={}&nvalue={}&svalue={}'.format(self.domoticzip, didb, code, value)
        return self.send_domoticz(url)
