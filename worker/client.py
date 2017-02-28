import json
import os

from kazoo.client import KazooClient, KazooState
from kazoo.protocol.states import EventType
from twisted.internet import reactor

from emulator import Emulator
from logger import logger
from utils import build_config


NODENAME = os.environ.get('EMU_NODE', 'droid1')
zk = KazooClient()
em = Emulator()


def initialize():
    em.start()
    zk.create('/droids/available/{}'.format(NODENAME),
              value=json.dumps(build_config(em)),
              makepath=True, ephemeral=True)


def conn_listener(state):
    if state == KazooState.CONNECTED:
        logger.debug('connected...')
    elif state == KazooState.LOST:
        logger.debug('connection lost...')
    elif state == KazooState.SUSPENDED:
        logger.debug('connection suspended...')


@zk.DataWatch('/droids/synchronize/{}'.format(NODENAME))
def on_sync(data, stat, event):
    if event:
        if event.type in [EventType.CREATED, EventType.CHANGED]:
            logger.log('Synchronizing state')
            data = json.loads(data)
            for apk in data['installed_apks']:
                em.load_apk(apk)
            # Set node in synchronized
            path = '/droids/synchronized/{}'.format(NODENAME)
            if zk.exists(path):
                zk.set(path, data)
            else:
                zk.create(path, value=data, ephemeral=True)


def cleanup():
    zk.stop()
    em.stop()


zk.add_listener(conn_listener)


if __name__ == '__main__':
    zk.start()
    initialize()
    reactor.addSystemEventTrigger('before', 'shutdown', cleanup)
    reactor.run()
