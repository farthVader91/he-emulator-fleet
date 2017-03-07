import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAR_DIR = os.path.join(ROOT_DIR, 'var')
CONFIG_PATH = os.path.join(ROOT_DIR, 'droid_config.json')

ZK_HOST = "localhost"
ZK_PORT = "2181"
