## Introduction

Python program that exposes different USB sticks through a TCP port.

## Features

The program has the following features:

- Detects plugged and unplugged USB sticks (udev)
- Opens a TCP port connected to the USB stick serial connection (socat)
- Announces the TCP connection to the rest of the network (mDNS)

The remote TCP connections can be limited to a single IP address making use of the "ALLOWED_IP" configuration parameter.

## Installation

wget https://raw.githubusercontent.com/Tknika/serial2tcp-gateway/master/install.sh

chmod +x install.sh

sudo ./install.sh

Follow the on-screen instructions and enjoy!
