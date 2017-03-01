import json
import random

from kazoo.client import KazooClient, KazooState
from kazoo.exceptions import NoNodeError
from kazoo.protocol.states import EventType
from kazoo.recipe.watchers import ChildrenWatch, DataWatch

from logger import logger
from common_settings import ZK_HOST, ZK_PORT
from worker.thrift_client import DroidClient


class MasterZkClient(object):
    def __init__(self):
        host = '{}:{}'.format(ZK_HOST, ZK_PORT)
        zk = KazooClient(host)
        zk.add_listener(self.conn_listener)
        self.zk = zk

    def setup(self):
        logger.debug('Setting up directories and nodes')
        self.zk.start()
        self.zk.ensure_path('/droids/running')
        self.zk.ensure_path('/droids/free')
        self.zk.ensure_path('/droids/assigned')

        # Register watches
        self.on_running_droid = ChildrenWatch(
            self.zk,
            '/droids/running',
            self.on_running_droid,
            send_event=True
        )
        self.on_assigned_droid = ChildrenWatch(
            self.zk,
            '/droids/assigned',
            self.on_assigned_droid,
        )

    @staticmethod
    def conn_listener(state):
        if state == KazooState.CONNECTED:
            logger.debug('connected...')
        elif state == KazooState.LOST:
            logger.debug('connection lost...')
        elif state == KazooState.SUSPENDED:
            logger.debug('connection suspended...')

    def on_running_droid(self, children, event):
        if not event:
            return
        logger.debug('Registering watches on running droids')
        assigned_droids = self.zk.get_children('/droids/assigned')
        free_doids = set(children) - set(assigned_droids)
        for droid in free_doids:
            # Implies a new droid became available
            logger.debug('WooHoo! Another droid joins our ranks!')
            # Create corresponding node in /droids/free
            free_p = '/droids/free/{}'.format(droid)
            self.zk.ensure_path(free_p)
            droid_p = '/droids/running/{}'.format(droid)
            DataWatch(self.zk, droid_p, self.on_running_droid_change)

    def on_running_droid_change(self, data, stat, event):
        if event:
            node_name = event.path.rsplit('/', 1)[1]
            if event.type == EventType.DELETED:
                # Implies an existing droid was disconnected
                # Attempt to drop it from running/assigned
                try:
                    free_p = '/droids/free/{}'.format(node_name)
                    self.zk.delete(free_p)
                except NoNodeError:
                    logger.debug('{} was not free'.format(node_name))
                try:
                    assigned_p = '/droids/assigned/{}'.format(node_name)
                    self.zk.delete(assigned_p)
                except NoNodeError:
                    logger.debug('{} was not assigned'.format(node_name))
            else:
                logger.debug('These are not the events you are looking for.')

    def assign_droid(self, user):
        free_droids = self.zk.get_children('/droids/free')
        if not free_droids:
            logger.error('No free droids')
            return False
        child = free_droids[0]
        child_p = '/droids/free/{}'.format(child)
        _, stat = self.zk.get(child_p)
        transaction = self.zk.transaction()
        transaction.check(child_p, stat.version)
        transaction.delete(child_p)
        transaction.create(
            '/droids/assigned/{}'.format(child),
            value=user,
        )
        transaction.commit()
        return True

    def get_droid(self, droid):
        data, _ = self.zk.get('/droids/running/{}'.format(droid))
        cpar = json.loads(data)
        return DroidClient(cpar['thrift_host'], int(cpar['thrift_port']))

    def get_arbitrary_droid_name(self):
        children = self.zk.get_children('/droids/running')
        return random.choice(children)

    def get_arbitrary_droid(self):
        try:
            droid_name = self.get_arbitrary_droid_name()
            return self.get_droid(droid_name)
        except IndexError:
            return None

    def get_droid_for_user(self, user):
        for child in self.zk.get_children('/droids/assigned'):
            data, _ = self.zk.get('/droids/assigned/{}'.format(child))
            if data == user:
                return self.get_droid(child)
        return None

    def release_droid(self, droid):
        data, stat = self.zk.get('/droids/running/{}'.format(droid))
        t = self.zk.transaction()
        t.check('/droids/running/{}'.format(droid), stat.version)
        t.delete('/droids/assigned/{}'.format(droid))
        t.create('/droids/free/{}'.format(droid))
        t.commit()

    def on_assigned_droid(self, children):
        logger.debug('Registering watches on assigned droids')
        for child in children:
            child_p = '/droids/assigned/{}'.format(child)
            DataWatch(self.zk, child_p, self.on_assigned_droid_change)
            logger.debug('Assigned {}'.format(child))

    def on_assigned_droid_change(self, data, stat, event):
        if event:
            node_name = event.path.rsplit('/', 1)[1]
            if event.type == EventType.DELETED:
                # Check if droid was lost or freed.
                if self.zk.exists('/droids/running/{}'.format(node_name)):
                    logger.debug('Droid ({}) was released'.format(node_name))
                    return
                logger.error(
                    'Uh-oh! An assigned droid ({}) was lost!'.format(
                        node_name))
                logger.error(
                    'Accomodate user ({}) with a new droid'.format(data))
            else:
                logger.debug('These are not the events you are looking for.')

    def teardown(self):
        logger.debug('Tearing down ZkMaster')
        self.zk.stop()


if __name__ == '__main__':
    m = MasterZkClient()
    m.setup()
    from twisted.internet import reactor

    reactor.addSystemEventTrigger('before', 'shutdown', m.teardown)
    reactor.run()
