#!/usr/bin/env python3

import pyudev
import signal
import logging
import sys
import json
import os
from socat2tcp import Socat2TCP
from mdns_advertiser import MDNSAdvertiser
from device_definitions import devices as registered_devices

logging.basicConfig(format='%(asctime)s %(levelname)-8s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

threads = {}

context = pyudev.Context()


def usb_stick_event(action, device):
    for rd in registered_devices:
        if device.get("ID_MODEL") == rd.get("ID_MODEL") and device.get("ID_VENDOR") == rd.get("ID_VENDOR"):
            if action == "add":
                logger.info("Device '{}' added".format(rd.get("NAME")))
                s2tcp = Socat2TCP(device.get("DEVNAME"), tcp_port=rd.get("PORT"), allowed_ip=ALLOWED_IP)
                s2tcp.start()
                properties = {"friendly-name": FRIENDLY_NAME,
                              "device-name": rd.get("NAME")}
                advert = MDNSAdvertiser("_{}2tcp".format(rd.get("CATEGORY")), "{}2TCP ({})".format(rd.get("CATEGORY"), FRIENDLY_NAME),
                                        rd.get("PORT"), properties, None, INTERFACE)
                advert.start()
                threads[device.get("DEVNAME")] = [s2tcp, advert]
            elif action == "remove":
                logger.info("Device '{}' removed".format(rd.get("NAME")))
                for t in threads[device.get("DEVNAME")]:
                    t.stop()
                del threads[device.get("DEVNAME")]


def load_configuration(config_file=None):
    if not config_file:
        config_file = "{}/{}".format(os.path.dirname(os.path.realpath(__file__)), "configuration.json")

    try:
        with open(config_file) as f:
            config = json.load(f)
        return config
    except EnvironmentError as err:
        logger.error("[Configuration] No configuration file provided")
        sys.exit(1)
    except ValueError as err:
        logger.error("[Configuration] Syntax error in the configuration file")
        sys.exit(1)


def signal_handler(signal, frame):
    for device in threads.values():
        for thread in device:
            thread.stop()
    logger.info("Serial2TCP gateway program stopped")

if __name__ == "__main__":
    logger.info("Serial2TCP gateway program has started")

    config = load_configuration()

    FRIENDLY_NAME = config["FRIENDLY_NAME"]
    INTERFACE = config["INTERFACE"]
    ALLOWED_IP = config["ALLOWED_IP"]
    DEBUG = config["DEBUG"]

    if DEBUG:
        logging.getLogger().setLevel(logging.DEBUG)

    for device in context.list_devices(subsystem='tty'):
        usb_stick_event("add", device)

    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by('tty')

    usb_stick_observer = pyudev.MonitorObserver(monitor, usb_stick_event)

    usb_stick_observer.start()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.pause()
