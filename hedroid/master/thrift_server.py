import atexit

from hedroid.logger import logger
from hedroid.master.settings import THRIFT_HOST, THRIFT_PORT
from hedroid.master.zk_master import MasterZkClient

from hedroid.master.tgen.droid_keeper.ttypes import ConnParams, ApplicationException
from hedroid.master.tgen.droid_keeper import DroidKeeper

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
            exc.msg = str(err)
            if hasattr(err, 'msg'):
                exc.msg = err.msg
            raise exc

    def get_endpoint_for_user(self, user):
        logger.debug(
            'Getting endpoint for user - {}'.format(user)
        )
        droid_name = self.zk_client.get_droid_name_for_user(user)
        if droid_name is None:
            if not self.zk_client.assign_droid(user):
                logger.debug('No droids available')
                ae = ApplicationException()
                ae.msg = 'No droids available'
                raise ae
        droid_name = self.zk_client.get_droid_name_for_user(user)
        droid = self.zk_client.get_droid(droid_name)
        # Get conn params
        endpoint_cpars = droid.get_endpoint(droid_name)
        cpars = ConnParams()
        cpars.host = endpoint_cpars.host
        cpars.port = endpoint_cpars.port
        cpars.password = endpoint_cpars.password
        return cpars

    def interact_with_endpoint(self, dr):
        logger.debug(
            'Interacting with user({}) endpoint'.format(dr.user)
        )
        droid_name = self.zk_client.get_droid_name_for_user(dr.user)
        if droid_name is None:
            msg = 'No droid assigned for user({})'.format(dr.user)
            logger.error(msg)
            ae = ApplicationException()
            ae.msg = msg
            raise ae
        droid = self.zk_client.get_droid(droid_name)
        # If operation is specified, check if it is to start a package
        try:
            return droid.run_operation(droid_name, dr.op, dr.apk_url)
        except Exception as err:
            exc = ApplicationException()
            exc.msg = str(err)
            if hasattr(err, 'msg'):
                exc.msg = err.msg
            raise exc
        return True

    def release_endpoint_for_user(self, user):
        logger.debug(
            'Releasing endpoint for user - {}'.format(user)
        )
        droid_name = self.zk_client.get_droid_name_for_user(user)
        if droid_name is None:
            logger.debug('No droid assigned to this user')
            return
        self.zk_client.release_droid(droid_name)
        logger.debug('Released droid for user - {}'.format(user))

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
