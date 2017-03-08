import re
import json
import os
import socket
from copy import deepcopy
from tempfile import NamedTemporaryFile

import requests
from requests.exceptions import ConnectTimeout
import subprocess32 as subprocess

from hedroid.common_settings import CONFIG_PATH, HOSTNAME
from hedroid.logger import logger


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
    pkg = get_package_name(download_to)
    # Remove temp file
    os.remove(download_to)
    return pkg


def parse_manifest(path):
    package, activity = None, None
    cmd = ["aapt", "dump", "badging", path]
    output = subprocess.check_output(
        cmd, timeout=5, universal_newlines=True)
    p1 = re.compile(r"^package: name='([\w\.]+)'")
    p2 = re.compile(r"^launchable-activity: name='([\w\.]+)'")
    for line in output.splitlines():
        if package and activity:
            return {
                'package': package,
                'activity': activity,
            }
        if package is None:
            m = p1.match(line)
            if m:
                package = m.group(1)
                logger.debug('Extracted package name {}'.format(package))
        if activity is None:
            m = p2.match(line)
            if m:
                activity = m.group(1)
                logger.debug('Extracted activity  {}'.format(activity))

    error = 'Unable to extract package name for file {}'.format(
        os.path.basename(path))
    raise Exception(error)


def get_package_name(path):
    return parse_manifest(path)['package']


def restart_adb_server():
    logger.debug('Restarting adb')
    try:
        subprocess.call(["adb", "kill-server"])
    finally:
        try:
            subprocess.call(["adb", "start-server"])
        except:
            pass


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
	if HOSTNAME is not None:
            CachedGlobals.HOSTNAME = HOSTNAME
	else:
            url = "http://169.254.169.254/latest/meta-data/public-host"
            try:
                resp = requests.get(url, timeout=(3, 2))
                if resp.status == 200:
                    CachedGlobals.HOSTNAME = resp.text
            except ConnectTimeout:
                CachedGlobals.HOSTNAME = socket.gethostname()

    return CachedGlobals.HOSTNAME


def get_config():
    if CachedGlobals.CONFIG is None:
        err = "Config file not provided for worker"
        assert os.path.exists(CONFIG_PATH), err
        with open(CONFIG_PATH) as source:
            CachedGlobals.CONFIG = json.load(source)

    return deepcopy(CachedGlobals.CONFIG)


if __name__ == '__main__':
    print is_open_port(5672)
