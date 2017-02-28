import os

from worker.emulator import Emulator


class EndpointBuilder(object):
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


class EndpointCoordinator(object):
	def __init__(self):
		self.instances = {}

	def set_endpoint(self, id, endpoint):
		self.instances[id] = endpoint

	def get_endpoint(self, id):
		return self.instances[id]

	def start_all_instances(self):
		for instance in self.instances.values():
			instance.start()

	def get_num_endpoints(self):
		return len(self.instances)