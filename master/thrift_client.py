from contextlib import contextmanager

from master.tgen.droid_keeper import DroidKeeper

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
        transport.open()
        yield
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
