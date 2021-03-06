from contextlib import contextmanager

from hedroid.logger import logger

from hedroid.master.tgen.droid_keeper import DroidKeeper
from hedroid.master.tgen.droid_keeper.ttypes import DroidRequest

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


class DroidKeeperClient(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port

    @contextmanager
    def transport(self):
        transport = TSocket.TSocket(self.host, self.port)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        self.client = DroidKeeper.Client(protocol)
        logger.debug('opening connection')
        transport.open()
        try:
            yield
        finally:
            logger.debug('closing connection')
            transport.close()
            self.client = None

    def ping(self):
        with self.transport():
            return self.client.ping()

    def get_package_name(self, apk_url):
        with self.transport():
            return self.client.get_package_name(apk_url)

    def get_endpoint_for_user(self, user):
        with self.transport():
            return self.client.get_endpoint_for_user(user)

    def interact_with_endpoint(self, user, op, apk_url=None):
        dr = DroidRequest()
        dr.user = user
        dr.op = op
        if apk_url:
            dr.apk_url = apk_url
        with self.transport():
            return self.client.interact_with_endpoint(dr)

    def release_endpoint_for_user(self, user):
        with self.transport():
            return self.client.release_endpoint_for_user(user)
