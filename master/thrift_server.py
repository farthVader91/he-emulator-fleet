import atexit

from logger import logger
from master.settings import THRIFT_HOST, THRIFT_PORT
from master.zk_master import MasterZkClient

from master.tgen.droid_keeper.ttypes import ConnParams, ApplicationException
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
        droid = self.zk_client.get_arbitrary_droid()
        if droid is None:
            exc = ApplicationException()
            exc.msg = 'No droids available'
            raise exc
        try:
            return droid.get_package_name(apk_url)
        except Exception as err:
            exc = ApplicationException()
            exc.msg = err.msg
            raise exc

    def get_endpoint_for_user(self, user):
        logger.debug(
            'Getting endpoint for user - {}'.format(user)
        )
        droid = self.zk_client.get_droid_for_user(user)
        if droid is None:
            self.zk_client.assign_droid(user)
        droid = self.zk_client.get_droid_for_user(user)
        endpoint_cpars = droid.get_endpoint()
        cpars = ConnParams()
        cpars.host = endpoint_cpars.host
        cpars.port = endpoint_cpars.port
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
