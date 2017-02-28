import os

from worker.emulator import Emulator
from zk_client import DroidZkClient


class DroidBuilder(object):
    def __init__(self):
        self.port = os.environ.get('ADB_PORT', '5554')
        self.avd = os.environ.get('AVD_NAME', 'nexus6-android7')

    def set_port(self, port):
        self.port = port
        return self

    def set_avd(self, avd):
        self.avd = avd
        return self

    def build(self):
        return Emulator(port=self.port, avd=self.avd)


class DroidCoordinator(object):
    def __init__(self):
        self.instances = {}

    def set_endpoint(self, id, endpoint):
        self.instances[id] = {
            'endpoint': endpoint,
            'zk_client': DroidZkClient(id),
        }

    def get_endpoint(self, id):
        return self.instances[id]['endpoint']

    def get_zk_client(self, id):
        return self.instances[id]['zl_client']

    def get_num_endpoints(self):
        return len(self.instances)

    def start_endpoint(self, id):
        endpoint = self.get_endpoint(id)
        # Start droid
        endpoint.start()
        # Setup Zk client
        zk_client = self.get_zk_client(id)
        zk_client.setup()

    def iter_endpoints(self):
        return self.instances.iteritems()

    def setup(self):
        for instance_id, _ in self.iter_instances():
            self.start_endpoint(instance_id)

    def stop_endpoint(self, id):
        endpoint = self.get_endpoint(id)
        # Stop droid
        endpoint.stop()
        # Setup Zk client
        zk_client = self.get_zk_client(id)
        zk_client.teardown()

    def teardown(self):
        for instance_id, _ in self.iter_instances():
            self.stop_endpoint(instance_id)

    