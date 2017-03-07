from contextlib import contextmanager

from hedroid.logger import logger

from hedroid.worker.tgen.droid_service import DroidService

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


class DroidClient(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.client = None

    @contextmanager
    def transport(self):
        transport = TSocket.TSocket(self.host, self.port)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        self.client = DroidService.Client(protocol)
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
            self.client.ping()

    def get_package_name(self, apk_url):
        with self.transport():
            return self.client.get_package_name(apk_url)

    def get_endpoint(self, endpoint_id):
        with self.transport():
            return self.client.get_endpoint(endpoint_id)

    def run_operation(self, endpoint_id, operation, apk_url):
        with self.transport():
            return self.client.run_operation(
                    endpoint_id, operation, apk_url)
