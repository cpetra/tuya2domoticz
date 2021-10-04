# tuya2domoticz

This package is intended to be used as a standalone application (command line or daemon) for receiving
Pulsar asynchronous messages from TUYA sensor devices, and then passing those as alarm device messages to Domoticz using http requests.

This is NOT a Domoticz plugin!

For Domoticz, a tuya plugin is already implemented:
https://github.com/Xenomes/Domoticz-TUYA-Plugin

But it just handles switches and devices that are usually online, not battery sensors.
For me, that was not useable, I have reflashed all my Tuya devices with Tasmota (very easily), but for the actual sensors the reflashing is a painful and unguarranteed process. If reflashing is preferred, have a look at this:  
https://templates.blakadder.com/Y09.html

Currently, the only tested device is the Y09 WiFi water leakage sensor.

Home Assistant can also handle tuya devices through a tuya maintained plugin (tuya-home-assistant) but, for what I can tell, it just uses a polling mechanism with a big warning about the delay in use. The Domoticz-TUYA-Plugin apparently uses the same plugin to interface with Tuya.

## Pre-requisites
1. Pair the Tuya devices using the default SmartHome Application.

2. Create an account and a cloud project on http://iot.tuya.com.

3. Link the SmartHome app linked devices in the project (Devices -> Add Device -> Add Device with IOT Device Management App).

4. Configure the **Home** and **device** related service APIs.

5. Write down the ID and KEY for that project. One device UID is also required, as the "normal" device listing fails. 

## Installation
Using pip:
```bash
# Install tuya2domoticz
pip3 install tuya2domoticz
```

## Setup
1. Configure devices
The first run will help to configure the device. You will need to set up the ACCESS_ID, ACCESS_KEY, one of the registered devices UID (as reported from the tuya IOT project setup), Domoticz IP:PORT and then the device numbers for the Domoticz virtual devices. For each pyhisical device, there should be one a virtual alert device for the actual status, and one for the battery status. If the device battery status is not needed, it shall be set to "-2".

```bash
costa@tuf:~/work/python/tuya2domoticz$ python3 -m tuya2domoticz
2021-10-04 11:45:28,485 - tuya2domoticz - INFO - Started, using config file: config.json
Please configure the following parameters:
ACCESS_ID: zzzzzzzzzzzzzzzzzzzz
ACCESS_KEY: yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
First device UID: 05075255e098061ba2f6
Region (us, eu, cn): eu
domoticz (IP:PORT): 192.168.1.41:8080
2021-10-04 11:46:12,202 - tuya2domoticz - INFO - Initializing tuya connector.
domoticz ID for "Water leak sensor" (uid: 05075255e098061ba2f6): 38
domoticz battery ID for "Water leak sensor" (uid: 05075255e098061ba2f6): 40
domoticz ID for "Water leak sensor 2" (uid: 050752558caab55ab820): 39
domoticz battery ID for "Water leak sensor 2" (uid: 050752558caab55ab820): 41
2021-10-04 11:46:23,042 - tuya2domoticz - INFO - {'uid': '05075255e098061ba2f6', 'name': 'Water leak sensor', 'domoticz_id': '38', 'domoticz_id_battery': '40'}
2021-10-04 11:46:23,042 - tuya2domoticz - INFO - {'uid': '050752558caab55ab820', 'name': 'Water leak sensor 2', 'domoticz_id': '39', 'domoticz_id_battery': '41'}
2021-10-04 11:46:23,042 - tuya2domoticz - INFO - Devices initialized.
2021-10-04 11:46:23,042 - tuya2domoticz - INFO - Starting pulsar listener.
```

2. Install the module as service:
```bash
$ python3 -m tuya2domoticz -i
```

3. Start the service:
```bash
$ systemctl --user status tuya2domoticz
● tuya2domoticz.service - Tuya2domoticz Daemon
     Loaded: loaded (/home/costa/.config/systemd/user/tuya2domoticz.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2021-10-04 17:14:04 EEST; 2s ago
   Main PID: 90404 (python3)
     CGroup: /user.slice/user-1000.slice/user@1000.service/app.slice/tuya2domoticz.service
             └─90404 /usr/bin/python3 -m tuya2domoticz -c /home/costa/tuya2domoticz/config.json

oct 04 17:14:04 tuf systemd[999]: Started Tuya2domoticz Daemon.
oct 04 17:14:04 tuf python3[90404]: 2021-10-04 17:14:04,826 - tuya2domoticz - INFO - Started, using config file: /home/costa/tuya2domoticz/config.json
oct 04 17:14:04 tuf python3[90404]: 2021-10-04 17:14:04,826 - tuya2domoticz - INFO - Config loaded.
oct 04 17:14:04 tuf python3[90404]: 2021-10-04 17:14:04,826 - tuya2domoticz - INFO - Initializing tuya connector.
oct 04 17:14:05 tuf python3[90404]: 2021-10-04 17:14:05,009 - tuya2domoticz - INFO - {'uid': '05075255e098061ba2f6', 'name': 'Water leak sensor', 'domoticz_id': '38', 'domoticz_id_battery': '40'}
oct 04 17:14:05 tuf python3[90404]: 2021-10-04 17:14:05,009 - tuya2domoticz - INFO - {'uid': '050752558caab55ab820', 'name': 'Water leak sensor 2', 'domoticz_id': '39', 'domoticz_id_battery': '41'}
oct 04 17:14:05 tuf python3[90404]: 2021-10-04 17:14:05,009 - tuya2domoticz - INFO - Devices initialized.
oct 04 17:14:05 tuf python3[90404]: 2021-10-04 17:14:05,010 - tuya2domoticz - INFO - Starting pulsar listener.
```
