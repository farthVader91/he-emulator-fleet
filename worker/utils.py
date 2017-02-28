from copy import deepcopy
import json
import os
import socket

import requests
from requests.exceptions import ConnectTimeout

from settings import ROOT_DIR


def is_open_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('127.0.0.1', port))
    return result != 0  # Implies port is being used


class CachedGlobals:
    HOSTNAME = None
    CONFIG = None


def get_public_hostname():
    if CachedGlobals.HOSTNAME is None:
        try:
            resp = requests.get("http://169.254.169.254/latest/meta-data/public-host",
                                timeout=(3, 2))
            if resp.status == 200:
                CachedGlobals.HOSTNAME = resp.text
        except ConnectTimeout:
            CachedGlobals.HOSTNAME = socket.gethostname()

    return CachedGlobals.HOSTNAME


def get_config():
    if CachedGlobals.CONFIG is None:
        config_path = os.path.join(ROOT_DIR, 'worker',  'config.json')
        assert os.path.exists(config_path), "Config file not provided for worker"
        with open(config_path) as source:
            CachedGlobals.CONFIG = json.load(source)

    return deepcopy(CachedGlobals.CONFIG)


if __name__ == '__main__':
    print is_open_port(5672)
