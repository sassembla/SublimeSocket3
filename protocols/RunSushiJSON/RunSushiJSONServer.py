
from ...PythonSwitch import PythonSwitch
from ... import SublimeSocketAPISettings


import time


class RunSushiJSONServer:
	def __init__(self, server, transferId):
		self.methodName = SublimeSocketAPISettings.RUNSUSHIJSON_SERVER
		self.transferId = transferId
		
		self.args = None

		self.path = "not set yet."
		self.continuation = False

		self.sublimeSocketServer = server

	def info(self):
		message = "SublimeSocket RunSushiJSONServer running by path:" + self.path
		
		return message
		

	def currentArgs(self):
		return (self.methodName, self.args)


	def setup(self, params):
		assert "path" in params, "RunSushiJSONServer require 'path' param."

		self.path = params["path"]

		if "continuation" in params:
			self.continuation = params["continuation"]
		
		# set for restart.
		self.args = params
		


	def spinup(self):
		self.sublimeSocketServer.transferSpinupped('SublimeSocket RunSushiJSONServer spinupped')

		data = SublimeSocketAPISettings.SSAPI_PREFIX_SUB + SublimeSocketAPISettings.SSAPI_DEFINE_DELIM + SublimeSocketAPISettings.API_RUNSUSHIJSON + ":" + "{\"path\": \"" + self.path + "\"}"
		
		self.sublimeSocketServer.transferInputted(data, self.transferId)

		while self.continuation:
			time.sleep(0.1)

	## teardown the server
	def teardown(self):
		self.sublimeSocketServer.transferSpinupped('SublimeSocket RunSushiJSONServer teardowned')

	## return connection IDs
	def connectionIdentities(self):
		pass
		
	## update specific client's id
	def updateClientId(self, clientId, newIdentity):
		print("updateClientId do nothing.")

	def thisClientIsDead(self, clientId):
		print("thisClientIsDead do nothing.")
		

	def purgeConnection(self, clientId):
		print("purgeConnection do nothing.")
		

	# remove from Client dict
	def closeClient(self, clientId):
		print("closeClient do nothing.", clientId)

	# call SublimeSocket server. transfering datas.
	def call(self, data, clientId):
		print("call with data", data, "to", clientId)


	def sendMessage(self, targetId, message):
		if message:
			pass
		else:
			return (False, "no data to:"+targetId)
		
		print("call with data", data, "to", clientId)


	def broadcastMessage(self, message):
		print("broadcastMessage do nothing.")
