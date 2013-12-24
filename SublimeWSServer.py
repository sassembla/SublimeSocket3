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

SERVER_INTERVAL_SEC = 2000

class SublimeWSServer:

	def __init__(self):
		self.clients = {}
		
		self.socket = ''
		self.host = ''
		self.port = ''

		self.listening = False
		self.kvs = KVS()
		self.api = SublimeSocketAPI(self)
		self.temporaryEventDict = {}

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

		# start serverControlIntervals
		# self.intervals(), SERVER_INTERVAL_SEC)

		# load settings
		results = self.api.initResult(str(uuid.uuid4()))
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


	## interval
	def intervals(self):
		# check KVS for "eventListen", and the other APIs.
		
		for key in SublimeSocketAPISettings.INTERVAL_DEPEND_APIS:
			pass
			# self.api.runOnInterval(self.getV(key))

		# sublime.status_message("params:\n".join(debugArray)), 0)
		
		# loop
		self.intervals()
		

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
		resultIdentity = str(uuid.uuid4())

		def call(identity):
			results = self.api.initResult(identity)
			self.api.parse(apiData, currentClient, results)
		
		call(resultIdentity)

		
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
	def collectViews(self):
		for views in [window.views() for window in sublime.windows()]:
			for view in views:
				self.fireKVStoredItem(SublimeSocketAPISettings.SS_EVENT_COLLECT, 
					{SublimeSocketAPISettings.VIEW_SELF:view}
				)
	
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
	def deleteAllRegionsInAllView(self):
		viewDict = self.getV(SublimeSocketAPISettings.DICT_VIEWS)
		
		deletes = []

		def eraseAllRegionsAtViewDict(viewDictValue):
		
			if SublimeSocketAPISettings.SUBDICT_REGIONS in viewDictValue:
				
				viewInstance = viewDictValue[SublimeSocketAPISettings.VIEW_SELF]
				regionsDict = viewDictValue[SublimeSocketAPISettings.SUBDICT_REGIONS]
				
				if regionsDict:
					for regionIdentity in regionsDict.keys():
						viewInstance.erase_regions(regionIdentity)
						print("regionIdentity", regionIdentity)
						deletes.append(regionIdentity)

						viewDictValue[SublimeSocketAPISettings.SUBARRAY_DELETED_REGIONS][regionIdentity] = 1
				
					deletedRegions = viewDictValue[SublimeSocketAPISettings.SUBARRAY_DELETED_REGIONS]

					for deletedRegionIdentity in deletedRegions.keys(): 
						if deletedRegionIdentity in regionsDict:
							del regionsDict[deletedRegionIdentity]

				regionsDict = {}
				
		if viewDict:
			list(map(eraseAllRegionsAtViewDict, viewDict.values()))

		return deletes

	## generate thread per selector. or add
	def setOrAddReactor(self, params):
		target = params[SublimeSocketAPISettings.REACTOR_TARGET]
		event = params[SublimeSocketAPISettings.REACTOR_EVENT]
		selectorsArray = params[SublimeSocketAPISettings.REACTOR_SELECTORS]

		if event in SublimeSocketAPISettings.REACTIVE_RESERVED_INTERVAL_EVENT:
			assert SublimeSocketAPISettings.REACTOR_INTERVAL in params, "this type of event require 'interval' param."

		# check event kind
		# delete when set the reactor of the event.
		if event in self.temporaryEventDict:
			del self.temporaryEventDict[event]
		
		# set default interval
		interval = 0
		if SublimeSocketAPISettings.REACTOR_INTERVAL in params:
			interval = params[SublimeSocketAPISettings.REACTOR_INTERVAL]

		reactorsDict = {}
		if self.isExistOnKVS(SublimeSocketAPISettings.DICT_REACTORS):
			reactorsDict = self.getV(SublimeSocketAPISettings.DICT_REACTORS)

		reactDict = {}
		reactDict[SublimeSocketAPISettings.REACTOR_SELECTORS] = selectorsArray
		reactDict[SublimeSocketAPISettings.REACTOR_INTERVAL] = interval

		if SublimeSocketAPISettings.REACTOR_REPLACEFROMTO in params:
			reactDict[SublimeSocketAPISettings.REACTOR_REPLACEFROMTO] = params[SublimeSocketAPISettings.REACTOR_REPLACEFROMTO]

		# already set or not-> spawn dictionary for event.
		if not event in reactorsDict:			
			reactorsDict[event] = {}

		if not target in reactorsDict[event]:
			# store reactor			
			reactorsDict[event][target] = reactDict
			self.setKV(SublimeSocketAPISettings.DICT_REACTORS, reactorsDict)
			
			if 0 < interval:
				# spawn event-loop for event execution
				self.eventIntervals(target, event, selectorsArray, interval)

		return reactorsDict
		

	def removeAllReactors(self):
		reactorsDict = {}
		if self.isExistOnKVS(SublimeSocketAPISettings.DICT_REACTORS):
			reactorsDict = self.getV(SublimeSocketAPISettings.DICT_REACTORS)

		deletedReactorsDict = reactorsDict
		self.setKV(SublimeSocketAPISettings.DICT_REACTORS, {})

		return reactorsDict


	## interval execution for event
	def eventIntervals(self, target, event, selectorsArray, interval):
		reactorsDict = self.getV(SublimeSocketAPISettings.DICT_REACTORS)

		# return if empty
		if not reactorsDict:
			return

		# if exist, continue
		if not event in reactorsDict:
			return

		if not target in reactorsDict[event]:
			return

		if reactorsDict[event][target]:
			
			reactorDict = reactorsDict[event][target]

			if event in self.temporaryEventDict:
				# get latest event
				eventParam = self.temporaryEventDict[event]
				
				# consume event
				del self.temporaryEventDict[event]#

				# run all selector
				self.runAllSelector(reactorDict, selectorsArray, eventParam)

			# continue
			threading.Timer(interval/1000, self.eventIntervals, [target, event, selectorsArray, interval]).start()

	# ready for react completion. old-loading completion will ignore.
	def prepareCompletion(self, identity):
		if SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS in self.temporaryEventDict:
			del self.temporaryEventDict[SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS]

		# re-generate completions dictionaries
		self.temporaryEventDict[SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS] = {}
		self.temporaryEventDict[SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS][identity] = {}

		# reset current completing data
		self.temporaryEventDict[SublimeSocketAPISettings.REACTIVE_CURRENT_COMPLETINGS] = {}


	def updateCompletion(self, identity, completions, lockcount):
		if SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS in self.temporaryEventDict:
			if identity in self.temporaryEventDict[SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS]:
				# set completion
				self.temporaryEventDict[SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS][identity] = completions

				# set current completing data
				self.temporaryEventDict[SublimeSocketAPISettings.REACTIVE_CURRENT_COMPLETINGS] = {
					SublimeSocketAPISettings.RUNCOMPLETION_ID:identity,
					SublimeSocketAPISettings.RUNCOMPLETION_LOCKCOUNT:lockcount
				}

	def getCurrentCompletingsDict(self):
		if SublimeSocketAPISettings.REACTIVE_CURRENT_COMPLETINGS in self.temporaryEventDict:
			return self.temporaryEventDict[SublimeSocketAPISettings.REACTIVE_CURRENT_COMPLETINGS]
		return {}

	def isLoadingCompletion(self, identity):
		if SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS in self.temporaryEventDict:
			currentCompletionDict = self.temporaryEventDict[SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS]
			if identity in currentCompletionDict:
				return True

		return False

	# run user-defined event.
	def runOrSetUserDefinedEvent(self, eventName, eventParam, reactorsDict):
		# emit now or set to fire with interval
		if SublimeSocketAPISettings.REACTOR_INTERVAL in reactorsDict:
			self.temporaryEventDict[eventName] = eventParam
			return

		# emit now
		target = eventParam[SublimeSocketAPISettings.REACTOR_TARGET]
		reactDict = reactorsDict[eventName][target]
		
		selector = reactDict[SublimeSocketAPISettings.REACTOR_SELECTORS]

		self.runAllSelector(reactDict, selector, eventParam)
	def runAllSelector(self, reactorDict, selectorsArray, eventParam):
		def runForeachAPI(selector):
			# {u'broadcastMessage': {u'message': u"text's been modified!"}}

			for commands in selector.keys():
				command = commands
				
			params = selector[command]

			# print "params", params, "command", command
			currentParams = params.copy()
			# replace parameters if key 'replace' exist
			if SublimeSocketAPISettings.REACTOR_REPLACEFROMTO in reactorDict:
				for fromKey in reactorDict[SublimeSocketAPISettings.REACTOR_REPLACEFROMTO].keys():
					toKey = reactorDict[SublimeSocketAPISettings.REACTOR_REPLACEFROMTO][fromKey]
					
					# replace or append
					currentParams[toKey] = eventParam[fromKey]

			print("runAllSelector内でのrunAPI？")
			self.api.runAPI(command, currentParams)

		[runForeachAPI(selector) for selector in selectorsArray]



	## emit event if params matches the regions that sink in view
	def containsRegions(self, params, results=None):
		if self.isExistOnKVS(SublimeSocketAPISettings.DICT_VIEWS):
			viewDict = self.getV(SublimeSocketAPISettings.DICT_VIEWS)

			assert SublimeSocketAPISettings.CONTAINSREGIONS_VIEW in params, "containsRegions require 'view' param"
			assert SublimeSocketAPISettings.CONTAINSREGIONS_TARGET in params, "containsRegions require 'target' param"
			assert SublimeSocketAPISettings.CONTAINSREGIONS_EMIT in params, "containsRegions require 'emit' param"
			

			# specify regions that are selected.
			viewInstance = params[SublimeSocketAPISettings.CONTAINSREGIONS_VIEW]

			viewId = viewInstance.file_name()

			# return if view not exist(include ST's console)
			if not viewId in viewDict:
				return

			
			viewInfoDict = viewDict[viewId]
			if SublimeSocketAPISettings.SUBDICT_REGIONS in viewInfoDict:
				regionsDicts = viewInfoDict[SublimeSocketAPISettings.SUBDICT_REGIONS]
				selectedRegionSet = viewInstance.sel()
				
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
					
					self.fireKVStoredItem(emit, regionInfo)
					
					if SublimeSocketAPISettings.CONTAINSREGIONS_DEBUG in params:
						debug = params[SublimeSocketAPISettings.CONTAINSREGIONS_DEBUG]

						if debug:
							message = regionInfo[SublimeSocketAPISettings.APPENDREGION_MESSAGE]

							messageDict = {}
							messageDict[SublimeSocketAPISettings.SHOWSTATUSMESSAGE_MESSAGE] = message
							print("containsRegionsからのrunAPI", results)
							self.api.runAPI(SublimeSocketAPISettings.API_I_SHOWSTATUSMESSAGE, messageDict)
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
	def fireKVStoredItem(self, eventName, eventParam=None):
		# print("fireKVStoredItem eventListen!", eventName,"eventParam",eventParam)

		# event listener adopt
		if eventName in SublimeSocketAPISettings.REACTIVE_RESERVED_INTERVAL_EVENT:
			# store data to temporary.
			self.temporaryEventDict[eventName] = eventParam


		# run when the event occured adopt. start with specific "user-defined" event identity that defined as REACTIVE_PREFIX_USERDEFINED_EVENT.
		if eventName.startswith(SublimeSocketAPISettings.REACTIVE_PREFIX_USERDEFINED_EVENT):
			
			# emit now if exist
			reactorsDict = self.getV(SublimeSocketAPISettings.DICT_REACTORS)
			
			# if exist, continue
			if reactorsDict and eventName in reactorsDict:
				# interval-set or not
				self.runOrSetUserDefinedEvent(eventName, eventParam, reactorsDict)


		# run when the foundation-event occured adopt
		if eventName in SublimeSocketAPISettings.REACTIVE_FOUNDATION_EVENT:
			# emit now if exist
			reactorsDict = self.getV(SublimeSocketAPISettings.DICT_REACTORS)
			
			# if exist, continue
			if reactorsDict and eventName in reactorsDict:
				self.runFoundationEvent(eventName, eventParam, reactorsDict)


		# viewCollector "renew" will react
		if eventName in SublimeSocketAPISettings.VIEW_EVENTS_RENEW:
			viewInstance = eventParam[SublimeSocketAPISettings.VIEW_SELF]

			if viewInstance.is_scratch():
				# print "scratch buffer."
				pass
				
			elif not viewInstance.file_name():
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

				filePath = viewInstance.file_name()

				viewInfo = {}
				if filePath in viewDict:
					viewInfo = viewDict[filePath]

				viewInfo[SublimeSocketAPISettings.VIEW_ID] = viewInstance.id()
				viewInfo[SublimeSocketAPISettings.VIEW_BUFFERID] = viewInstance.buffer_id()
				viewInfo[SublimeSocketAPISettings.VIEW_BASENAME] = os.path.basename(viewInstance.file_name())
				viewInfo[SublimeSocketAPISettings.VIEW_VNAME] = viewInstance.name()
				viewInfo[SublimeSocketAPISettings.VIEW_SELF] = viewInstance
				
				# add
				viewDict[filePath] = viewInfo
				self.setKV(SublimeSocketAPISettings.DICT_VIEWS, viewDict)


		# viewCollector "del" will react
		if eventName in SublimeSocketAPISettings.VIEW_EVENTS_DEL:
			viewInstance = eventParam[SublimeSocketAPISettings.VIEW_SELF]

			viewDict = {}
			
			# get view-dictionary if exist.
			if self.isExistOnKVS(SublimeSocketAPISettings.DICT_VIEWS):
				viewDict = self.getV(SublimeSocketAPISettings.DICT_VIEWS)

			# create
			else:	
				return

			filePath = viewInstance.file_name()

			# delete
			if filePath in viewDict:
				del viewDict[filePath]
				self.setKV(SublimeSocketAPISettings.DICT_VIEWS, viewDict)


	## return param
	def getKVStoredItem(self, eventName, eventParam=None):
		if eventName in SublimeSocketAPISettings.REACTIVE_REACTABLE_EVENT:
			if SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS in self.temporaryEventDict:
				for completionsKey in self.temporaryEventDict[SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS]:
					return self.temporaryEventDict[SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS][completionsKey]
		

	def runFoundationEvent(self, eventName, eventParam, reactorsDict):
		for case in PythonSwitch(eventName):
			if case(SublimeSocketAPISettings.SS_FOUNDATION_NOVIEWFOUND):
				reactDict = reactorsDict[eventName][SublimeSocketAPISettings.FOUNDATIONREACTOR_TARGET_DEFAULT]
			
				selector = reactDict[SublimeSocketAPISettings.REACTOR_SELECTORS]

				self.runAllSelector(reactDict, selector, eventParam)
				break

			if case(SublimeSocketAPISettings.SS_FOUNDATION_RUNWITHBUFFER):				
				for currentDict in reactorsDict[eventName]:
					# get data from view-buffer
					bodyView = eventParam[SublimeSocketAPISettings.F_RUNWITHBUFFER_VIEW]

					currentRegion = sublime.Region(0, 0)

					# continue until size not changed.
					before = -1
					count = 1

					while True:
						if currentRegion.b == before:
							break

						before = currentRegion.b
						currentRegion = bodyView.word(sublime.Region(0, SublimeSocketAPISettings.SIZE_OF_BUFFER * count))

						count = count + 1

					body = bodyView.substr(bodyView.word(currentRegion))
					path = bodyView.file_name()
					path = path.replace(":","&").replace("\\", "/")
					# get line num
					sel = bodyView.sel()[0]
					(row, col) = bodyView.rowcol(sel.a)
					rowColStr = str(row)+","+str(col)

					reactDict = reactorsDict[eventName][currentDict].copy()
					currentSelector = reactDict[SublimeSocketAPISettings.REACTOR_SELECTORS]
					
					# append 'body' 'path' param from buffer
					currentEventParam = {}
					currentEventParam[SublimeSocketAPISettings.F_RUNWITHBUFFER_VIEW] = bodyView
					currentEventParam[SublimeSocketAPISettings.F_RUNWITHBUFFER_ID] = str(uuid.uuid4())
					currentEventParam[SublimeSocketAPISettings.F_RUNWITHBUFFER_BODY] = body
					currentEventParam[SublimeSocketAPISettings.F_RUNWITHBUFFER_PATH] = path
					currentEventParam[SublimeSocketAPISettings.F_RUNWITHBUFFER_ROWCOL] = rowColStr


					self.runAllSelector(reactDict, currentSelector, currentEventParam)

				break

			if case():
				print("unknown foundation api", command)
				break


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


