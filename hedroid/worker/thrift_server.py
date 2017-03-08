import os
import atexit

import requests
import shutil

from hedroid.logger import logger
from hedroid.worker.helpers import DroidCoordinatorFactory, DroidBuilder
from hedroid.worker.utils import get_config, get_public_hostname
from hedroid.worker.utils import get_package_name_from_url
from hedroid.worker.utils import restart_adb_server
from hedroid.common_settings import VAR_DIR

from hedroid.worker.tgen.droid_service.ttypes import ConnParams, ApplicationException
from hedroid.worker.tgen.droid_service import DroidService

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer


class DroidServiceHandler(object):
    def __init__(self):
        factory = DroidCoordinatorFactory()
        self.coordinator = factory.make_droid_coordinator()

    def setup_dirs(self):
        # setup tmp dir
        if os.path.isdir(VAR_DIR):
            shutil.rmtree(VAR_DIR)

        logger.debug('Setting up temp dir')
        os.makedirs(VAR_DIR)

    def setup(self):
        logger.debug('Setting up dirs')
        self.setup_dirs()
        restart_adb_server()
        logger.debug('Setting up droids')
        config = get_config()
        builder = DroidBuilder()
        for droid in config['droids']:
            for key, value in droid.iteritems():
                func = getattr(builder, "set_{}".format(key))
                func(value)
            self.coordinator.add_droid(builder.build())
        # Start all endpoints now
        self.coordinator.setup()

    def ping(self):
        logger.debug('Ping!')

    def get_package_name(self, apk_url):
        logger.debug("getting package name for apk {}".format(apk_url))
        try:
            return get_package_name_from_url(apk_url)
        except Exception as err:
            exc = ApplicationException()
            exc.msg = str(err)
            if hasattr(err, 'msg'):
                exc.msg = err.msg
            raise exc

    def get_endpoint(self, endpoint_id):
        logger.debug("Getting endpoint for {}".format(endpoint_id))
        endpoint = self.coordinator.get_droid(endpoint_id)
        cp = ConnParams()
        cp.host = get_public_hostname()
        cp.port = endpoint.websockify.source_port
        return cp

    def run_operation(self, endpoint_id, operation, apk_url):
        logger.debug("Interacting with Droid({})".format(endpoint_id))
        try:
            endpoint = self.coordinator.get_droid(endpoint_id)
            if operation == 'install_apk':
                return endpoint.emulator.install_apk_from_url(apk_url)
            elif operation == 'install_and_start_apk':
                endpoint.emulator.install_apk_from_url(apk_url)
                return endpoint.emulator.start_last_package()
            else:
                raise Exception('Unsupported operation - {}'.format(operation))
        except Exception as err:
            exc = ApplicationException()
            exc.msg = str(err)
            if hasattr(err, 'msg'):
                exc.msg = err.msg
            raise exc

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
