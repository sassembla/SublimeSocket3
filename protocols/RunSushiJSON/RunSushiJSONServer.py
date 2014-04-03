
from ...PythonSwitch import PythonSwitch
from ... import SublimeSocketAPISettings


import time

THREAD_INTERVAL = 1.0

class RunSushiJSONServer:
	def __init__(self, server, transferId):
		self.methodName = SublimeSocketAPISettings.PROTOCOL_RUNSUSHIJSON_SERVER
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
		self.sublimeSocketServer.transferSpinupped('SublimeSocket RunSushiJSONServer spinupped'+self.transferId)

		data = SublimeSocketAPISettings.SSAPI_PREFIX_SUB + SublimeSocketAPISettings.SSAPI_DEFINE_DELIM + SublimeSocketAPISettings.API_RUNSUSHIJSON + ":" + "{\"path\": \"" + self.path + "\"}"
		
		self.sublimeSocketServer.transferInputted(data, self.transferId)
		while self.continuation:
			time.sleep(THREAD_INTERVAL)

		message = "SublimeSocket RunSushiJSONServer closed:"+self.transferId
		self.sublimeSocketServer.transferTeardowned(self.transferId, message)

	## teardown the server
	def teardown(self):
		self.continuation = False
		

	## return connection IDs
	def connectionIdentities(self):
		# runSushiJSONServer has no connections.
		return []
		
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
		

	# transfering datas as runSushiJSON API input.
	def input(self, params):

		if "path" in params:
			assert not "data" in params, "RunSushiJSONServer require 'path' or 'data' param. Not both."
			path = params["path"]
			data = SublimeSocketAPISettings.SSAPI_PREFIX_SUB + SublimeSocketAPISettings.SSAPI_DEFINE_DELIM + SublimeSocketAPISettings.API_RUNSUSHIJSON + ":" + "{\"path\": \"" + path + "\"}"
			
			self.call(data, None)

		elif "data" in params:
			dataSource = params["data"]
			escapedDataSource = dataSource.replace("\"", "\\\"")
			data = SublimeSocketAPISettings.SSAPI_PREFIX_SUB + SublimeSocketAPISettings.SSAPI_DEFINE_DELIM + SublimeSocketAPISettings.API_RUNSUSHIJSON + ":" + "{\"data\": \"" + escapedDataSource + "\"}"

			self.call(data, None)


	# call SublimeSocket server.
	def call(self, dataSource, clientId):
		self.sublimeSocketServer.transferInputted(dataSource, self.transferId)


	def sendMessage(self, targetId, message):
		return (False, "no imple")

	def broadcastMessage(self, message):
		return []
