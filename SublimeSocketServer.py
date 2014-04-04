# -*- coding: utf-8 -*-

import re
import time

from .SublimeSocketAPI import SublimeSocketAPI
from . import SublimeSocketAPISettings

from .KVS import KVS

# choose transfer method from below.
from .protocols.RunSushiJSON.RunSushiJSONServer import RunSushiJSONServer
from .protocols.WebSocket.WSServer import WSServer
from .protocols.HTTP.HTTPServer import HTTPServer
from .protocols.ByteData.ByteDataServer import ByteDataServer
from .protocols.TailMachine.TailMachine import TailMachine


from .PythonSwitch import PythonSwitch


class SublimeSocketServer:
	def __init__(self):
		self.api = SublimeSocketAPI(self)
		self.kvs = KVS()

		self.transfers = {}
		self.reserveRestart = {}

		self.onConnectedTriggers = {}

	# control server self.

	def resetServer(self):
		currentTransferIdentities = list(self.transfers)
		for transferIdentity in currentTransferIdentities:
			self.teardownTransfer(transferIdentity)

		self.refreshKVS()

	def teardownServer(self):
		self.resetServer()
		# teardowned will be called.
	
	def refreshKVS(self):
		self.clearAllKeysAndValues()

	def transferTeardowned(self, transferIdentity, message):
		self.api.editorAPI.printMessage(message + "\n")
		self.api.editorAPI.statusMessage(message)

		del self.transfers[transferIdentity]

		# run if restert reserved.
		if transferIdentity in self.reserveRestart:
			newTransferIdentity = self.setupTransfer(*self.reserveRestart[transferIdentity])

			self.spinupTransfer(newTransferIdentity)
			del self.reserveRestart[transferIdentity]

		if self.transfers:
			pass
		else:
			self.api.editorAPI.statusMessage("no transfer remain. SublimeSocketServer is now restartable.")

	def transferIdentities(self):
		return self.transfers.keys()
	
	def transferNoticed(self, message):
		self.api.editorAPI.printMessage(message)

	def transferSpinupFailed(self, message):
		self.api.editorAPI.printMessage(message)
		self.api.editorAPI.statusMessage(message)

	def transferSpinupped(self, message):
		self.api.editorAPI.printMessage(message)
		self.api.editorAPI.statusMessage(message)

		# react to renew
		self.onTransferRenew()

	def transferConnected(self, transferIdentity, connectionId):
		if self.onConnectedTriggers:
			if transferIdentity in self.onConnectedTriggers:
				triggers = self.onConnectedTriggers[transferIdentity]
				for func in triggers:
					func()
					
				del self.onConnectedTriggers[transferIdentity]


	# by raw string. main API data incoming method.
	def transferInputted(self, data, transferId, clientId=None):
		apiData = data.split(SublimeSocketAPISettings.SSAPI_DEFINE_DELIM, 1)[1]

		self.api.parse(apiData, transferId, clientId)

		# should run for stub.
		# self.dummyOutput(apiData)

	# by command and params. direct igniton of API.
	def transferRunAPI(self, command, params, transferId, clientId=None):
		self.api.runAPI(command, params, transferId, clientId)
		

	def showTransferInfo(self):
		if self.transfers:
			infos = [" ".join(transfer.info()) for transfer in self.transfers.values()]
			return infos

		else:
			return "no transfer running."

	def isValidTransferId(self, transferIdentity):
		if transferIdentity in self.transfers:
			return True

		return False

	def isValidConnectionId(self, transferIdentity, connectionIdentity):
		if self.isValidTransferId(transferIdentity) and connectionIdentity in self.transfers[transferIdentity].connectionIdentities():
			return True

		return False

	def updateTransferClientIdOf(self, targetTransferIdentity, targetConnectionIdentity, newConnectionIdentity):
		self.transfers[targetTransferIdentity].updateClientId(targetConnectionIdentity, newConnectionIdentity)



	# control transfer.

	def setupTransfer(self, params):
		assert SublimeSocketAPISettings.ADDTRANSFER_PROTOCOL in params, "setupTransfer require 'protocol' param."
		assert SublimeSocketAPISettings.ADDTRANSFER_TRANSFERIDENTITY in params, "setupTransfer require 'transferIdentity' param."
		assert SublimeSocketAPISettings.ADDTRANSFER_CONNECTIONIDENTITY in params, "setupTransfer require 'connectionIdentity' param for add new transfer."

		transferIdentity = params[SublimeSocketAPISettings.ADDTRANSFER_TRANSFERIDENTITY]
		
		print("self.transfers", self.transfers)

		if self.transfers:
			assert not transferIdentity in self.transfers, "identity:" + transferIdentity + " has already taken. please define other identity. taken by:" + str(self.transfers[transferIdentity]) + " please use 'addConnectionToTransfer' API."
		
		transferProtocol = params[SublimeSocketAPISettings.ADDTRANSFER_PROTOCOL]
		assert transferProtocol in SublimeSocketAPISettings.TRANSFER_PROTOCOLS, "protocol:" + transferProtocol + " is not supported."
			
		for case in PythonSwitch(transferProtocol):
			if case(SublimeSocketAPISettings.PROTOCOL_RUNSUSHIJSON_SERVER):
				assert "path" in params, "RunSushiJSONServer require 'path' param."
				
				self.transfers[transferIdentity] = RunSushiJSONServer(self, transferIdentity)
				self.transfers[transferIdentity].setup(params)

				break
				
			if case(SublimeSocketAPISettings.PROTOCOL_WEBSOCKET_SERVER):
				assert "host" in params, "WebSocketServer require 'host' param."
				assert "port" in params, "WebSocketServer require 'port' param."
				
				self.transfers[transferIdentity] = WSServer(self, transferIdentity)
				self.transfers[transferIdentity].setup(params)

				break

			if case(SublimeSocketAPISettings.PROTOCOL_HTTP_SERVER):
				assert "host" in params, "WebSocketServer require 'host' param."
				assert "port" in params, "WebSocketServer require 'port' param."
				
				self.transfers[transferIdentity] = HTTPServer(self, transferIdentity)
				self.transfers[transferIdentity].setup(params)

				break

			if case(SublimeSocketAPISettings.PROTOCOL_BYTEDATA_SERVER):
				assert "binders" in params, "ByteDataServer require 'binders' param."
				self.transfers[transferIdentity] = ByteDataServer(self, transferIdentity)
				self.transfers[transferIdentity].setup(params)
				break


			if case(SublimeSocketAPISettings.PROTOCOL_TAIL_MACHINE):
				assert "result" in params, "TailMachine require 'result' param."
				result = params["result"]
				
				# not file, reactor body.
				if result == -1:
				    assert "tailPath" in params, "TailMachine require 'tailPath' param."
				    assert "reactors" in params, "TailMachine require 'reactors' param."

				# file path. reactor string.
				else:
				    assert "tailPath" in params, "TailMachine require 'tailPath' param."
				    assert "reactorsSource" in params, "TailMachine require 'reactorsSource' param."

				self.transfers[transferIdentity] = TailMachine(self)
				self.transfers[transferIdentity].setup(params)
				break


		return transferIdentity

	def inputToTransfer(self, params):
		assert SublimeSocketAPISettings.INPUTTOTRANSFER_TRANSFERIDENTITY in params, "inputToTransfer require 'transferIdentity' param."
		assert SublimeSocketAPISettings.INPUTTOTRANSFER_PARAMS in params, "inputToTransfer require 'params' param."
		
		transferIdentity = params[SublimeSocketAPISettings.INPUTTOTRANSFER_TRANSFERIDENTITY]
		assert transferIdentity in self.transfers, "transferIdentity:" + transferIdentity + " is not in current transfers."

		currentParams = params[SublimeSocketAPISettings.INPUTTOTRANSFER_PARAMS]
		self.transfers[transferIdentity].input(currentParams)
		


	def addConnectionToTransfer():
		print("not yet implemented.")
		pass


	# spinup "latest" transfer.
	def spinupLatestTransfer(self):
		assert self.transfers, "should setupTransfer before spinup."
		transferIdentity = list(self.transfers)[-1]
		self.spinupTransfer(transferIdentity)


	def spinupTransfer(self, transferIdentity):
		assert transferIdentity in self.transfers, "there are no transfer:"+transferIdentity
		self.transfers[transferIdentity].spinup()


	def restartTransfer(self, transferIdentity):
		if transferIdentity in self.transfers:
			# reserve restart
			self.reserveRestart[transferIdentity] = self.transfers[transferIdentity].currentArgs()
			self.teardownTransfer(transferIdentity)
		else:
			self.transferSpinupFailed("no transfer running:"+ transferIdentity)

	def teardownTransfer(self, transferIdentity):
		if transferIdentity in self.transfers:
			self.transfers[transferIdentity].teardown()
		else:
			self.transferTeardowned(transferIdentity, "no transfer running.")

	def appendOnConnectedTriggers(self, transferIdentity, funcs):
		for addedFunctionDict in self.onConnectedTriggers:
			if transferIdentity in addedFunctionDict.keys():
				print("duplicate trigger for:" + transferIdentity + " function:" +str(funcs))
				return
			
		self.onConnectedTriggers[transferIdentity] = funcs

	# message series
	
	def sendMessage(self, transferId, connectionId, message):
		assert connectionId, "sendMessage require 'connectionId' param."

		if transferId in self.transfers:
			return self.transfers[transferId].sendMessage(connectionId, message)
		
		# if transferId is None, try to send message via all transfer's connectionId.
		elif not transferId:
			results = [self.transfers[currentTransferId].sendMessage(connectionId, message) for currentTransferId in list(self.transfers)]

			# ignore result. 
			return (True, "done")

		return (False, "no transfer & connection found in transfers:" + str(self.transfers) + " connection:" + connectionId)
		

	def broadcastMessage(self, message):
		return [self.transfers[transferId].broadcastMessage(message) for transferId in self.transfers]

	# purge
	def purgeConnection(self, transferId, connectionId):
		self.transfers[transferId].purgeConnection(connectionId)


	# other series

	def onTransferRenew(self):
		settingCommands = self.api.editorAPI.loadSettings("onTransferRenew")
		for command in settingCommands:
			self.api.runAPI(command, None)






	# KVS bridge series

	def clearAllKeysAndValues(self):
		self.kvs.clear()


	def showAllKeysAndValues(self):
		everything = self.kvs.getAll()
		print("everything", everything)


	# views and KVS
	def viewsDict(self):
		viewsDict = self.kvs.get(SublimeSocketAPISettings.DICT_VIEWS)

		if viewsDict:
			return viewsDict
		
		return {}

	def updateViewsDict(self, viewsDict):
		self.kvs.setKeyValue(SublimeSocketAPISettings.DICT_VIEWS, viewsDict)



	# regions and KVS
	def storeRegion(self, path, identity, line, regionFrom, regionTo, message):
		regionsDict = self.regionsDict()
		
		if path in regionsDict:
			if identity in regionsDict[path]:
				pass
			else:
				regionsDict[path][identity] = {}
				regionsDict[path][identity][SublimeSocketAPISettings.REGION_LINE] = line
				regionsDict[path][identity][SublimeSocketAPISettings.REGION_FROM] = regionFrom
				regionsDict[path][identity][SublimeSocketAPISettings.REGION_TO] = regionTo
				regionsDict[path][identity][SublimeSocketAPISettings.REGION_MESSAGES] = []
		else:
			regionsDict[path] = {}
			regionsDict[path][identity] = {}
			regionsDict[path][identity][SublimeSocketAPISettings.REGION_LINE] = line
			regionsDict[path][identity][SublimeSocketAPISettings.REGION_FROM] = regionFrom
			regionsDict[path][identity][SublimeSocketAPISettings.REGION_TO] = regionTo
			regionsDict[path][identity][SublimeSocketAPISettings.REGION_MESSAGES] = []

		if not message in regionsDict[path][identity][SublimeSocketAPISettings.REGION_MESSAGES]:
			regionsDict[path][identity][SublimeSocketAPISettings.REGION_MESSAGES].insert(0, message)
		
			self.updateRegionsDict(regionsDict)

	def regionsDict(self):
		regionsDict = self.kvs.get(SublimeSocketAPISettings.DICT_REGIONS)

		if regionsDict:
			return regionsDict

		return {}

	def updateRegionsDict(self, regionsDict):
		self.kvs.setKeyValue(SublimeSocketAPISettings.DICT_REGIONS, regionsDict)

	def selectingRegionIds(self, path):
		regionsDict = self.kvs.get(SublimeSocketAPISettings.DICT_REGIONS)
		
		if path in regionsDict:
			selectingRegionIds = [regionId for regionId, regionDatas in regionsDict[path].items() if SublimeSocketAPISettings.REGION_ISSELECTING in regionDatas and regionDatas[SublimeSocketAPISettings.REGION_ISSELECTING] == 1]
			
			return selectingRegionIds

		return []

	def updateSelectingRegionIdsAndResetOthers(self, path, selectingRegionIds):
		regionsDict = self.kvs.get(SublimeSocketAPISettings.DICT_REGIONS)
		
		if path in regionsDict:
			regions = regionsDict[path]
			allRegionIds = list(regions)
			
			unselectedRegionIds = set(allRegionIds) - set(selectingRegionIds)

			for selectingRegionId in selectingRegionIds:
				regions[selectingRegionId][SublimeSocketAPISettings.REGION_ISSELECTING] = 1
			
			for unselectdRegionid in unselectedRegionIds:
				regions[unselectdRegionid][SublimeSocketAPISettings.REGION_ISSELECTING] = 0

	# reactor and KVS
	def reactorsDict(self):
		reactorsDict = self.kvs.get(SublimeSocketAPISettings.DICT_REACTORS)
		if reactorsDict:
			return reactorsDict

		return {}

	def updateReactorsDict(self, reactorsDict):
		self.kvs.setKeyValue(SublimeSocketAPISettings.DICT_REACTORS, reactorsDict)




	# reactorsLog and KVS
	def reactorsLogDict(self):
		reactorsLogDict = self.kvs.get(SublimeSocketAPISettings.DICT_REACTORSLOG)

		if reactorsLogDict:
			return reactorsLogDict

		return {}

	def updateReactorsLogDict(self, reactorsLogDict):
		self.kvs.setKeyValue(SublimeSocketAPISettings.DICT_REACTORSLOG, reactorsLogDict)




	# completions and KVS
	def completionsDict(self):
		completionsDict = self.kvs.get(SublimeSocketAPISettings.DICT_COMPLETIONS)
		if completionsDict:
			return completionsDict

		return {}

	def deleteCompletion(self, identity):
		completionsDict = self.kvs.get(SublimeSocketAPISettings.DICT_COMPLETIONS)
		del completionsDict[identity]
		self.updateCompletionsDict(completionsDict)

	def updateCompletionsDict(self, completionsDict):
		self.kvs.setKeyValue(SublimeSocketAPISettings.DICT_COMPLETIONS, completionsDict)



	# filters and KVS
	def filtersDict(self):
		filtersDict = self.kvs.get(SublimeSocketAPISettings.DICT_FILTERS)

		if filtersDict:
			return filtersDict

		return {}

	def updateFiltersDict(self, filtersDict):
		self.kvs.setKeyValue(SublimeSocketAPISettings.DICT_FILTERS, filtersDict)
	


	# def dummyOutput(self, data):
	# 	# 適当に書き出してしまおう。
	# 	print("d",data)

	# 	pass