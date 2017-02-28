import json
import socket


def is_open_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('127.0.0.1', port))
    return result != 0  # Implies port is being used


def get_public_hostname():
    hostname = ''
    resp = requests.get("http://169.254.169.254/latest/meta-data/public-host")
    if resp.status == 200:
        hostname = resp.text
    else:
        hostname = socket.gethostname()

    return hostname

def get_hostname():
    return socket.gethostname()


def build_config(emulator):
    return {
        'hostname': get_hostname(),
        'adb_port': emulator.port,
        'ws_port': 'n/a',
        'vnc_port': 'n/a',
    }


def read_config():
    config_path = 


if __name__ == '__main__':
    print is_open_port(5672)
