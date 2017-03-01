import os

from worker.emulator import Emulator
from zk_droid import DroidZkClient


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
        self.droids_to_start = []
        self.initialised = {}

    def add_droid(self, droid):
        self.droids_to_start.append(droid)

    def start_droid(self, droid):
        droid.start()
        zk_client = DroidZkClient()
        zk_client.setup()
        self.initialised[zk_client.nodename] = {
            'droid': droid,
            'zk_client': zk_client,
        }

    def setup(self):
        while True:
            try:
                droid = self.droids_to_start.pop()
                self.start_droid(droid)
            except IndexError:
                break

    def count(self):
        return len(self.initialised)

    def get_droid(self, id):
        return self.initialised[id]['droid']

    def get_zk_client(self, id):
        return self.initialised[id]['zk_client']

    def stop_droid(self, id):
        # Stop Zk client
        zk_client = self.get_zk_client(id)
        zk_client.teardown()
        # Stop droid
        droid = self.get_droid(id)
        droid.stop()

    def iter_droid_ids(self):
        return self.initialised.iterkeys()

    def teardown(self):
        for instance_id in self.iter_droid_ids():
            self.stop_droid(instance_id)
