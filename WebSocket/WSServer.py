# -*- coding: utf-8 -*-


# サーバ、WebSocketサーバの実装そのもので、その単一性を使って動いているので、KVSコントロール部分と分離したい。
# 

import sublime, sublime_plugin

import threading
import os
import socket
import threading
import string
import time
import json
import uuid
import re

from .WSClient import WSClient

from ..SublimeSocketAPI import SublimeSocketAPI

# choice editorApi by platform.
from ..interface.SublimeText.EditorAPI import EditorAPI

from .. import SublimeSocketAPISettings
from ..PythonSwitch import PythonSwitch


class WSServer:
	def __init__(self):
		self.clients = {}
		
		self.socket = ''
		self.host = ''
		self.port = ''

		self.listening = False
		self.kvs = KVS()
		self.editorAPI = EditorAPI()

		self.api = SublimeSocketAPI(self, self.editorAPI)

		# python上でないといけない。
		self.currentCompletion = {}


	def start(self, host, port):
		self.host = host
		self.port = port
		self.socket = socket.socket()

		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		try:
			self.socket.bind((host,port))
		except socket.error as msg:
			# print ("error", msg[1])
			return 1

		self.socket.listen(1)

		serverStartMessage = 'SublimeSocket WebSocketServing started @ ' + str(host) + ':' + str(port)
		print('\n', serverStartMessage, "\n")
		sublime.status_message(serverStartMessage)


		# initialize API-results buffer for load-settings.
		results = self.api.initResult("loadSettings:"+str(uuid.uuid4()))

		# load settings
		self.loadSettings(results)


		self.listening = True
		while self.listening:
			(conn, addr) = self.socket.accept()

			if self.listening is None:
				return 0
			
			identity = str(uuid.uuid4())

			# genereate new client
			client = WSClient(self, identity)
			
			self.clients[identity] = client

			threading.Thread(target = client.handle, args = (conn,addr)).start()
				
		return 0
		

	## load settings and run in mainThread
	def loadSettings(self, results):
		settingCommands = sublime.load_settings("SublimeSocket.sublime-settings").get('loadSettings')
		for command in settingCommands:
			self.api.runAPI(command, None, None, None, results)

	## update specific client's id
	def updateClientId(self, client, params):
		assert client, "updateClientId requre 'client should not be None'"
		assert SublimeSocketAPISettings.IDENTITY_ID in params, "updateClientId requre 'id' param"

		newIdentity = params[SublimeSocketAPISettings.IDENTITY_ID]

		currentClient = self.clients[client.clientId]

		# del from list
		self.deleteClientId(currentClient.clientId)

		# update
		client.clientId = newIdentity
		self.clients[newIdentity] = client

		return newIdentity

	# remove from Client dict
	def deleteClientId(self, clientId):
		if clientId in self.clients:
			del self.clients[clientId]
		else:
			print("ss: server don't know about client:", clientId)

	## api 
	def callAPI(self, apiData, clientId):
		currentClient = [client for client in self.clients.values() if client.clientId == clientId][0]
		
		# gen result id of toplevel
		resultIdentity = "callAPI:"+str(uuid.uuid4())
	
		results = self.api.initResult(resultIdentity)
		self.api.parse(apiData, currentClient, results)
		
		
	## tearDown the server
	def tearDown(self):
		for clientId in self.clients:
			client = self.clients[clientId]
			client.close()

		self.clients = None

		# no mean?
		self.socket.close()
		
		# stop receiving
		self.listening = False
		

		self.kvs.clear()
		
		serverTearDownMessage = 'SublimeSocket WebSocketServing tearDown @ ' + str(self.host) + ':' + str(self.port)
		print('\n', serverTearDownMessage, "\n")
		sublime.status_message(serverTearDownMessage)


	## return the filter has been defined or not
	def isFilterDefined(self, filterName):
		if self.isExistOnKVS(SublimeSocketAPISettings.DICT_FILTERS):
			filterDict = self.kvs.get(SublimeSocketAPISettings.DICT_FILTERS)
			if filterName in filterDict:
				return True
		return False

	## collect current views
	def collectViews(self, results):
		collectedViews = []
		for views in [window.views() for window in sublime.windows()]:
			for view in views:
				viewParams = self.editorAPI.generateSublimeViewInfo(
					view,
					SublimeSocketAPISettings.VIEW_SELF,
					SublimeSocketAPISettings.VIEW_ID,
					SublimeSocketAPISettings.VIEW_BUFFERID,
					SublimeSocketAPISettings.VIEW_PATH,
					SublimeSocketAPISettings.VIEW_BASENAME,
					SublimeSocketAPISettings.VIEW_VNAME,
					SublimeSocketAPISettings.VIEW_SELECTED,
					SublimeSocketAPISettings.VIEW_ISEXIST
				)

				emitIdentity = str(uuid.uuid4())
				viewParams[SublimeSocketAPISettings.REACTOR_VIEWKEY_EMITIDENTITY] = emitIdentity


				self.fireKVStoredItem(
					SublimeSocketAPISettings.REACTORTYPE_VIEW,
					SublimeSocketAPISettings.SS_EVENT_COLLECT, 
					viewParams,
					results
				)

				collectedViews.append(viewParams[SublimeSocketAPISettings.VIEW_PATH])

		self.api.setResultsParams(results, self.collectViews, {"collected":collectedViews})
	
	
	## store region to viewDict-view in KVS
	def storeRegionToView(self, view, identity, region, line, message):
		path = self.internal_detectViewPath(view)

		specificViewDict = self.viewsDict()[path]

		regionDict = {}
		regionDict[SublimeSocketAPISettings.REGION_LINE] = line
		regionDict[SublimeSocketAPISettings.REGION_MESSAGE] = message
		regionDict[SublimeSocketAPISettings.REGION_SELF] = region
		
		# generate SUBDICT_REGIONS if not exist yet.
		if not SublimeSocketAPISettings.SUBDICT_REGIONS in specificViewDict:
			specificViewDict[SublimeSocketAPISettings.SUBDICT_REGIONS] = {}
			specificViewDict[SublimeSocketAPISettings.SUBARRAY_DELETED_REGIONS] = {}

		specificViewDict[SublimeSocketAPISettings.SUBDICT_REGIONS][identity] = regionDict


	## delete all regions in all view 
	def deleteAllRegionsInAllView(self, targetViewPath=None):
		deletes = {}

		viewDict = self.viewsDict()
		if not viewDict:
			return deletes
		

		def eraseAllRegionsAtViewDict(viewDictValue):
		
			if SublimeSocketAPISettings.SUBDICT_REGIONS in viewDictValue:
				
				viewInstance = viewDictValue[SublimeSocketAPISettings.VIEW_SELF]
					

				regionsDict = viewDictValue[SublimeSocketAPISettings.SUBDICT_REGIONS]
				deletesList = []

				currentViewPath = viewInstance.file_name()

				# if exist, should erase specified view's region only.
				if targetViewPath:
					if currentViewPath:
						if not currentViewPath in targetViewPath:
							return
					else:
						return

				deletes[currentViewPath] = deletesList
				currentDeletesList = deletes[currentViewPath]
				
				if regionsDict:
					for regionIdentity in regionsDict.keys():
						viewInstance.erase_regions(regionIdentity)

						if currentViewPath:
							currentDeletesList.append(regionIdentity)

						viewDictValue[SublimeSocketAPISettings.SUBARRAY_DELETED_REGIONS][regionIdentity] = 1
				
					deletedRegions = viewDictValue[SublimeSocketAPISettings.SUBARRAY_DELETED_REGIONS]

					for deletedRegionIdentity in deletedRegions.keys(): 
						if deletedRegionIdentity in regionsDict:
							del regionsDict[deletedRegionIdentity]

				regionsDict = {}

		list(map(eraseAllRegionsAtViewDict, viewDict.values()))
		return deletes


	## set reactor to KVS
	def setReactor(self, reactorType, params):
		assert SublimeSocketAPISettings.REACTOR_TARGET in params, "setXReactor require 'target' param."
		assert SublimeSocketAPISettings.REACTOR_REACT in params, "setXReactor require 'react' param."
		assert SublimeSocketAPISettings.REACTOR_SELECTORS in params, "setXReactor require 'selectors' param."

		reactorsDict = {}
		reactorsLogDict = {}

		if self.isExistOnKVS(SublimeSocketAPISettings.DICT_REACTORS):
			reactorsDict = self.getV(SublimeSocketAPISettings.DICT_REACTORS)

		if self.isExistOnKVS(SublimeSocketAPISettings.DICT_REACTORSLOG):
			reactorsLogDict = self.getV(SublimeSocketAPISettings.DICT_REACTORSLOG)


		target = params[SublimeSocketAPISettings.REACTOR_TARGET]
		reactEventName = params[SublimeSocketAPISettings.REACTOR_REACT]
		selectorsArray = params[SublimeSocketAPISettings.REACTOR_SELECTORS]

		# set default delay
		delay = 0
		if SublimeSocketAPISettings.REACTOR_DELAY in params:
			delay = params[SublimeSocketAPISettings.REACTOR_DELAY]
		
		reactDict = {}
		reactDict[SublimeSocketAPISettings.REACTOR_SELECTORS] = selectorsArray
		reactDict[SublimeSocketAPISettings.REACTOR_DELAY] = delay

		if SublimeSocketAPISettings.REACTOR_INJECT in params:
			reactDict[SublimeSocketAPISettings.REACTOR_INJECT] = params[SublimeSocketAPISettings.REACTOR_INJECT]

		# already set or not-> spawn dictionary for name.
		if not reactEventName in reactorsDict:			
			reactorsDict[reactEventName] = {}
			reactorsLogDict[reactEventName] = {}


		# store reactor			
		reactorsDict[reactEventName][target] = reactDict

		# reset reactLog too
		reactorsLogDict[reactEventName][target] = {}


		self.setKV(SublimeSocketAPISettings.DICT_REACTORS, reactorsDict)
		self.setKV(SublimeSocketAPISettings.DICT_REACTORSLOG, reactorsLogDict)
			

		return reactorsDict


	def removeAllReactors(self):
		reactorsDict = {}
		if self.isExistOnKVS(SublimeSocketAPISettings.DICT_REACTORS):
			reactorsDict = self.getV(SublimeSocketAPISettings.DICT_REACTORS)

		reactorsLogDict = {}
		if self.isExistOnKVS(SublimeSocketAPISettings.DICT_REACTORSLOG):
			reactorsLogDict = self.getV(SublimeSocketAPISettings.DICT_REACTORSLOG)

		deletedReactorsDict = reactorsDict

		self.setKV(SublimeSocketAPISettings.DICT_REACTORS, {})
		self.setKV(SublimeSocketAPISettings.DICT_REACTORSLOG, {})

		return reactorsDict


	## emit event if params matches the regions that sink in view
	def containsRegionsInKVS(self, params, results):
		viewDict = self.viewsDict()
		if viewDict:
			
			# specify regions that are selected.
			viewInstance = params[SublimeSocketAPISettings.CONTAINSREGIONS_VIEW]
			selectedRegionSet = params[SublimeSocketAPISettings.CONTAINSREGIONS_SELECTED]

			viewId = viewInstance.file_name()

			# return if view not exist(include ST's console)
			if not viewId in viewDict:
				return

			
			viewInfoDict = viewDict[viewId]
			if SublimeSocketAPISettings.SUBDICT_REGIONS in viewInfoDict:
				regionsDicts = viewInfoDict[SublimeSocketAPISettings.SUBDICT_REGIONS]
				
				
				# identity
				def isRegionMatchInDict(dictKey):
					currentRegion = regionsDicts[dictKey][SublimeSocketAPISettings.REGION_SELF]
					
					if selectedRegionSet.contains(currentRegion):
						return dictKey
					else:
						pass
					
				regionIdentitiesListWithNone = [isRegionMatchInDict(key) for key in regionsDicts.keys()]
				
				# collect if exist
				regionIdentitiesList = [val for val in regionIdentitiesListWithNone if val]
				
				target = params[SublimeSocketAPISettings.CONTAINSREGIONS_TARGET]
				emit = params[SublimeSocketAPISettings.CONTAINSREGIONS_EMIT]
				
				# emit event of regions
				def emitRegionMatchEvent(key):

					regionInfo = regionsDicts[key]

					# append target
					regionInfo[SublimeSocketAPISettings.REACTOR_TARGET] = target
					
					self.fireKVStoredItem(SublimeSocketAPISettings.REACTORTYPE_VIEW, emit, regionInfo, results)
					
					if SublimeSocketAPISettings.CONTAINSREGIONS_DEBUG in params:
						debug = params[SublimeSocketAPISettings.CONTAINSREGIONS_DEBUG]

						if debug:
							message = regionInfo[SublimeSocketAPISettings.APPENDREGION_MESSAGE]

							messageDict = {}
							messageDict[SublimeSocketAPISettings.SHOWSTATUSMESSAGE_MESSAGE] = message
							
							self.api.runAPI(SublimeSocketAPISettings.API_I_SHOWSTATUSMESSAGE, messageDict, None, None, results)
							self.api.printout(message)
							
				[emitRegionMatchEvent(region) for region in regionIdentitiesList]
				

	## show current status & connectionIds
	def showCurrentStatusAndConnections(self):
		print("ss: server host:", self.host, "	port:", self.port)
		
		print("ss: connections:")
		for client in self.clients:
			print("	", client)


	

	## input to sublime from server.
	# fire event in KVS, if exist.
	def fireKVStoredItem(self, reactorType, eventName, eventParam, results):
		reactorsDict = self.getV(SublimeSocketAPISettings.DICT_REACTORS)
		reactorsLogDict = self.getV(SublimeSocketAPISettings.DICT_REACTORSLOG)

		# run when the event occured adopt. start with specific "user-defined" event identity that defined as REACTIVE_PREFIX_USERDEFINED_EVENT.
		if eventName.startswith(SublimeSocketAPISettings.REACTIVE_PREFIX_USERDEFINED_EVENT):
			# if exist, continue
			if reactorsDict and eventName in reactorsDict:
				
				target = eventParam[SublimeSocketAPISettings.REACTOR_TARGET]
				if target in reactorsDict[eventName]:
					reactDict = reactorsDict[eventName][target]

					delay = reactorsDict[eventName][target][SublimeSocketAPISettings.REACTOR_DELAY]

					if not self.isExecutableWithDelay(eventName, target, delay):
						pass
					else:
						self.api.runAllSelector(reactDict, eventParam, results)

		elif eventName in SublimeSocketAPISettings.REACTIVE_FOUNDATION_EVENT:
			if reactorsDict and eventName in reactorsDict:
				self.api.runFoundationEvent(eventName, eventParam, reactorsDict[eventName], results)
				
		else:
			if eventName in SublimeSocketAPISettings.VIEW_EVENTS_RENEW:
				self.runRenew(eventParam)

			if eventName in SublimeSocketAPISettings.VIEW_EVENTS_DEL:
				self.runDeletion(eventParam)

			# if reactor exist, run all selectors. not depends on "target".
			if reactorsDict and eventName in reactorsDict:
				reactorDict = reactorsDict[eventName]
				for reactorKey in list(reactorDict):
					
					delay = reactorsDict[eventName][reactorKey][SublimeSocketAPISettings.REACTOR_DELAY]
					if not self.isExecutableWithDelay(eventName, reactorKey, delay):
						pass

					else:
						reactorParams = reactorDict[reactorKey]
						self.api.runReactor(reactorType, reactorParams, eventParam, results)

	
	def isExecutableWithDelay(self, name, target, elapsedWaitDelay):
		currentTime = round(int(time.time()*1000))
		reactorsLogDict = self.getV(SublimeSocketAPISettings.DICT_REACTORSLOG)

		if elapsedWaitDelay == 0:
			pass
		else:
			# check should delay or not.

			# delay log is exist.
			if name in reactorsLogDict and target in reactorsLogDict[name]:
				delayedExecuteLog = reactorsLogDict[name][target]
				if SublimeSocketAPISettings.REACTORSLOG_LATEST in delayedExecuteLog:
					latest = delayedExecuteLog[SublimeSocketAPISettings.REACTORSLOG_LATEST]

					# should delay = not enough time passed.
					if 0 < (elapsedWaitDelay + latest - currentTime):
						return False


		# update latest time

		# create executed log dict if not exist.
		if name in reactorsLogDict:
			if target in reactorsLogDict[name]:
				pass
			else:
				reactorsLogDict[name][target] = {}
		else:
			reactorsLogDict[name] = {}
			reactorsLogDict[name][target] = {}

		reactorsLogDict[name][target][SublimeSocketAPISettings.REACTORSLOG_LATEST]	= currentTime
		self.setKV(SublimeSocketAPISettings.DICT_REACTORSLOG, reactorsLogDict)
		
		return True

	## return completion then delete.
	def consumeCompletion(self, viewIdentity, eventName):
		if viewIdentity in list(self.currentCompletion):
			completion = self.currentCompletion[viewIdentity]
			del self.currentCompletion[viewIdentity]
			return completion

		return None


	def updateCompletion(self, viewIdentity, completions):
		self.currentCompletion[viewIdentity] = completions
		

	def runRenew(self, eventParam):
		viewInstance = eventParam[SublimeSocketAPISettings.VIEW_SELF]
		filePath = eventParam[SublimeSocketAPISettings.REACTOR_VIEWKEY_PATH]

		if self.editorAPI.isBuffer(filePath):
			if self.editorAPI.isNamed(viewInstance):
				pass
			else:
				# no name buffer view will ignore.
				return
			
		# update or append if exist.
		viewDict = self.viewsDict()


		viewInfo = {}
		if filePath in viewDict:
			viewInfo = viewDict[filePath]

		viewInfo[SublimeSocketAPISettings.VIEW_ISEXIST] = eventParam[SublimeSocketAPISettings.REACTOR_VIEWKEY_ISEXIST]
		viewInfo[SublimeSocketAPISettings.VIEW_ID] = eventParam[SublimeSocketAPISettings.REACTOR_VIEWKEY_ID]
		viewInfo[SublimeSocketAPISettings.VIEW_BUFFERID] = eventParam[SublimeSocketAPISettings.REACTOR_VIEWKEY_BUFFERID]
		viewInfo[SublimeSocketAPISettings.VIEW_BASENAME] = filePath
		viewInfo[SublimeSocketAPISettings.VIEW_VNAME] = eventParam[SublimeSocketAPISettings.REACTOR_VIEWKEY_VNAME]
		viewInfo[SublimeSocketAPISettings.VIEW_SELF] = viewInstance

		# add
		viewDict[filePath] = viewInfo
		self.updateViewDict(viewDict)

	def runDeletion(self, eventParam):
		viewInstance = eventParam[SublimeSocketAPISettings.VIEW_SELF]
		filePath = eventParam[SublimeSocketAPISettings.REACTOR_VIEWKEY_BASENAME]

		viewDict = self.viewsDict()

		# delete
		if filePath in viewDict:
			del viewDict[filePath]
			self.setKV(SublimeSocketAPISettings.DICT_VIEWS, viewDict)


	## KVSControl
	def KVSControl(self, subCommandAndParam):
		if 1 < len(subCommandAndParam):
			return "KVSControl: too many subCommands. please set only one subCommand."


		subCommands = subCommandAndParam.keys()
		for key in subCommands:
			param = subCommandAndParam[key]

			# python-switch
			for case in PythonSwitch(key):
				if case(SublimeSocketAPISettings.KVS_SHOWALL):
					return self.showAll()
					break

				if case(SublimeSocketAPISettings.KVS_SHOWVALUE):
					return self.showValue(param)
					break

				if case(SublimeSocketAPISettings.KVS_REMOVEVALUE):
					return self.remove(param)
					break
					
				if case(SublimeSocketAPISettings.KVS_CLEAR):
					return self.clear()
					break

				if case():
					print("unknown KVS subcommand")
					break


	## return view dict
	def viewsDict(self):
		viewsDict = self.kvs.get(SublimeSocketAPISettings.DICT_VIEWS)

		if viewsDict:
			return viewsDict
		else:
			return {}

	def updateViewDict(self, viewDict):
		self.setKV(SublimeSocketAPISettings.DICT_VIEWS, viewDict)

	## put key-value onto KeyValueStore
	def setKV(self, key, value):
		self.kvs.setKeyValue(key, value)


	## return None or object
	def getV(self, key):
		value = self.kvs.get(key)
		return value


	## exist or not. return bool
	def isExistOnKVS(self, key):
		if self.kvs.get(key):
			# print "isExistOnKVS true", self.kvs.get(key)
			return True
			
		else:
			# print "isExistOnKVS false", self.kvs.get(key)
			return False

	## return all key-value as string
	def showAll(self):
		if self.kvs.isEmpty():
			return "No Keys - Values. empty."

		v = self.kvs.items()
		printKV = []
		for kvTuple in v:
			kvsStr = str(kvTuple[0]) + " : " + str(kvTuple[1])+ "	/	"
			printKV.append(kvsStr)
		
		return "".join(printKV)


	## return single key-value as string
	def showValue(self, key):
		if not self.kvs.get(key):
			return str(False)
		
		kv = key + " : " + str(self.kvs.get(key))
		return str(kv)


	## clear all KVS contents
	def clear(self):
		self.kvs.clear()
		return str(True)
		

	def remove(self, key):
		result = self.kvs.remove(key)
		return str(result)



	def internal_detectViewPath(self, view):
		instances = []
		viewsDict = self.viewsDict()
		
		if viewsDict:
			for path in list(viewsDict):
				viewInstance = viewsDict[path][SublimeSocketAPISettings.VIEW_SELF]
				if view == viewInstance:
					return path

				instances.append(viewInstance)

		return None


	def internal_getViewAndPathFromViewOrName(self, params, viewParamKey, nameParamKey):
		view = None
		path = None

		if viewParamKey in params:
			view = params[viewParamKey]
			
			path = self.internal_detectViewPath(view)
			
				
		elif nameParamKey in params:
			name = params[nameParamKey]
			
			view = self.internal_detectViewInstance(name)
			path = self.internal_detectViewPath(view)

		if view and path:
			return (view, path)
		else:
			return (None, None)


	## get the target view-s information if params includes "filename.something" or some pathes represents filepath.
	def internal_detectViewInstance(self, name):
		viewDict = self.viewsDict()
		if viewDict:
			viewKeys = viewDict.keys()

			viewSearchSource = name

			# remove empty and 1 length string pattern.
			if not viewSearchSource or len(viewSearchSource) is 0:
				return None

			viewSearchSource = viewSearchSource.replace("\\", "&")
			viewSearchSource = viewSearchSource.replace("/", "&")

			# straight full match in viewSearchSource. "/aaa/bbb/ccc.d something..." vs "*********** /aaa/bbb/ccc.d ***********"
			for viewKey in viewKeys:
				# replace path-expression by component with &.
				viewSearchKey = viewKey.replace("\\", "&")
				viewSearchKey = viewSearchKey.replace("/", "&")

				if re.findall(viewSearchSource, viewSearchKey):
					return viewDict[viewKey][SublimeSocketAPISettings.VIEW_SELF]
			
			# partial match in viewSearchSource. "ccc.d" vs "********* ccc.d ************"
			for viewKey in viewKeys:
				viewBasename = viewDict[viewKey][SublimeSocketAPISettings.VIEW_BASENAME]
				if viewBasename in viewSearchSource:
					return viewDict[viewKey][SublimeSocketAPISettings.VIEW_SELF]

		# totally, return None and do nothing
		return None


## key-value pool
class KVS:
	def __init__(self):
		self.keyValueDict = {}


	## empty or not
	def isEmpty(self):
		if 0 == len(self.keyValueDict):
			return True
		else:
			return False

		
	## set (override if exist already)
	def setKeyValue(self, key, value):
		if key in self.keyValueDict:
			# print "overwritten:", key, "as:", value
			pass

		self.keyValueDict[key] = value
		return self.keyValueDict[key]


	## get value for key
	def get(self, key):
		if key in self.keyValueDict:
			return self.keyValueDict[key]


	## get all key-value
	def items(self):
		return self.keyValueDict.items()


	## remove key-value
	def remove(self, key):
		if self.get(key):
			del self.keyValueDict[key]
			return True
		else:
			print("no '", key, "' key exists in KVS.")
			return False


	## remove all keys and values
	def clear(self):
		self.keyValueDict.clear()
		return True
