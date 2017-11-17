#!/usr/bin/env python

import serial
import threading
import subprocess
import logging

logger = logging.getLogger('socat2tcp')


class Socat2TCP(object):
    def __init__(self, serial_port, baudrate=115200, tcp_listen="0.0.0.0", tcp_port=5555, allowed_ip=None):
        self.serial_port = serial_port
        self.serial_baudrate = baudrate
        self.tcp_listen = tcp_listen
        self.tcp_port = tcp_port
        self.allowed_ip = allowed_ip
        self.serial_connection = None
        self.socket_connection = None
        self.remote_connection = None
        self.redirector = None
        self.socket_listener = None
        self.process_id = None

    def start(self):
        range = ""
        if self.allowed_ip:
            range = ",range={}/0".format(self.allowed_ip)
        command = "/usr/bin/socat tcp-l:{0},reuseaddr,fork{1} file:{2},raw,nonblock,echo=0".format(
            self.tcp_port, range, self.serial_port)
        try:
            result = subprocess.Popen(command.split(" "))
        except Exception as e:
            logger.error("Error starting the Socat2TCP bridge: {}".format(e))
            return

        self.process_id = result.pid
        logger.debug("Socat2TCP Bridge started at port '{}'".format(self.tcp_port))

    def stop(self):
        command = "/bin/kill -9 {}".format(self.process_id)
        try:
            result = subprocess.Popen(command.split(" "))
        except Exception as e:
            logger.error("Error stopping the Socat2TCP bridge: {}".format(e))

        logger.debug("Socat2TCP Bridge stopped")
