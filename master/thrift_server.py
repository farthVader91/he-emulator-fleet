import atexit

from logger import logger
from master.settings import THRIFT_HOST, THRIFT_PORT
from master.zk_master import MasterZkClient

from master.tgen.droid_keeper.ttypes import ConnParams
from master.tgen.droid_keeper import DroidKeeper

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer


class DroidKeeperHandler(object):
    def __init__(self):
        self.zk_client = MasterZkClient()

    def setup(self):
        logger.debug('Setting up droid keeper')
        self.zk_client.setup()

    def ping(self):
        logger.debug('Ping!')

    def get_package_name(self, apk_url):
        logger.debug(
            'Getting package name for {}'.format(apk_url))
        return "com.blah.meh"

    def get_endpoint(self, user):
        logger.debug(
            'Getting endpoint for user - {}'.format(user)
        )
        cpars = ConnParams()
        cpars.host = 'localhost'
        cpars.port = '9090'
        return cpars

    def teardown(self):
        logger.debug('Tearing down DroidKeeper')
        self.zk_client.teardown()


def start_server():
    handler = DroidKeeperHandler()
    handler.setup()
    atexit.register(handler.teardown)
    processor = DroidKeeper.Processor(handler)
    transport = TSocket.TServerSocket(
        host=THRIFT_HOST,
        port=THRIFT_PORT)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    server.serve()


if __name__ == '__main__':
    start_server()
