# -*- coding: utf-8 -*-
import uuid
import re
import time

from .SublimeSocketAPI import SublimeSocketAPI
from . import SublimeSocketAPISettings

from .KVS import KVS

# choose transfer method.
from .WebSocket.WSServer import WSServer
from .PythonSwitch import PythonSwitch


class SublimeSocketServer:
	def __init__(self):
		self.api = SublimeSocketAPI(self)
		self.kvs = KVS()

		self.transfer = None
		self.reserveRestart = None



	# control server self.

	def resetServer(self):
		self.refreshKVS()
		self.teardownTransfer()

	def teardownServer(self):
		self.resetServer()
		# teardowned will call.
	
	def refreshKVS(self):
		self.clearAllKeysAndValues()

	def transferTeardowned(self, message):
		self.api.editorAPI.printMessage(message + "\n")
		self.api.editorAPI.statusMessage(message)

		self.transfer = None

		# run when restert reserved.
		if self.reserveRestart:
			self.setupTransfer(*self.reserveRestart)

			self.spinupTransfer()
			self.reserveRestart = None

	
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


	# main API incoming method.
	def transferInputted(self, data, clientId):
		apiData = data.split(SublimeSocketAPISettings.API_DEFINE_DELIM, 1)[1]

		# gen result id of toplevel
		resultIdentity = "callAPI:"+str(uuid.uuid4())
	
		results = self.api.initResult(resultIdentity)
		self.api.parse(apiData, clientId, results)

	def showTransferInfo(self):
		if self.transfer:
			return self.transfer.info()

		else:
			return "no transfer running."



	# control transfer.

	def setupTransfer(self, transferMethod, params):
		if self.transfer:
			message = "SublimeSocket already running." + self.transfer.info()
			self.api.editorAPI.printMessage(message + "\n")
			self.api.editorAPI.statusMessage(message)
		
		else:
			if transferMethod in SublimeSocketAPISettings.TRANSFER_METHODS:
				
				for case in PythonSwitch(transferMethod):
					if case(SublimeSocketAPISettings.WEBSOCKET_SERVER):
						self.transfer = WSServer(self)
						self.transfer.setup(params)
						break

		self.currentTransferMethod = transferMethod

	def spinupTransfer(self):
		if self.transfer:
			self.transfer.spinup()

	def restartTransfer(self):
		if self.transfer:
			# reserve restart
			self.reserveRestart = self.transfer.currentArgs()
			self.teardownTransfer()
		else:
			self.transferSpinupFailed("no transfer running.")

	def teardownTransfer(self):
		if self.transfer:
			self.transfer.teardown()
		else:
			self.transferTeardowned("no transfer running.")

	

	# message series
	
	def sendMessage(self, targetId, message):
		return self.transfer.sendMessage(targetId, message)

	def broadcastMessage(self, message):
		return self.transfer.broadcastMessage(message)



	# other series

	def onTransferRenew(self):
		# initialize API-results buffer for load-settings.
		results = self.api.initResult("onTransferRenew:"+str(uuid.uuid4()))

		settingCommands = self.api.editorAPI.loadSettings("onTransferRenew")
		for command in settingCommands:
			self.api.runAPI(command, None, None, None, results)






	# KVS bridge series

	def clearAllKeysAndValues(self):
		self.kvs.clear()




	# views and KVS
	def viewsDict(self):
		viewsDict = self.kvs.get(SublimeSocketAPISettings.DICT_VIEWS)

		if viewsDict:
			return viewsDict
		
		return {}

	def updateViewsDict(self, viewsDict):
		self.kvs.setKeyValue(SublimeSocketAPISettings.DICT_VIEWS, viewsDict)



	# regions and KVS
	def storeRegion(self, path, identity, regionDict):
		regionsDict = self.regionsDict()
		
		if path in regionsDict:
			if identity in regionsDict:
				pass
			else:
				regionsDict[path][identity] = []

	
		# generate if not exist yet.	
		else:
			regionsDict[path] = {}
			regionsDict[path][identity] = []

		# add regionDict as new item of list.
		regionsDict[path][identity].append(regionDict)

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
			def isSelecting(regionData):
				if SublimeSocketAPISettings.REGION_SELECTING in regionData and regionData[SublimeSocketAPISettings.REGION_SELECTING] == 1:
					return True
				return None

			selectingRegionId = []
			
			for _, regions in regionsDict.items():
				for regionId, regionDatas in regions.items():
					selectingRegionIds = [regionId for regionData in regionDatas if isSelecting(regionData)]
			
			return set(selectingRegionIds)
		return None

	def updateSelectingRegionIdsAndResetOthers(self, path, selectingRegionIds):
		regionsDict = self.kvs.get(SublimeSocketAPISettings.DICT_REGIONS)

		if path in regionsDict:
			# ここで含まれてないのも出せるのでそこでリセットするのが移送敵意。
			regions = regionsDict[path]
			allRegionIds = set(list(regions))
			
			unselectedRegionIds = allRegionIds - selectingRegionIds
			
			for selectingRegionId in selectingRegionIds:
				for regionData in regions[selectingRegionId]:
					regionData[SublimeSocketAPISettings.REGION_SELECTING] = 1
			
			for unselectdRegionid in unselectedRegionIds:
				for regionData in regions[unselectdRegionid]:
					regionData[SublimeSocketAPISettings.REGION_SELECTING] = 0

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
	
