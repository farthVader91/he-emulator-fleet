import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAR_DIR = os.path.join(ROOT_DIR, 'var')
CONFIG_DIR = os.path.join(ROOT_DIR, 'config')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'droid_config.json')

# HOSTNAME = 'emulator.hackerearth.com'
HOSTNAME = 'localhost'

# ZK_HOST = "he-zookeeper-vpc.hackerearth.com"
ZK_HOST = "localhost"
ZK_PORT = "2181"

DEBUG = True
