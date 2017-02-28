
class EndpointFactory(object):
	def __init__(self):
		self.endpoints = {}

	def add_endpoint(self, id, endpoint):
		self.endpoints[id] = endpoint

	def get_endpoint(self, id):
		if id not in self.endpoints:
			raise Exception('Endpoint does not exist')
		return self.endpoints[id]

