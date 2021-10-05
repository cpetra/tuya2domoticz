import json
import os
import sys
import logging
import logging.handlers
import signal
import time
from optparse import OptionParser
from .t2d_devman import t2d_devman
from .t2dconnector import t2dconnector
try:
    import daemon
    from daemon import pidfile
except ImportError:
    daemon = None

# Main class
# 
class tuya2domoticz:
    config = {}
    refresh_devices = False
    filename = "config.json"


    def __init__(self, refresh_devices=False, config_file="config.json"):
        self.filename = config_file
        name = vars(sys.modules[__name__])['__package__']
        self.log = logging.getLogger(name)
        self.log.info("Started, using config file: {}".format(config_file))
        if self.load_config() == False:
            self.refresh_devices = True
            self.create_config()

        self.t2d = t2dconnector(self.config)
        if refresh_devices:
            self.t2d.detect_devices()
            self.set_domoticz_ids()
            self.write_config()

    def run(self, devm):
        self.t2d.run(devm)

    def stop(self):
        self.t2d.stop()

    def load_config(self):
        if os.path.exists(self.filename):
            with open(self.filename) as f:
                self.config = json.load(f)
            self.log.info("Config loaded.")
            return True
        return False

    def write_config(self):
        with open(self.filename, 'w') as f:
            json.dump(self.config, f, indent=4)
        ("Config file written.")

    def do_input(self, str, empty=False):
        plat = sys.platform
        if plat == 'win32':
            val = input(str)
        else:
            BOLD = '\033[1m'
            END = '\033[0m'
            BLUE = '\033[94m'
            val = input(BOLD + BLUE + str + END)
        if empty == False and val == "" :
            print("Cannot have empty configuration values")
            exit(1)
        return val

    def set_domoticz_ids(self):
        for dev in self.config['DEVICES']:
            if dev['domoticz_id'] == '-1':
                did = self.do_input("domoticz ID for \"" + dev['name'] + "\" (uid: " + dev['uid'] + "): ")
                dev['domoticz_id'] = did 
            if dev['domoticz_id_battery'] == '-1':
                didb = self.do_input("domoticz battery ID for \"" + dev['name'] + "\" (uid: " + dev['uid'] + "): ")
                dev['domoticz_id_battery'] = didb

    def create_config(self):
        print("Please configure the following parameters:")
        access_id = self.do_input("ACCESS_ID: ")
        access_key = self.do_input("ACCESS_KEY: ")
        first_device = self.do_input("First device UID: ")
        region = self.do_input("Region (us, eu, cn): ")
        domoticz = self.do_input("domoticz (IP:PORT): ")

        self.config['DOMOTICZ'] = domoticz
        self.config['ACCESS_ID'] = access_id
        self.config['ACCESS_KEY'] = access_key
        self.config['REGION'] = region
        self.config['DEVICES'] = []
        self.config['DEVICES'].append({'uid' : first_device, 'name' : "yet unknown", 'domoticz_id' : '-1', 'domoticz_id_battery' : '-1'})
        self.write_config()
        refresh_devices = True

def parse_command_line():
    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config",
                  help="Use THIS config file", metavar="FILE", default="config.json")

    parser.add_option("-r", "--refresh", dest="refresh", action="store_true",
                  help="Refresh devices configuration", default=False)

    parser.add_option("-d", "--daemon", dest="daemon", action="store_true",
                  help="Run as daemon", default=False)

    parser.add_option("-i", "--install", dest="install", action="store_true",
                  help="Install as service", default=False)

    parser.add_option("-l", "--logfile", dest="logfile",
                  help="Use THIS log file", metavar="FILE", default="")

    (options, args) = parser.parse_args()
    return vars(options)

def setup_logging(logfile=""):
    logger = logging.getLogger("tuya2domoticz")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    if logfile != "":
        handler = logging.handlers.WatchedFileHandler(logfile)
    else:
        handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

got_sigterm = False
def on_signal(sig, frame):
    global got_sigterm
    log = logging.getLogger("tuya2domoticz")
    log.info("got SIGTERM")
    got_sigterm = True

def runme(refresh_devices, config_file, is_daemon=False):
    global got_sigterm
    t2d = tuya2domoticz(refresh_devices=refresh_devices, config_file=config_file)
    devm = t2d_devman(t2d.config)
    signal.signal(signal.SIGTERM, on_signal)

    t2d.run(devm)

    try:
        while got_sigterm == False:
            time.sleep(1)
    except KeyboardInterrupt:
        print('got CTRL+C')

    t2d.stop()
    exit(0)

from lockfile.pidlockfile import PIDLockFile

def start_daemon(config_file):
    name = vars(sys.modules[__name__])['__package__']
    rundir = "/var/lib/{}".format(name)
    pid_file = "{}/{}.pid".format(rundir, name)
    logfile = "{}/{}.log".format(rundir, name)
    print("Starting daemon.")
    
    with daemon.DaemonContext(
        working_directory=rundir,
        umask=0o002,
        pidfile=pidfile.TimeoutPIDLockFile(pid_file),
        ) as context:
        setup_logging(logfile)
        runme(refresh_devices=False, config_file=config_file, is_daemon=True)

# must be done as root
# won't work on raspberry pi
# Verified on Ubuntu
def install_initd_service():
    import pkg_resources
    name = vars(sys.modules[__name__])['__package__']
    path = pkg_resources.resource_filename(__name__, "conf/" + name + ".initd")
    print(path) 
    dst = "/etc/init.d/" + name
    rundir = "/var/lib/{}".format(name)
    os.system("mkdir -p {}".format(rundir))
    os.system("cp {} {}".format(path, dst))
    os.system('systemctl daemon-reload')
    os.system('systemctl enable {}'.format(name))
    os.system("service {} start".format(name))
    os.system("cp {} {}".format("config.json", rundir))

# OK for raspberry pi
def install_systemd_service():
    import pkg_resources
    name = vars(sys.modules[__name__])['__package__']
    path = pkg_resources.resource_filename(__name__, "conf/" + name + ".service")
    dst = os.path.expanduser('~') + "/.config/systemd/user"
    workdir = os.path.expanduser('~') + "/" + name;
    os.system("mkdir -p {}".format(dst))
    os.system("cp {} {}".format(path, dst))
    os.system("cp {} {}".format("config.json", workdir))
    os.system('systemctl --user daemon-reload')
    os.system('systemctl --user enable {}'.format(name))

def main():
    options = parse_command_line()
    if (options['install']):
        # install_initd_service()
        install_systemd_service()
        exit(0)
    if (options['daemon'] and daemon != None):
        start_daemon(config_file=options['config'])
    else:
        setup_logging(options['logfile'])
        runme(refresh_devices=options['refresh'], config_file=options['config'])

if __name__ == "__main__":
    main()
