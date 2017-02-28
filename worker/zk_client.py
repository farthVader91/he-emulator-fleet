import json
import os

from kazoo.client import KazooClient, KazooState
from kazoo.protocol.states import EventType

from logger import logger
from worker.emulator import Emulator
from worker.utils import get_config, get_public_hostname


def conn_listener(state):
    if state == KazooState.CONNECTED:
        logger.debug('connected...')
    elif state == KazooState.LOST:
        logger.debug('connection lost...')
    elif state == KazooState.SUSPENDED:
        logger.debug('connection suspended...')


class DroidZkClient(object):
    def __init__(self, nodename):
        self.nodename = nodename

        config = get_config()
        host='{}:{}'.format(config['zk_host'], config['zk_port'])
        zk = KazooClient(host)
        zk.add_listener(conn_listener)
        self.zk = zk

    def setup(self):
        logger.debug('Registering onto zookeeper')
        self.zk.start()
        config = get_config()
        value = {
            'thrift_host': get_public_hostname(),
            'thrift_port': config['thrift_port'],
        }
        self.zk.create('/droids/available/{}'.format(self.nodename),
                        value=json.dumps(value),
                        makepath=True, ephemeral=True)

    def teardown(self):
        self.zk.stop()


if __name__ == '__main__':
    c = DroidZkClient('droid1')
    c.setup()
    from twisted.internet import reactor
    
    reactor.addSystemEventTrigger('before', 'shutdown', c.teardown)
    reactor.run()
