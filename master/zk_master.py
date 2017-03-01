import json

from kazoo.client import KazooClient, KazooState
from kazoo.protocol.states import EventType
from kazoo.recipe.watchers import DataWatch

from logger import logger
from master.settings import ZOOKEEPER_HOST, ZOOKEEPER_PORT


class MasterZkClient(object):
    def __init__(self):
        host='{}:{}'.format(ZOOKEEPER_HOST, ZOOKEEPER_PORT)
        zk = KazooClient(host)
        zk.add_listener(self.conn_listener)
        self.zk = zk
        self.on_available_droid = ChildrenWatch(
            zk,
            '/droids/available',
            self.on_available_droid,
        )

    def setup(self):
        self.zk.ensure_path('/droids/available')
        self.zk.ensure_path('/droids/assigned')

    @staticmethod
    def conn_listener(state):
        if state == KazooState.CONNECTED:
            logger.debug('connected...')
        elif state == KazooState.LOST:
            logger.debug('connection lost...')
        elif state == KazooState.SUSPENDED:
            logger.debug('connection suspended...')


    def on_available_droid(self, children):
        logger.debug('Registering watches on available droids')
        for child in children:
            child_p = '/droids/available/{}'.format(child)
            DataWatch(self.zk, child_p, self.handle_dropped_droid)


    def handle_dropped_droid(self, data, stat, event):
        if event:
            if event.type == EventType.CREATED:
                # Implies a new droid became available
                logger.debug('WooHoo! Another droid joins our ranks!')
            elif event.type == EventType.DELETED:
                # Implies an existing droid was disconnected
                # Check if it was assigned and remove it from there.
                node_name = event.path.rsplit('/', 1)[1]
                assigned_emulators = self.zk.get_children('/droids/assigned')
                if node_name in assigned_emulators:
                    # Check if droid was being assigned, by comparing creation
                    # times.
                    assigned_p = '/droids/assigned/{}'.format(node_name)
                    adata, astat = self.zk.get(assigned_p)
                    import ipdb; ipdb.set_trace()
                    logger.error('Oh no, droid-{} was lost'.format(node_name))
                    self.zk.delete(assigned_p)
            else:
                logger.debug('These are not the events you are looking for.')

    def assign_droid(self, user):
        available_droids = self.zk.get_children('/droids/available')
        if not available_droids:
            logger.error('No droids available')
            return False
        child = available_droids[0]
        child_p = '/droids/available/{}'.format(child)
        data, stat = self.zk.get(child_p)
        data = json.loads(data)
        transaction = self.zk.transaction()
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
    from twisted.internet import reactor

    reactor.addSystemEventTrigger('before', 'shutdown', lambda: zk.stop())
    reactor.run()
