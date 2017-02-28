from contextlib import contextmanager

from tgen.droid_service import DroidService

from thrift import Thrift
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
		transport.open()
		yield
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

	def install_apk(self, endpoint_id, apk_url):
		with self.transport():
			return self.client.install_apk(endpoint_id, apk_url)

	def start_package(self, endpoint_id, package_name):
		with self.transport():
			return self.client.start_package(endpoint_id, package_name)