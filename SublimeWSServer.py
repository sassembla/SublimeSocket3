# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import threading
import os

import socket, threading, string, time
from .SublimeWSClient import SublimeWSClient
from .SublimeSocketAPI import SublimeSocketAPI
from . import SublimeSocketAPISettings

import json
import uuid

import re

from .PythonSwitch import PythonSwitch


class SublimeWSServer:

	def __init__(self):
		self.clients = {}
		
		self.socket = ''
		self.host = ''
		self.port = ''

		self.listening = False
		self.kvs = KVS()
		self.api = SublimeSocketAPI(self)

		self.deletedRegionIdPool = []
		self.completions = []


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
			client = SublimeWSClient(self, identity)
			
			self.clients[identity] = client

			threading.Thread(target = client.handle, args = (conn,addr)).start()
				
		return 0
		

	## load settings and run in mainThread
	def loadSettings(self, results):
		settingCommands = sublime.load_settings("SublimeSocket.sublime-settings").get('loadSettings')
		for command in settingCommands:
			print("loadSettingsからのrunAPI", results)
			self.api.runAPI(command, None, None, results)

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
				view_file_name = view.file_name()

				# run if not scratch
				if view_file_name:
					viewParams = self.getSublimeViewInfo(
						view,
						SublimeSocketAPISettings.VIEW_SELF,
						SublimeSocketAPISettings.VIEW_ID,
						SublimeSocketAPISettings.VIEW_BUFFERID,
						SublimeSocketAPISettings.VIEW_PATH,
						SublimeSocketAPISettings.VIEW_BASENAME,
						SublimeSocketAPISettings.VIEW_VNAME,
						SublimeSocketAPISettings.VIEW_SELECTED
					)

					self.fireKVStoredItem(
						SublimeSocketAPISettings.REACTORTYPE_VIEW,
						SublimeSocketAPISettings.SS_EVENT_COLLECT, 
						viewParams,
						results
					)

					collectedViews.append(view_file_name)

		self.api.setResultsParams(results, self.collectViews, {"collected":collectedViews})
	
	
	## store region to viewDict-view in KVS
	def storeRegionToView(self, view, identity, region, line, message):
		key = view.file_name()

		specificViewDict = self.getV(SublimeSocketAPISettings.DICT_VIEWS)[key]

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

		viewDict = self.getV(SublimeSocketAPISettings.DICT_VIEWS)
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

		if SublimeSocketAPISettings.REACTOR_REPLACEFROMTO in params:
			reactDict[SublimeSocketAPISettings.REACTOR_REPLACEFROMTO] = params[SublimeSocketAPISettings.REACTOR_REPLACEFROMTO]

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


	def runReactor(self, reactorType, reactorDict, eventParam, results):
		# reactorTypeで判別、viewの場合は引数の暗黙変換を行う。
		for case in PythonSwitch(reactorType):
			if case(SublimeSocketAPISettings.REACTORTYPE_EVENT):
				# do nothing
				break

			if case(SublimeSocketAPISettings.REACTORTYPE_VIEW):
				# add view param for react.
				assert SublimeSocketAPISettings.REACTOR_VIEWKEY_VIEWSELF in eventParam, "reactorType:view require 'view' info."
				reactorDict[SublimeSocketAPISettings.REACTOR_REPLACEFROMTO] = {
					SublimeSocketAPISettings.REACTOR_VIEWKEY_VIEWSELF:SublimeSocketAPISettings.REACTOR_VIEWKEY_VIEWSELF,
					SublimeSocketAPISettings.REACTOR_VIEWKEY_SELECTED:SublimeSocketAPISettings.REACTOR_VIEWKEY_SELECTED
					}
				break

		self.api.runAllSelector(reactorDict, eventParam, results)


	# ready for react completion. old-loading completion will ignore.
	def prepareCompletion(self, identity):
		print("prepareCompletion!!!!!!!!!!!!")
		# if SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS in self.temporaryReactorDict:
		# 	del self.temporaryReactorDict[SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS]

		# # re-generate completions dictionaries
		# self.temporaryReactorDict[SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS] = {}
		# self.temporaryReactorDict[SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS][identity] = {}

		# # reset current completing data
		# self.temporaryReactorDict[SublimeSocketAPISettings.REACTIVE_CURRENT_COMPLETINGS] = {}


	def updateCompletion(self, identity, completions, lockcount):
		print("updateCompletion!!!!!!!!")
		# if SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS in self.temporaryReactorDict:
		# 	if identity in self.temporaryReactorDict[SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS]:
		# 		# set completion
		# 		self.temporaryReactorDict[SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS][identity] = completions

		# 		# set current completing data
		# 		self.temporaryReactorDict[SublimeSocketAPISettings.REACTIVE_CURRENT_COMPLETINGS] = {
		# 			SublimeSocketAPISettings.RUNCOMPLETION_ID:identity,
		# 			SublimeSocketAPISettings.RUNCOMPLETION_LOCKCOUNT:lockcount
		# 		}

	def getCurrentCompletingsDict(self):
		print("getCurrentCompletingsDict!!!!!!!!!!!!!!")
		# if SublimeSocketAPISettings.REACTIVE_CURRENT_COMPLETINGS in self.temporaryReactorDict:
		# 	return self.temporaryReactorDict[SublimeSocketAPISettings.REACTIVE_CURRENT_COMPLETINGS]
		return {}

	def isLoadingCompletion(self, identity):
		print("isLoadingCompletion!!!!!!!!!!!!!!!")
		# if SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS in self.temporaryReactorDict:
		# 	currentCompletionDict = self.temporaryReactorDict[SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS]
		# 	if identity in currentCompletionDict:
		# 		return True

		return False
			

	## emit event if params matches the regions that sink in view
	def containsRegionsInKVS(self, params, results):
		
		if self.isExistOnKVS(SublimeSocketAPISettings.DICT_VIEWS):
			viewDict = self.getV(SublimeSocketAPISettings.DICT_VIEWS)

			

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
					
					print("なんでわざわざイベント扱いしてるんだろう。selectorじゃダメなのかな。")
					self.fireKVStoredItem(SublimeSocketAPISettings.REACTORTYPE_VIEW, emit, regionInfo, results)
					
					if SublimeSocketAPISettings.CONTAINSREGIONS_DEBUG in params:
						debug = params[SublimeSocketAPISettings.CONTAINSREGIONS_DEBUG]

						if debug:
							message = regionInfo[SublimeSocketAPISettings.APPENDREGION_MESSAGE]

							messageDict = {}
							messageDict[SublimeSocketAPISettings.SHOWSTATUSMESSAGE_MESSAGE] = message
							
							self.api.runAPI(SublimeSocketAPISettings.API_I_SHOWSTATUSMESSAGE, messageDict, None, results)
							self.api.printout(message)
							
				[emitRegionMatchEvent(region) for region in regionIdentitiesList]
				

	## show current status & connectionIds
	def showCurrentStatusAndConnections(self):
		print("ss: server host:", self.host, "	port:", self.port)
		
		print("ss: connections:")
		for client in self.clients:
			print("	", client)


	## depends on sublime-view method
	def getSublimeViewInfo(self, viewInstance, viewKey, viewIdKey, viewBufferIdKey, viewPathKey, viewBaseNameKey, viewVNameKey, viewSelectedKey):
		return {
			viewKey : viewInstance,
			viewIdKey: viewInstance.id(),
			viewBufferIdKey: viewInstance.buffer_id(),
			viewPathKey: viewInstance.file_name(),
			viewBaseNameKey: os.path.basename(viewInstance.file_name()),
			viewVNameKey: viewInstance.name(),
			viewSelectedKey: viewInstance.sel()
		}


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
					
					if self.shouldDelay(reactorsDict, eventName, target):
						pass
					else:
						self.api.runAllSelector(reactDict, eventParam, results)

		elif eventName in SublimeSocketAPISettings.REACTIVE_FOUNDATION_EVENT:
			if reactorsDict and eventName in reactorsDict:
				self.runFoundationEvent(eventName, eventParam, reactorsDict[eventName], results)
				
		else:
			if eventName in SublimeSocketAPISettings.VIEW_EVENTS_RENEW:
				self.runRenew(eventParam)

			if eventName in SublimeSocketAPISettings.VIEW_EVENTS_DEL:
				self.runDeletion(eventParam)

			# if reactor exist, run all selectors. not depends on "target".
			if reactorsDict and eventName in reactorsDict:
				reactorDict = reactorsDict[eventName]
				for reactorKey in list(reactorDict):
					reactorParams = reactorDict[reactorKey]

					if self.shouldDelay(reactorsDict, eventName, reactorKey):
						pass
					else:
						self.runReactor(reactorType, reactorParams, eventParam, results)


	## should delay = pass or not.
	def shouldDelay(self, reactorsDict, name, target):
		currentTime = round(int(time.time()*1000))
		
		delay = reactorsDict[name][target][SublimeSocketAPISettings.REACTOR_DELAY]

		if delay is 0:
			return False

		else:
			reactorsLogDict = self.getV(SublimeSocketAPISettings.DICT_REACTORSLOG)
			log = reactorsLogDict[name][target]
			
			if log:
				latest = log[SublimeSocketAPISettings.REACTORSLOG_LATEST]
				print(SublimeSocketAPISettings.REACTORSLOG_LATEST, latest, "sub = ", (delay + latest - currentTime))
				if 0 > (delay + latest - currentTime):
					reactorsLogDict[name][target][SublimeSocketAPISettings.REACTORSLOG_LATEST]	= currentTime
					self.setKV(SublimeSocketAPISettings.DICT_REACTORSLOG, reactorsLogDict)
					return True
					
			else:
				reactorsLogDict[name][target][SublimeSocketAPISettings.REACTORSLOG_LATEST]	= currentTime
				self.setKV(SublimeSocketAPISettings.DICT_REACTORSLOG, reactorsLogDict)
				return True

		return False

	## return param
	def getKVStoredItem(self, eventName, eventParam=None):
		if eventName in SublimeSocketAPISettings.REACTIVE_REACTABLE_EVENT:
			# if SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS in self.temporaryReactorDict:
			# 	for completionsKey in self.temporaryReactorDict[SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS]:
			# 		return self.temporaryReactorDict[SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS][completionsKey]
			pass


	def runRenew(self, eventParam):
		viewInstance = eventParam[SublimeSocketAPISettings.VIEW_SELF]
		filePath = eventParam[SublimeSocketAPISettings.REACTOR_VIEWKEY_PATH]

		if viewInstance.is_scratch():
			# print "scratch buffer."
			pass
			
		elif not filePath:
			# print "no path"
			pass

		else:
			viewDict = {}
			
			# update or append if exist.
			if self.isExistOnKVS(SublimeSocketAPISettings.DICT_VIEWS):
				viewDict = self.getV(SublimeSocketAPISettings.DICT_VIEWS)

			# create
			else:	
				pass


			viewInfo = {}
			if filePath in viewDict:
				viewInfo = viewDict[filePath]

			viewInfo[SublimeSocketAPISettings.VIEW_ID] = eventParam[SublimeSocketAPISettings.REACTOR_VIEWKEY_ID]
			viewInfo[SublimeSocketAPISettings.VIEW_BUFFERID] = eventParam[SublimeSocketAPISettings.REACTOR_VIEWKEY_BUFFERID]
			viewInfo[SublimeSocketAPISettings.VIEW_BASENAME] = filePath
			viewInfo[SublimeSocketAPISettings.VIEW_VNAME] = eventParam[SublimeSocketAPISettings.REACTOR_VIEWKEY_VNAME]
			viewInfo[SublimeSocketAPISettings.VIEW_SELF] = viewInstance
			
			# add
			viewDict[filePath] = viewInfo
			self.setKV(SublimeSocketAPISettings.DICT_VIEWS, viewDict)

	def runDeletion(self, eventParam):
		viewInstance = eventParam[SublimeSocketAPISettings.VIEW_SELF]
		filePath = eventParam[SublimeSocketAPISettings.REACTOR_VIEWKEY_BASENAME]

		viewDict = {}
		
		# get view-dictionary if exist.
		if self.isExistOnKVS(SublimeSocketAPISettings.DICT_VIEWS):
			viewDict = self.getV(SublimeSocketAPISettings.DICT_VIEWS)

		# create
		else:	
			pass

		# delete
		if filePath in viewDict:
			del viewDict[filePath]
			self.setKV(SublimeSocketAPISettings.DICT_VIEWS, viewDict)

	def runFoundationEvent(self, eventName, eventParam, reactors, results):
		for case in PythonSwitch(eventName):
			if case(SublimeSocketAPISettings.SS_FOUNDATION_NOVIEWFOUND):
				self.foundation_noViewFound(reactors, eventParam, results)
				break

			if case(SublimeSocketAPISettings.SS_FOUNDATION_RUNWITHBUFFER):
				self.foundation_runWithBuffer(reactors, eventParam, results)
				break


	def foundation_noViewFound(self, reactDicts, eventParam, results):
		for target in list(reactDicts):
			reactDict = reactDicts[target]
			
			self.api.runAllSelector(reactDict, eventParam, results)


	def foundation_runWithBuffer(self, reactDicts, eventParam, results):
		for currentDict in reactDicts:
			# get data from view-buffer
			
			bodyView = eventParam[SublimeSocketAPISettings.F_RUNWITHBUFFER_VIEW]
			
			currentRegion = sublime.Region(0, bodyView.size())

			body = bodyView.substr(bodyView.word(currentRegion))
			path = bodyView.file_name()
			path = path.replace(":","&").replace("\\", "/")
			# get line num
			sel = bodyView.sel()[0]
			(row, col) = bodyView.rowcol(sel.a)
			rowColStr = str(row)+","+str(col)

			currentReactDict = reactDicts[currentDict].copy()
			
			# append 'body' 'path' param from buffer
			currentEventParam = {}
			currentEventParam[SublimeSocketAPISettings.F_RUNWITHBUFFER_VIEW] = bodyView
			currentEventParam[SublimeSocketAPISettings.F_RUNWITHBUFFER_ID] = str(uuid.uuid4())
			currentEventParam[SublimeSocketAPISettings.F_RUNWITHBUFFER_BODY] = body
			currentEventParam[SublimeSocketAPISettings.F_RUNWITHBUFFER_PATH] = path
			currentEventParam[SublimeSocketAPISettings.F_RUNWITHBUFFER_ROWCOL] = rowColStr

			self.api.runAllSelector(currentReactDict, currentEventParam, results)


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
	def viewDict(self):
		return self.kvs.get(SublimeSocketAPISettings.DICT_VIEWS)


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


