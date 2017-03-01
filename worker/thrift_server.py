import atexit

from logger import logger
from worker.helpers import DroidCoordinator, DroidBuilder
from worker.utils import get_config, get_public_hostname
from worker.utils import get_package_name_from_url

from tgen.droid_service.ttypes import ConnParams
from tgen.droid_service import DroidService

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer


class DroidServiceHandler(object):
    def __init__(self):
        self.coordinator = DroidCoordinator()

    def setup(self):
        logger.debug('Setting up droids')
        config = get_config()
        builder = DroidBuilder()
        for droid in config['droids']:
            if droid['port']:
                builder.set_port(droid['port'])
            if droid['avd']:
                builder.set_avd(droid['avd'])
            self.coordinator.add_droid(builder.build())
        # Start all endpoints now
        self.coordinator.setup()

    def ping(self):
        logger.debug('Ping!')

    def get_package_name(self, apk_url):
        logger.debug("getting package name for apk {}".format(apk_url))
        return get_package_name_from_url(apk_url)

    def get_endpoint(self, endpoint_id):
        logger.debug("Getting endpoint for {}".format(endpoint_id))
        endpoint = self.coordinator.get_droid(endpoint_id)
        cp = ConnParams()
        cp.host = get_public_hostname()
        cp.port = endpoint.port
        return cp

    def install_apk(self, endpoint_id, apk_url):
        logger.debug("installing apk in {}".format(endpoint_id))
        return True

    def start_package(self, endpoint_id, package_name):
        logger.debug("Starting package {} for {}".format(package_name, endpoint_id))
        return True

    def pre_server_start_log(self):
        logger.debug("{} droid(s) at your service".format(
            self.coordinator.count()))

    def teardown(self):
        logger.debug("Running teardown operations")
        self.coordinator.teardown()


def start_server():
    handler = DroidServiceHandler()
    handler.setup()
    atexit.register(handler.teardown)
    processor = DroidService.Processor(handler)
    config = get_config()
    transport = TSocket.TServerSocket(
        host=config['thrift_host'],
        port=int(config['thrift_port']))
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    handler.pre_server_start_log()
    server.serve()

if __name__ == '__main__':
    start_server()