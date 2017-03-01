import re
import json
import os
import socket
from copy import deepcopy
from tempfile import NamedTemporaryFile

import requests
from mirakuru import SimpleExecutor
from requests.exceptions import ConnectTimeout

from settings import ROOT_DIR
from logger import logger


def get_temp_apk_path():
    nf = NamedTemporaryFile(suffix='.apk', delete=True)
    nf.close()
    return nf.name


def download_to(url, target_p):
    resp = requests.get(url, stream=True)
    SIZE_4MB = 4 << 20
    with open(target_p, 'wb') as target:
        for chunk in resp.iter_content(SIZE_4MB):
            target.write(chunk)
    return target_p


def download_to_temp(url):
    target_p = get_temp_apk_path()
    return download_to(url, target_p)


def get_package_name_from_url(apk_url):
    download_to = download_to_temp(apk_url)
    return get_package_name(download_to)


def get_package_name(path):
    cmd = ["aapt", "dump", "badging", path]
    proc = SimpleExecutor(cmd)
    proc.start()
    p = re.compile(r"^package: name='([\w\.]+)'")
    for line in proc.output():
        m = p.match(line)
        if m:
            pkg = m.group(1)
            logger.debug('Extracted package name {}'.format(pkg))
            return pkg
    error = 'Unable to extract package name for file {}'.format(
        os.path.basename(path))
    raise Exception(error)


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
