from logger import logger
from worker.factory import EndpointFactory
from worker.helpers import EndpointCoordinator, EndpointBuilder
from worker.utils import read_config

from tgen.droid_service.ttypes import ConnParams
from tgen.droid_service import DroidService

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer


class DroidServiceHandler(object):
    def __init__(self):
        self.coordinator = EndpointCoordinator()

    def setup(self):
        logger.debug('Setting up droids')
        config = read_config()
        builder = EndpointBuilder()
        for droid in config['droids']:
            if droid['port']:
                builder.set_port(droid['port'])
            if droid['avd']:
                builder.set_avd(droid['avd'])
            self.coordinator.set_endpoint(droid['name'], builder.build())
        # Start all instances now
        self.coordinator.start_all_instances()

    def ping(self):
        logger.debug('Ping!')

    def get_package_name(apk_url):
        logger.debug("getting package name for apk {}".format(apk_url))
        return "some random package"

    def get_endpoint(endpoint_id):
        logger.debug("Getting endpoint for {}".format(endpoint_id))
        cp = ConnParams()
        cp.host = 'deathstart'
        cp.port = 54321
        return cp

    def install_apk(endpoint_id, apk_url):
        logger.debug("installing apk in {}".format(endpoint_id))
        return True

    def start_package(endpoint_id, package_name):
        logger.debug("Starting package {} for {}".format(package_name, endpoint_id))
        return True

    def pre_server_start_log(self):
        logger.debug("{} droid(s) at your service".format(
            self.coordinator.get_num_endpoints()))


def start_server():
    handler = DroidServiceHandler()
    handler.setup()
    processor = DroidService.Processor(handler)
    transport = TSocket.TServerSocket(port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    handler.pre_server_start_log()
    server.serve()

if __name__ == '__main__':
    start_server()