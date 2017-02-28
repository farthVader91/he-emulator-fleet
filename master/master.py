import json

from kazoo.client import KazooClient, KazooState
from kazoo.protocol.states import EventType
from kazoo.recipe.watchers import DataWatch
from twisted.internet import reactor

from logger import logger

zk = KazooClient()


def init_nodes():
    zk.ensure_path('/droids/available')
    zk.ensure_path('/droids/synchronize')
    zk.ensure_path('/droids/synchronized')
    zk.ensure_path('/droids/assigned')


def conn_listener(state):
    if state == KazooState.CONNECTED:
        logger.debug('connected...')
    elif state == KazooState.LOST:
        logger.debug('connection lost...')
    elif state == KazooState.SUSPENDED:
        logger.debug('connection suspended...')


@zk.ChildrenWatch('/droids/available')
def on_available_droid(children):
    logger.debug('Registering watches on available droids')
    for child in children:
        child_p = '/droids/available/{}'.format(child)
        DataWatch(zk, child_p, handle_dropped_droid)


def handle_dropped_droid(data, stat, event):
    if event:
        if event.type == EventType.CREATED:
            # Implies a new emulator became available
            logger.debug('WooHoo! Another droid joins our ranks!')
        elif event.type == EventType.DELETED:
            # Implies an existing emulator was disconnected
            # Check if it was assigned and remove it from there.
            node_name = event.path.rsplit('/', 1)[1]
            assigned_emulators = zk.get_children('/droids/assigned')
            if node_name in assigned_emulators:
                logger.error('Oh no, droid-{} was lost'.format(node_name))
                assigned_p = '/droids/assigned/{}'.format(node_name)
                zk.delete(assigned_p)
        else:
            logger.debug('These are not the events you are looking for.')


def synchronize_droid(droid_name, apks=None):
    zk.create('/droids/synchronize/{}'.format(droid_name),
              value=json.dumps({
                  'installed_apks': apks or [],
              }))


def assign_droid(user):
    available_droids = zk.get_children('/droids/available')
    if not available_droids:
        logger.error('No droids available')
        return False
    child = available_droids[0]
    child_p = '/droids/available/{}'.format(child)
    data, stat = zk.get(child_p)
    data = json.loads(data)
    transaction = zk.transaction()
    transaction.check(child_p, stat.version)
    transaction.delete(child_p)
    data['user'] = user
    transaction.create(
        '/droids/assigned/{}'.format(child),
        value=json.dumps(data),
    )
    transaction.commit()
    return True


if __name__ == '__main__':
    zk.start()
    init_nodes()
    reactor.addSystemEventTrigger('before', 'shutdown', lambda: zk.stop())
    reactor.run()
