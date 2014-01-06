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
						SublimeSocketAPISettings.VIEW_VNAME
					)

					self.fireKVStoredItem(
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
		# delete if already set the reactor of the event.
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
				self.api.runAllSelector(reactorDict, selectorsArray, eventParam, self.api.initResult("eventIntervals:"+str(uuid.uuid4())))

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
	def runOrSetUserDefinedEvent(self, eventName, eventParam, reactorsDict, results):
		# emit now or ready to fire after interval
		if SublimeSocketAPISettings.REACTOR_INTERVAL in reactorsDict:
			self.temporaryEventDict[eventName] = eventParam
			return

		# emit now
		target = eventParam[SublimeSocketAPISettings.REACTOR_TARGET]
		reactDict = reactorsDict[eventName][target]
		
		selector = reactDict[SublimeSocketAPISettings.REACTOR_SELECTORS]
		
		self.api.runAllSelector(reactDict, selector, eventParam, results)

	# run event.
	def runOrSetEvent(self, eventName, eventParam, reactorsDict, results):
		# emit now or ready to fire after interval
		if SublimeSocketAPISettings.REACTOR_INTERVAL in reactorsDict:
			self.temporaryEventDict[eventName] = eventParam
			return

		# emit now
		reactDicts = reactorsDict[eventName]
		for reactDictKey in list(reactDicts):
			reactDict = reactDicts[reactDictKey]

			selector = reactDict[SublimeSocketAPISettings.REACTOR_SELECTORS]

			self.api.runAllSelector(reactDict, selector, eventParam, results)


	## emit event if params matches the regions that sink in view
	def containsRegionsInKVS(self, params, results):
		assert SublimeSocketAPISettings.CONTAINSREGIONS_VIEW in params, "containsRegions require 'view' param"
		assert SublimeSocketAPISettings.CONTAINSREGIONS_TARGET in params, "containsRegions require 'target' param"
		assert SublimeSocketAPISettings.CONTAINSREGIONS_EMIT in params, "containsRegions require 'emit' param"
		
		if self.isExistOnKVS(SublimeSocketAPISettings.DICT_VIEWS):
			viewDict = self.getV(SublimeSocketAPISettings.DICT_VIEWS)

			

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
					
					self.fireKVStoredItem(emit, regionInfo, results)
					
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
	def getSublimeViewInfo(self, viewInstance, viewKey, viewIdKey, viewBufferIdKey, viewPathKey, viewBaseNameKey, viewVNameKey):
		return {
			viewKey : viewInstance,
			viewIdKey: viewInstance.id(),
			viewBufferIdKey: viewInstance.buffer_id(),
			viewPathKey: viewInstance.file_name(),
			viewBaseNameKey: os.path.basename(viewInstance.file_name()),
			viewVNameKey: viewInstance.name()
		}


	## input to sublime from server.
	# fire event in KVS, if exist.
	def fireKVStoredItem(self, eventName, eventParam, results):

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
				self.runOrSetUserDefinedEvent(eventName, eventParam, reactorsDict, results)


		# run when the foundation-event occured adopt
		if eventName in SublimeSocketAPISettings.REACTIVE_FOUNDATION_EVENT:
			# emit now if exist
			reactorsDict = self.getV(SublimeSocketAPISettings.DICT_REACTORS)
			
			# if exist, continue
			if reactorsDict and eventName in reactorsDict:
				self.runFoundationEvent(eventName, eventParam, reactorsDict, results)


		# viewCollector "renew" will react
		if eventName in SublimeSocketAPISettings.VIEW_EVENTS_RENEW:
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

			# run reactor if set
			reactorsDict = self.getV(SublimeSocketAPISettings.DICT_REACTORS)
			
			# if exist, continue
			if reactorsDict and eventName in reactorsDict:
				# interval-set or not
				self.runOrSetEvent(eventName, eventParam, reactorsDict, results)


		# viewCollector "del" will react
		if eventName in SublimeSocketAPISettings.VIEW_EVENTS_DEL:
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

			# run reactor if set
			reactorsDict = self.getV(SublimeSocketAPISettings.DICT_REACTORS)
			
			# if exist, continue
			if reactorsDict and eventName in reactorsDict:
				# interval-set or not
				self.runOrSetEvent(eventName, eventParam, reactorsDict, results)



	## return param
	def getKVStoredItem(self, eventName, eventParam=None):
		if eventName in SublimeSocketAPISettings.REACTIVE_REACTABLE_EVENT:
			if SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS in self.temporaryEventDict:
				for completionsKey in self.temporaryEventDict[SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS]:
					return self.temporaryEventDict[SublimeSocketAPISettings.REACTABLE_EVENT_ON_QUERY_COMPLETIONS][completionsKey]
		

	def runFoundationEvent(self, eventName, eventParam, reactorsDict, results=None):

		for case in PythonSwitch(eventName):
			if case(SublimeSocketAPISettings.SS_FOUNDATION_NOVIEWFOUND):
				reactDicts = reactorsDict[eventName]

				for target in list(reactDicts):
					reactDict = reactDicts[target]
					
					selector = reactDict[SublimeSocketAPISettings.REACTOR_SELECTORS]
					self.api.runAllSelector(reactDict, selector, eventParam, results)

				break

			if case(SublimeSocketAPISettings.SS_FOUNDATION_RUNWITHBUFFER):				
				for currentDict in reactorsDict[eventName]:
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

					reactDict = reactorsDict[eventName][currentDict].copy()
					currentSelector = reactDict[SublimeSocketAPISettings.REACTOR_SELECTORS]
					
					# append 'body' 'path' param from buffer
					currentEventParam = {}
					currentEventParam[SublimeSocketAPISettings.F_RUNWITHBUFFER_VIEW] = bodyView
					currentEventParam[SublimeSocketAPISettings.F_RUNWITHBUFFER_ID] = str(uuid.uuid4())
					currentEventParam[SublimeSocketAPISettings.F_RUNWITHBUFFER_BODY] = body
					currentEventParam[SublimeSocketAPISettings.F_RUNWITHBUFFER_PATH] = path
					currentEventParam[SublimeSocketAPISettings.F_RUNWITHBUFFER_ROWCOL] = rowColStr


					self.api.runAllSelector(reactDict, currentSelector, currentEventParam, results)

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


