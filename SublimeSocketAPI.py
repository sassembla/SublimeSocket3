# -*- coding: utf-8 -*-
import sublime, sublime_plugin

from . import SublimeWSSettings
import json

from .SublimeWSEncoder import SublimeWSEncoder
from . import SublimeSocketAPISettings

import subprocess
import shlex
import os
import time

import re
from functools import reduce

from .PythonSwitch import PythonSwitch
import uuid


MY_PLUGIN_PATHNAME = os.path.split(os.path.dirname(os.path.realpath(__file__)))[1]


## API Parse the action
class SublimeSocketAPI:
	def __init__(self, server):
		self.server = server
		self.encoder = SublimeWSEncoder()

		self.isTesting = False
		self.testResults = []

		self.testPassedCount = 0
		self.testFailedCount = 0

		self.counts = {}

		self.setSublimeSocketWindowBasePath(None)
		

	## initialize results as the part of testResults.
	def initResult(self, resultIdentity):
		initializedResults = {resultIdentity:{}}
		self.testResults.append(initializedResults)

		return self.testResults[-1]

	def setResultsParams(self, results, apiFunc, value):
		if not self.isTesting:
			return results

		if not results:
			return results

		# only one key capable.
		assert len(results) == 1, "in setResultsParams, too much keys found."
		apiFuncIdentity = (apiFunc.__name__, str(uuid.uuid4()))

		for key in results:
			results[key][apiFuncIdentity] = value
			return results

	def addInnerResult(self, results, innerResults):
		for key in results:
			results[key] = innerResults
			return results

	def resultBody(self, results):
		for key in results:
			return results[key]
			
		return {}


	## Parse the API command
	def parse(self, data, client=None, results=None):
			
		# SAMPLE: inputIdentity:{"id":"537d5da6-ce7d-42f0-387b-d9c606465dbb"}->showAlert...
		commands = data.split(SublimeSocketAPISettings.API_CONCAT_DELIM)

		# command and param  SAMPLE:		inputIdentity:{"id":"537d5da6-ce7d-42f0-387b-d9c606465dbb"}
		for commandIdentityAndParams in commands :
			command_params = commandIdentityAndParams.split(SublimeSocketAPISettings.API_COMMAND_PARAMS_DELIM, 1)
			command = command_params[0]

			params = ''
			if 1 < len(command_params):
				try:
					data = command_params[1].replace("\r\n", "\n")
					data = data.replace("\r", "\n")
					data = data.replace("\n", "\\n")
					data = data.replace("\t", "	")
					params = json.loads(data)
				except Exception as e:
					print("JSON parse error", e, "source = ", command_params[1])
					return
					
			parseResult = self.runAPI(command, params, client, results)

			if SublimeSocketAPISettings.PARSERESULT_SWITCH in parseResult:
				resultKey = list(results)[0]
				results[resultKey] = {}
		
		
		return results


	def innerParse(self, data, client=None, results=None):
		currentResults = self.initResult("inner:"+str(uuid.uuid4()))
		innerResults = self.parse(data, client, currentResults)

		return self.addInnerResult(results, innerResults)


	## run the specified API with JSON parameters. Dict or Array of JSON.
	def runAPI(self, command, params=None, client=None, results=None):		
		# erase comment
		if SublimeSocketAPISettings.API_COMMENT_DELIM in command:
			splitted = command.split(SublimeSocketAPISettings.API_COMMENT_DELIM, 1)
			command = splitted[1]


		# attach bridgedParams and remove.
		if SublimeSocketAPISettings.API_PARAM_END in command:
			splitted = command.split(SublimeSocketAPISettings.API_PARAM_END, 1)
			command = splitted[1]
			
			# separate by delim
			keyValues = splitted[0][1:]# remove SublimeSocketAPISettings.API_PARAM_START
			keyValuesArray = keyValues.split(SublimeSocketAPISettings.API_PARAM_DELIM)

			for keyAndValue in keyValuesArray:
				# key|valueKey
				keyAndValueArray = keyAndValue.split(SublimeSocketAPISettings.API_PARAM_CONCAT)
				
				key = keyAndValueArray[0]
				value = keyAndValueArray[1]

				# replace params with bridgedParams-rule
				assert key in results, "no-key in results. should use the API that have results."

				params[value] = results[key]

  		# python-switch
		for case in PythonSwitch(command):
			if case(SublimeSocketAPISettings.API_RESETRESULTS):
				return SublimeSocketAPISettings.PARSERESULT_SWITCH
				break

			if case(SublimeSocketAPISettings.API_RUNTESTS):
				self.runTests(params, client, results)
				break

			if case(SublimeSocketAPISettings.API_ASSERTRESULT):
				assertedResult = self.assertResult(params, results)

				# send for display test result
				buf = self.encoder.text(assertedResult[1], mask=0)
				client.send(buf)

				# countup
				currentResult = False
				if SublimeSocketAPISettings.ASSERTRESULT_VALUE_PASS in assertedResult[0]:
					self.testPassedCount = self.testPassedCount + 1
				else:
					self.testFailedCount = self.testFailedCount + 1

				break

			if case(SublimeSocketAPISettings.API_COUNTUP):
				self.countUp(params, results)
				break			

			if case(SublimeSocketAPISettings.API_RESETCOUNTS):
				self.resetCounts(results)
				break

			if case(SublimeSocketAPISettings.API_RUNSETTING):
				filePath = params[SublimeSocketAPISettings.RUNSETTING_FILEPATH]

				result = self.runSetting(filePath, client, results)
				if client:
					buf = self.encoder.text(result, mask=0)
					client.send(buf)

				break

			if case(SublimeSocketAPISettings.API_INPUTIDENTITY):
				self.inputIdentity(client, params, results)
				break

			if case(SublimeSocketAPISettings.API_TEARDOWN):
				self.server.tearDown()
				break

			if case(SublimeSocketAPISettings.API_CREATEBUFFER):
				self.createBuffer(params, results)
				break

			if case(SublimeSocketAPISettings.API_OPENFILE):
				self.openFile(params, results)
				break

			if case(SublimeSocketAPISettings.API_CLOSEFILE):
				self.closeFile(params, results)
				break

			if case(SublimeSocketAPISettings.API_CLOSEALLBUFFER):
				self.closeAllBuffer(results)
				break

			if case(SublimeSocketAPISettings.API_CONTAINSREGIONS):
				self.containsRegions(params, results)
				break

			if case(SublimeSocketAPISettings.API_COLLECTVIEWS):
				self.server.collectViews(results)
				break

			if case(SublimeSocketAPISettings.API_KEYVALUESTORE):
				result = self.server.KVSControl(params)
				
				# print("kvs result", result)
				buf = self.encoder.text(result, mask=0)
				client.send(buf)
				break
				
			if case(SublimeSocketAPISettings.API_DEFINEFILTER):
				# define filter
				self.defineFilter(params, results)
				break

			if case(SublimeSocketAPISettings.API_FILTERING):
				# run filtering
				self.runFiltering(params, results)
				break

			if case(SublimeSocketAPISettings.API_SETEVENTREACTOR):
				self.setEventReactor(params, client, results)
				break
				
			if case(SublimeSocketAPISettings.API_SETVIEWREACTOR):
				self.setViewReactor(params, client, results)
				break

			if case(SublimeSocketAPISettings.API_RESETREACTORS):
				self.resetReactors(params, results)
				break

			if case(SublimeSocketAPISettings.API_VIEWEMIT):
				self.viewEmit(params, results)
				break

			if case(SublimeSocketAPISettings.API_MODIFYVIEW):
				self.modifyView(params, results)
				break

			if case(SublimeSocketAPISettings.API_SETSELECTION):
				self.setSelection(params, results)
				break

			if case(SublimeSocketAPISettings.API_RUNSHELL):
				self.runShell(params, results)
				break

			if case(SublimeSocketAPISettings.API_BROADCASTMESSAGE):
				self.broadcastMessage(params, results)
				break

			if case(SublimeSocketAPISettings.API_MONOCASTMESSAGE):
				self.monocastMessage(params, results)
				break

			if case(SublimeSocketAPISettings.API_SHOWATLOG):
				self.showAtLog(params, results)
				break

			if case(SublimeSocketAPISettings.API_SHOWDIALOG):
				self.showDialog(params, results)
				break

			if case(SublimeSocketAPISettings.API_APPENDREGION):
				self.appendRegion(params, results)
				break

			if case(SublimeSocketAPISettings.API_RUNWITHBUFFER):
				self.runWithBuffer(params, results)
				break

			if case(SublimeSocketAPISettings.API_NOTIFY):
				self.notify(params, results)
				break

			if case(SublimeSocketAPISettings.API_GETALLFILEPATH):
				self.getAllFilePath(params, results)
				break

			if case(SublimeSocketAPISettings.API_READFILEDATA):
				self.readFileData(params, results)
				break

			if case(SublimeSocketAPISettings.API_EVENTEMIT):
				self.eventEmit(params, results)
				break

			if case(SublimeSocketAPISettings.API_CANCELCOMPLETION):
				self.cancelCompletion(params, results)
				break

			if case(SublimeSocketAPISettings.API_RUNCOMPLETION):
				self.runCompletion(params, results)
				break
			if case(SublimeSocketAPISettings.API_OPENPAGE):
				self.openPage(params, results)
				break

			if case(SublimeSocketAPISettings.API_SETSUBLIMESOCKETWINDOWBASEPATH):
				self.setSublimeSocketWindowBasePath(results)
				break

			# internal APIS
			if case(SublimeSocketAPISettings.API_I_SHOWSTATUSMESSAGE):
				self.showStatusMessage(params, results)
				break

			if case(SublimeSocketAPISettings.API_ERASEALLREGION):
				self.eraseAllRegion(params, results)
				break

			if case (SublimeSocketAPISettings.API_VERSIONVERIFY):
				self.versionVerify(params, client, results)
				break

			if case():
				print("unknown command", command, "/")
				break

		return SublimeSocketAPISettings.PARSERESULT_NONE


	## run each selectors
	def runAllSelector(self, paramDict, eventParam, results):
		
		def runForeachAPI(selector):
			# {u'broadcastMessage': {u'message': u"text's been modified!"}}

			for commands in selector.keys():
				command = commands
				
			params = selector[command]

			# print "params", params, "command", command
			currentParams = params.copy()

			# replace parameters if key 'replace' exist
			if paramDict and SublimeSocketAPISettings.REACTOR_REPLACEFROMTO in paramDict:
				for fromKey in paramDict[SublimeSocketAPISettings.REACTOR_REPLACEFROMTO].keys():
					if fromKey in eventParam:
						toKey = paramDict[SublimeSocketAPISettings.REACTOR_REPLACEFROMTO][fromKey]
						
						# replace or append
						currentParams[toKey] = eventParam[fromKey]

			self.runAPI(command, currentParams, None, results)

		[runForeachAPI(selector) for selector in paramDict[SublimeSocketAPISettings.REACTOR_SELECTORS]]


	## count up specified labelled param.
	def countUp(self, params, results):
		assert SublimeSocketAPISettings.COUNTUP_LABEL in params, "countUp requre 'label' param."
		assert SublimeSocketAPISettings.COUNTUP_DEFAULT in params, "countUp requre 'default' param."

		label = params[SublimeSocketAPISettings.COUNTUP_LABEL]

		if label in self.counts:
			self.counts[label] = self.counts[label] + 1

		else:
			self.counts[label] = params[SublimeSocketAPISettings.COUNTUP_DEFAULT]

		self.setResultsParams(results, self.countUp, {SublimeSocketAPISettings.COUNTUP_LABEL:label, "count":self.counts[label]})


	def resetCounts(self, results):
		self.counts = {}

		self.setResultsParams(results, self.resetCounts, {})


	## run specific setting.txt file as API
	def runSetting(self, filePath, client, results):
		
		# check contains PREFIX or not
		filePath = self.getKeywordBasedPath(filePath, 
			SublimeSocketAPISettings.RUNSETTING_PREFIX_SUBLIMESOCKET_PATH,
			sublime.packages_path() + "/"+MY_PLUGIN_PATHNAME+"/")

		print("ss: runSetting:", filePath)
		
		settingFile = open(filePath, 'r', encoding='utf8')
		setting = settingFile.read()
		settingFile.close()

		# print "setting", setting

		# remove //comment line
		removeCommented_setting = re.sub(r'//.*', r'', setting)
		
		# remove spaces
		removeSpaces_setting = re.sub(r'(?m)^\s+', '', removeCommented_setting)
		
		# remove CRLF
		removeCRLF_setting = removeSpaces_setting.replace("\n", "")
		
		commands = removeCRLF_setting
		# print "result", result

		# parse with specific result
		currentResults = {}
		self.innerParse(commands, client, currentResults)

		self.setResultsParams(results, self.runSetting, {"result":"done"})
		return "runSettings:"+str(removeCRLF_setting)

	## run shellScript
	# params is array that will be evaluated as commandline marameters.
	def runShell(self, params, results=None):
		assert SublimeSocketAPISettings.RUNSHELL_MAIN in params, "runShell require 'main' param."

		if SublimeSocketAPISettings.RUNSHELL_DELAY in params:
			delay = params[SublimeSocketAPISettings.RUNSHELL_DELAY]
			del params[SublimeSocketAPISettings.RUNSHELL_DELAY]
			
			if type(delay) is str:
				delay = int(delay)
				
			sublime.set_timeout(self.runShell(params), delay)

			return

		main = params[SublimeSocketAPISettings.RUNSHELL_MAIN]
		
		def genKeyValuePair(key):
			val = ""


			def replaceValParts(val):
				val = val.replace(" ", SublimeSocketAPISettings.RUNSHELL_REPLACE_SPACE);
				val = val.replace("(", SublimeSocketAPISettings.RUNSHELL_REPLACE_RIGHTBRACE);
				val = val.replace(")", SublimeSocketAPISettings.RUNSHELL_REPLACE_LEFTBRACE);
				val = val.replace("'", SublimeSocketAPISettings.RUNSHELL_REPLACE_SINGLEQUOTE);
				val = val.replace("`", SublimeSocketAPISettings.RUNSHELL_REPLACE_SINGLEQUOTE);
				val = val.replace("@s@s@", SublimeSocketAPISettings.RUNSHELL_REPLACE_At_s_At_s_At);


				# check contains PREFIX or not
				val = self.getKeywordBasedPath(val, 
					SublimeSocketAPISettings.RUNSETTING_PREFIX_SUBLIMESOCKET_PATH,
					sublime.packages_path() + "/"+MY_PLUGIN_PATHNAME+"/")

				if " " in val:
					val = "\"" + val + "\""
					
				return val

			if type(params[key]) == list:

				replaced = [replaceValParts(v) for v in params[key]]
				val = ' '.join(replaced)
			else:
				val = replaceValParts(str(params[key]))


			if len(val) is 0:
				return key

			if len(key) is 0:
				return val

			return key + ' ' + val

		kvPairArray = [genKeyValuePair(key) for key in params.keys() if key not in SublimeSocketAPISettings.RUNSHELL_LIST_IGNORES]
		kvPairArray.insert(0, main) 

		runnable = ' '.join(kvPairArray)
		debugFlag = False

		if SublimeSocketAPISettings.RUNSHELL_DEBUG in params:
			debugFlag = params[SublimeSocketAPISettings.RUNSHELL_DEBUG]

		if debugFlag:
			print("runnable", runnable)
		
		if len(runnable):
			subprocess.call(runnable, shell=True)
			if results:
				self.setResultsParams(results, self.runShell, {"runnable":runnable})
			

	## emit message to clients.
	# broadcast messages if no-"target" key.
	def broadcastMessage(self, params, results):
		assert SublimeSocketAPISettings.OUTPUT_MESSAGE in params, "broadcastMessage require 'message' param."
		
		message = params[SublimeSocketAPISettings.OUTPUT_MESSAGE]

		buf = self.encoder.text(str(message), mask=0)
		
		clients = self.server.clients.values()

		clientNames = list(self.server.clients.keys())
		print("clientNames", clientNames)
		
		for client in clients:
			client.send(buf)

		self.setResultsParams(results, self.broadcastMessage, {"sentTo":clientNames})
	

	## send message to the specific client.
	def monocastMessage(self, params, results):
		if SublimeSocketAPISettings.OUTPUT_FORMAT in params:
			params = self.formattingMessageParameters(params, SublimeSocketAPISettings.OUTPUT_FORMAT, SublimeSocketAPISettings.OUTPUT_MESSAGE)
			self.monocastMessage(params, results)
			return

		assert SublimeSocketAPISettings.OUTPUT_TARGET in params, "monocastMessage require 'target' param."
		assert SublimeSocketAPISettings.OUTPUT_MESSAGE in params, "monocastMessage require 'message' param."
		
		target = params[SublimeSocketAPISettings.OUTPUT_TARGET]
		message = params[SublimeSocketAPISettings.OUTPUT_MESSAGE]
		
		if target in self.server.clients:
			client = self.server.clients[target]
			buf = self.encoder.text(str(message), mask=0)
			client.send(buf)
			self.setResultsParams(results, self.monocastMessage, {SublimeSocketAPISettings.OUTPUT_TARGET:target, SublimeSocketAPISettings.OUTPUT_MESSAGE:message})

		else:
			print("monocastMessage failed. target:", target, "is not exist in clients:", self.server.clients)
			self.setResultsParams(results, self.monocastMessage, {SublimeSocketAPISettings.OUTPUT_TARGET:"", SublimeSocketAPISettings.OUTPUT_MESSAGE:message})
	


	## send message to the other via SS.
	def showAtLog(self, params, results):
		if SublimeSocketAPISettings.LOG_FORMAT in params:
			params = self.formattingMessageParameters(params, SublimeSocketAPISettings.LOG_FORMAT, SublimeSocketAPISettings.LOG_MESSAGE)
			self.showAtLog(params, results)
			return

		assert SublimeSocketAPISettings.LOG_MESSAGE in params, "showAtLog require 'message' param."
		message = params[SublimeSocketAPISettings.LOG_MESSAGE]
		print(SublimeSocketAPISettings.LOG_prefix, message)

		self.setResultsParams(results, self.showAtLog, {"output":message})


	def showDialog(self, params, results):
		if SublimeSocketAPISettings.SHOWDIALOG_FORMAT in params:
			params = self.formattingMessageParameters(params, SublimeSocketAPISettings.SHOWDIALOG_FORMAT, SublimeSocketAPISettings.SHOWDIALOG_MESSAGE)
			self.showDialog(params, results)
			return

		assert SublimeSocketAPISettings.SHOWDIALOG_MESSAGE in params, "showDialog require 'message' param."
		message = params[SublimeSocketAPISettings.LOG_MESSAGE]

		sublime.message_dialog(message)

		self.setResultsParams(results, self.showDialog, {"output":message})


	## run testus
	def runTests(self, params, client, results):
		assert SublimeSocketAPISettings.RUNTESTS_PATH in params, "runTests require 'path' param."
		filePath = params[SublimeSocketAPISettings.RUNTESTS_PATH]

		# check contains PREFIX of path or not
		filePath = self.getKeywordBasedPath(filePath, 
			SublimeSocketAPISettings.RUNSETTING_PREFIX_SUBLIMESOCKET_PATH,
			sublime.packages_path() + "/"+MY_PLUGIN_PATHNAME+"/")
		
		settingFile = open(filePath, 'r', encoding='utf8')
		
		setting = settingFile.read()
		settingFile.close()

		# remove //comment line
		removeCommented_setting = re.sub(r'//.*', r'', setting)
		
		# remove spaces
		removeSpaces_setting = re.sub(r'(?m)^\s+', '', removeCommented_setting)
		
		# remove CRLF
		removeCRLF_setting = removeSpaces_setting.replace("\n", "")
		source = removeCRLF_setting


		# start test
		self.isTesting = True
		
		# reset testResults
		self.testResults = []

		# reset counts
		self.testPassedCount = 0
		self.testFailedCount = 0

		# parse then get results
		self.innerParse(source, client, results)

		# end test
		self.isTesting = False


		# count ASSERTRESULT_VALUE_PASS or ASSERTRESULT_VALUE_FAIL
		totalResultMessage = "TOTAL:" + str(self.testPassedCount + self.testFailedCount) + " passed:" + str(self.testPassedCount) + " failed:" + str(self.testFailedCount)
		buf = self.encoder.text(totalResultMessage, mask=0)
		client.send(buf);

		
	## assertions
	def assertResult(self, params, currentResults):
		assert SublimeSocketAPISettings.ASSERTRESULT_ID in params, "assertResult require 'id' param."
		assert SublimeSocketAPISettings.ASSERTRESULT_DESCRIPTION in params, "assertResult require 'description' param."
		
		identity = params[SublimeSocketAPISettings.ASSERTRESULT_ID]
		

		debug = False

		if SublimeSocketAPISettings.ASSERTRESULT_DEBUG in params:
			debug = params[SublimeSocketAPISettings.ASSERTRESULT_DEBUG]
		

		results = currentResults
		
		
		if SublimeSocketAPISettings.ASSERTRESULT_CONTEXT in params:
			contextKeyword = params[SublimeSocketAPISettings.ASSERTRESULT_CONTEXT]
			print("self.testResults", self.testResults)
			
			def checkIsResultsOf(currentContext, currentContextKeyword):
				key = list(currentContext)[0]
				
				if currentContextKeyword in key:
					return True
					
				return False

			def collectResultsContextValues(currentContext):
				key = list(currentContext)[0]
				value = currentContext[key]

				return value
				
			unmergedResultsList = [collectResultsContextValues(context) for context in self.testResults if checkIsResultsOf(context, contextKeyword)]

			resultValues = {}
			mergedResults = {}
			
			for item in unmergedResultsList:
				for key in list(item):
					resultValues[key] = item[key]
			
			results = {contextKeyword:resultValues}
			
		# load results for check
		resultBodies = self.resultBody(results)
		if debug:
			print("\nassertResult:\nid:", identity, "\nresultBodies:", resultBodies, "\n:assertResult\n")


		assertionIdentity = params[SublimeSocketAPISettings.ASSERTRESULT_ID]
		message = params[SublimeSocketAPISettings.ASSERTRESULT_DESCRIPTION]
		
		

		def genAssertionResult(passedOrFailed, assertionIdentity, message, results):

			def assertionMessage(assertType, currentIdentity, currentMessage):
				return assertType + " " + currentIdentity + " : " + currentMessage

			resultMessage = assertionMessage(passedOrFailed,
								assertionIdentity, 
								message)

			self.setResultsParams(results, self.assertResult, {assertionIdentity:resultMessage})
			return (passedOrFailed, resultMessage)



		# contains
		if SublimeSocketAPISettings.ASSERTRESULT_CONTAINS in params:
			currentDict = params[SublimeSocketAPISettings.ASSERTRESULT_CONTAINS]
			if debug:
				print("start assertResult 'contains' in", identity, resultBodies)

			# match
			for key in currentDict:
				for resultKey in resultBodies:
					if resultKey[0] == key:
						assertValue = currentDict[key]
						assertTarget = resultBodies[resultKey]
						if debug:
							print("expected:", assertValue, "\n", "actual:", assertTarget, "\n")

						if assertValue == assertTarget:
							return genAssertionResult(SublimeSocketAPISettings.ASSERTRESULT_VALUE_PASS,
								assertionIdentity, 
								key + ":" + str(assertValue) + " in " + str(resultBodies[resultKey]),
								results)

			# fail
			if debug:
				print("failed assertResult 'contains' in", identity)

			return genAssertionResult(SublimeSocketAPISettings.ASSERTRESULT_VALUE_FAIL,
				assertionIdentity, 
				message,
				results)


		# not contains
		if SublimeSocketAPISettings.ASSERTRESULT_NOTCONTAINS in params:
			currentDict = params[SublimeSocketAPISettings.ASSERTRESULT_NOTCONTAINS]
			if debug:
				print("start assertResult 'not contains' in", identity, resultBodies)

			# match
			for key in currentDict:
				for resultKey in resultBodies:
					if resultKey[0] == key:
						assertValue = currentDict[key]
						assertTarget = resultBodies[resultKey]

						if assertValue == assertTarget:
							if debug:
								print("failed assertResult 'not contains' in", identity)

							return genAssertionResult(SublimeSocketAPISettings.ASSERTRESULT_VALUE_FAIL,
								assertionIdentity, 
								key + ":" + str(assertValue) + " in " + str(resultBodies[resultKey]),
								results)

			# pass
			return genAssertionResult(SublimeSocketAPISettings.ASSERTRESULT_VALUE_PASS,
								assertionIdentity, 
								message,
								results)


		# is empty or not
		elif SublimeSocketAPISettings.ASSERTRESULT_ISEMPTY in params:
			if debug:
				print("start assertResult 'isempty' in", identity, resultBodies)

			# match
			if not resultBodies:
				return genAssertionResult(SublimeSocketAPISettings.ASSERTRESULT_VALUE_PASS,
					assertionIdentity, 
					"is empty.",
					results)

			# fail
			if debug:
				print("failed assertResult 'empty' in", identity)

			return genAssertionResult(SublimeSocketAPISettings.ASSERTRESULT_VALUE_FAIL,
				assertionIdentity, 
				message,
				results)

			

		# is not empty or empty
		elif SublimeSocketAPISettings.ASSERTRESULT_ISNOTEMPTY in params:
			if debug:
				print("start assertResult 'isnotempty' in", identity, resultBodies)

			targetAPIKey = params[SublimeSocketAPISettings.ASSERTRESULT_ISNOTEMPTY]
			print("targetAPIKey", targetAPIKey)

			# 特定のAPIkeyに対して、値が存在している
			print("resultBodies", resultBodies)
			
			for resultKey in resultBodies:
				if resultKey[0] == targetAPIKey:
					return genAssertionResult(SublimeSocketAPISettings.ASSERTRESULT_VALUE_PASS,
						assertionIdentity, 
						"is not empty.",
						results)

			# fail
			if debug:
				print("failed assertResult 'isnotempty' in", identity)

			return genAssertionResult(SublimeSocketAPISettings.ASSERTRESULT_VALUE_FAIL,
				assertionIdentity, 
				message,
				results)
			
		if debug:
				print("assertion aborted in assertResult API.", message, identity)

		return genAssertionResult(SublimeSocketAPISettings.ASSERTRESULT_VALUE_FAIL,
			assertionIdentity,
			"assertion aborted in assertResult API.",
			results)
		
	
	## input identity to client.
	def inputIdentity(self, client, params, results):
		identity = self.server.updateClientId(client, params)
		self.setResultsParams(results, self.inputIdentity, {"inputIdentity":identity})

	## create buffer then set contents if exist.
	def createBuffer(self, params, results):
		assert SublimeSocketAPISettings.CREATEBUFFER_NAME in params, "createBuffer require 'name' param"
		
		name = params[SublimeSocketAPISettings.CREATEBUFFER_NAME]

		# renew event will run, but the view will not store KVS because of no-name view.
		view = sublime.active_window().open_file(name)

		# buffer generated then set name and store to KVS.
		if self.server.isBuffer(view):
			message = "buffer "+ name +" created."
			result = message

			view.set_name(name)

			# restore to KVS with name
			viewParams = self.server.generateSublimeViewInfo(
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

			self.server.fireKVStoredItem(
				SublimeSocketAPISettings.REACTORTYPE_VIEW,
				SublimeSocketAPISettings.SS_EVENT_RENAMED, 
				viewParams,
				results)

			# if "contents" exist, set contents to buffer.
			if SublimeSocketAPISettings.CREATEBUFFER_CONTENTS in params:
				contents = params[SublimeSocketAPISettings.CREATEBUFFER_CONTENTS]
				view.run_command('insert_text', {'string': contents})
			
			self.setResultsParams(results, self.createBuffer, {"result":result, SublimeSocketAPISettings.CREATEBUFFER_NAME:name})
		
	
	## open file
	def openFile(self, params, results):
		assert SublimeSocketAPISettings.OPENFILE_NAME in params, "openFile require 'name' key."
		original_name = params[SublimeSocketAPISettings.OPENFILE_NAME]
		name = original_name

		name = self.getKeywordBasedPath(name, 
			SublimeSocketAPISettings.RUNSETTING_PREFIX_SUBLIMESOCKET_PATH,
			sublime.packages_path() + "/"+MY_PLUGIN_PATHNAME+"/")

		view = sublime.active_window().open_file(name)

		path = view.file_name()
		
		if self.server.isBuffer(view):
			message = "file " + original_name + " is not exist."
			print(message)

			result = message
			
			view.close()


		else:
			message = "file " + original_name + " is opened."
			print(message)
		
			result = message

			viewParams = self.server.generateSublimeViewInfo(
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
			
			self.server.fireKVStoredItem(
				SublimeSocketAPISettings.REACTORTYPE_VIEW,
				SublimeSocketAPISettings.SS_EVENT_LOADING, 
				viewParams,
				results)

		self.setResultsParams(results, self.openFile, {SublimeSocketAPISettings.OPENFILE_NAME:original_name, "result":result})
	
	## close file. if specified -> close the file. if not specified -> close current file.
	def closeFile(self, params, results):
		assert SublimeSocketAPISettings.CLOSEFILE_NAME in params, "closeFile require 'name' param."
		
		name = params[SublimeSocketAPISettings.CLOSEFILE_NAME]
		view = self.internal_detectViewInstance(name)
		
		view.close()
		self.setResultsParams(results, self.closeFile, {"name":name})


	def closeAllBuffer(self, results):
		closed = []

		def close(views):
			for view in views:
				if self.server.isBuffer(view):
					viewPath = self.internal_detectViewPath(view)
					closed.append(viewPath)

					view.close()

		[close(window.views()) for window in sublime.windows()]

		self.setResultsParams(results, self.closeAllBuffer, {"closed":closed})


	## selected is contains regions or not.
	def containsRegions(self, params, results):
		assert SublimeSocketAPISettings.CONTAINSREGIONS_VIEW in params, "containsRegions require 'view' param."
		assert SublimeSocketAPISettings.CONTAINSREGIONS_TARGET in params, "containsRegions require 'target' param."
		assert SublimeSocketAPISettings.CONTAINSREGIONS_EMIT in params, "containsRegions require 'emit' param."
		assert SublimeSocketAPISettings.CONTAINSREGIONS_SELECTED in params, "containsRegions requires 'selected' param."

		self.server.containsRegionsInKVS(params, results)
		
	## Define the filter and check filterPatterns
	def defineFilter(self, params, results):
		# check filter name
		assert SublimeSocketAPISettings.DEFINEFILTER_NAME in params, "defineFilter require 'name' key."

		# load defined filters
		filterNameAndPatternsArray = {}

		if self.server.isExistOnKVS(SublimeSocketAPISettings.DICT_FILTERS):
			filterNameAndPatternsArray = self.server.getV(SublimeSocketAPISettings.DICT_FILTERS)

		filterName = params[SublimeSocketAPISettings.DEFINEFILTER_NAME]

		patterns = params[SublimeSocketAPISettings.DEFINEFILTER_PATTERNS]
		assert type(patterns) == list, "defineFilter require: filterPatterns must be list."

		def mustBeSingleDict(filterDict):
			assert len(filterDict) is 1, "defineFilter. too many filter in one dictionary. len is "+str(len(filterDict))
			

		[mustBeSingleDict(currentFilterDict) for currentFilterDict in patterns]

		# key = filterName, value = the match patterns of filter.
		filterNameAndPatternsArray[filterName] = patterns

		# store anyway.
		self.server.setKV(SublimeSocketAPISettings.DICT_FILTERS, filterNameAndPatternsArray)

		self.setResultsParams(results, self.defineFilter, {"defined":params})
		

	## filtering. matching -> run API
	def runFiltering(self, params, results):
		assert SublimeSocketAPISettings.FILTER_NAME in params, "filtering require 'filterName' param."

		filterName = params[SublimeSocketAPISettings.FILTER_NAME]

		# check filterName exists or not
		if not self.server.isFilterDefined(filterName):
			print("filterName:"+str(filterName), "is not yet defined.")
			return

		filterSource = params[SublimeSocketAPISettings.FILTER_SOURCE]

		# get filter key-values array
		filterPatternsArray = self.server.getV(SublimeSocketAPISettings.DICT_FILTERS)[filterName]

		# print "filterPatternsArray", filterPatternsArray
		currentResults = []
		for pattern in filterPatternsArray:
			
			for key_executableDictPair in pattern.items():
				(key, executablesDict) = key_executableDictPair

			debug = False
			if SublimeSocketAPISettings.FILTER_DEBUG in executablesDict:
				debug = executablesDict[SublimeSocketAPISettings.FILTER_DEBUG]

			if debug:
				print("filterName:"+str(filterName))
				print("pattern:", pattern)
				print("executablesDict:", executablesDict)

			dotall = False
			if SublimeSocketAPISettings.FILTER_DOTALL in executablesDict:
				dotall = executablesDict[SublimeSocketAPISettings.FILTER_DOTALL]


			# search
			if dotall:
				searchResult = re.finditer(re.compile(r'%s' % key, re.M | re.DOTALL), filterSource)				
			else:
				searchResult = re.finditer(re.compile(r'%s' % key, re.M), filterSource)

			
			for searched in searchResult:
				
				if searched:
					executablesArray = executablesDict[SublimeSocketAPISettings.FILTER_SELECTORS]
					
					if debug:
						print("matched defineFilter selectors:", executablesArray)
						print("filterSource\n---------------------\n", filterSource, "\n---------------------")
						print("matched group()", searched.group())
						print("matched groups()", searched.groups())
					
						if SublimeSocketAPISettings.FILTER_COMMENT in executablesDict:
							print("matched defineFilter comment:", executablesDict[SublimeSocketAPISettings.FILTER_COMMENT])

					currentGroupSize = len(searched.groups())
					
					# run
					for executableDict in executablesArray:
						
						# execute
						for executableDictKey in executableDict.keys():
							command = executableDictKey
							break
						
						# print "command", command
						
						paramsSource = executableDict[command]

						params = None
						# replace the keyword "groups[x]" to regexp-result value of the 'groups[x]', if params are string-array
						if type(paramsSource) == list:
							# before	APINAME:["sublime.message_dialog('groups[0]')"]
							# after		APINAME:["sublime.message_dialog('THE_VALUE_OF_searched.groups()[0]')"]
							
							def replaceGroupsInListKeyword(param):
								result = param
								
								for index in range(currentGroupSize):
									# replace all expression
									if re.findall(r'groups\[(' + str(index) + ')\]', result):
										result = re.sub(r'groups\[' + str(index) + '\]', searched.groups()[index], result)

								result = re.sub(r'filterSource\[\]', filterSource, result)
								return result
								

							# replace "groups[x]" expression in the value of list to 'searched.groups()[x]' value
							params = map(replaceGroupsInListKeyword, paramsSource)
							
						elif type(paramsSource) == dict:
							# before {u'line': u'groups[1]', u'message': u'message is groups[0]'}
							# after	 {u'line': u'THE_VALUE_OF_searched.groups()[1]', u'message': u'message is THE_VALUE_OF_searched.groups()[0]'}

							def replaceGroupsInDictionaryKeyword(key):
								result = paramsSource[key]
								
								for index in range(currentGroupSize):
									
									# replace all expression
									if re.findall(r'groups\[(' + str(index) + ')\]', result):
										froms = searched.groups()[index]
										result = re.sub(r'groups\[' + str(index) + '\]', froms, result)

								result = re.sub(r'filterSource\[\]', filterSource, result)
								return {key:result}
							# replace "groups[x]" expression in the value of dictionary to 'searched.groups()[x]' value
							params_dicts = list(map(replaceGroupsInDictionaryKeyword, paramsSource.keys()))

							if not params_dicts:
								pass
							elif 1 == len(params_dicts):
								params = params_dicts[0]
							else:
								def reduceLeft(before, next):
									# append all key-value pair.
									for key in next.keys():
										before[key] = next[key]
									return before
								
								params = reduce(reduceLeft, params_dicts[1:], params_dicts[0])
							
						else:
							print("filtering warning:unknown type")
						
						if debug:
							print("filtering command:", command, "params:", params)

						# execute
						self.runAPI(command, params, None, results)
						
						# report
						currentResults.append({filterName:params})

				else:
					if debug:
						print("filtering not match")

		# return succeded signal
		if 0 < len(currentResults):
			# set params into results
			self.setResultsParams(results, self.runFiltering, currentResults)


	## set reactor for reactive-event
	def setEventReactor(self, params, client, results):
		reactors = self.server.setReactor(SublimeSocketAPISettings.REACTORTYPE_EVENT, params)
		self.setResultsParams(results, self.setEventReactor, {"eventreactors":reactors})

	## set reactor for view
	def setViewReactor(self, params, client, results):
		reactors = self.server.setReactor(SublimeSocketAPISettings.REACTORTYPE_VIEW, params)
		self.setResultsParams(results, self.setViewReactor, {"viewreactors":reactors})
		
	## erase all reactors
	def resetReactors(self, params, results):
		deletedReactors = self.server.removeAllReactors()

		self.setResultsParams(results, self.resetReactors, {"deletedReactors":deletedReactors})


	def viewEmit(self, params, results):
		assert SublimeSocketAPISettings.VIEWEMIT_SELECTORS in params, "viewEmit require 'selectors' param."
		
		(view, path) = self.internal_getViewAndPathFromViewOrName(params, SublimeSocketAPISettings.VIEWEMIT_VIEW, SublimeSocketAPISettings.VIEWEMIT_NAME)

		# set view param.
		eventParam = {SublimeSocketAPISettings.REACTOR_VIEWKEY_VIEWSELF:view}

		# interpolate "replace from to" automatically
		params[SublimeSocketAPISettings.REACTOR_REPLACEFROMTO] = {
			SublimeSocketAPISettings.REACTOR_VIEWKEY_VIEWSELF:SublimeSocketAPISettings.REACTOR_VIEWKEY_VIEWSELF,
			SublimeSocketAPISettings.REACTOR_VIEWKEY_SELECTED:SublimeSocketAPISettings.REACTOR_VIEWKEY_SELECTED
		}

		self.runAllSelector(params, eventParam, results)
		self.setResultsParams(results, self.viewEmit, {"name":path})


	def modifyView(self, params, results):
		view = None
		if SublimeSocketAPISettings.MODIFYVIEW_VIEW in params:
			view = params[SublimeSocketAPISettings.MODIFYVIEW_VIEW]
			path = view.file_name()

		if SublimeSocketAPISettings.MODIFYVIEW_NAME in params:
			path = params[SublimeSocketAPISettings.MODIFYVIEW_NAME]
			view = self.internal_detectViewInstance(path)

		assert view, "modifyView require 'view' or 'name' param."
		
		if SublimeSocketAPISettings.MODIFYVIEW_ADD in params:
			print("viewは", view.file_name())
			view.run_command('insert_text', {'string': params[SublimeSocketAPISettings.MODIFYVIEW_ADD]})
			print("over")
			
		if SublimeSocketAPISettings.MODIFYVIEW_REDUCE in params:
			view.run_command('reduce_text')


	## generate selection to view
	def setSelection(self, params, results):
		view = None
		if SublimeSocketAPISettings.SETSELECTION_VIEW in params:
			view = params[SublimeSocketAPISettings.SETSELECTION_VIEW]

		elif SublimeSocketAPISettings.SETSELECTION_NAME in params:
			path = params[SublimeSocketAPISettings.SETSELECTION_NAME]
			view = self.internal_detectViewInstance(path)

		assert view, "setSelection require 'view' or 'name' param."

		assert SublimeSocketAPISettings.SETSELECTION_FROM in params, "setSelection require 'from' param."
		assert SublimeSocketAPISettings.SETSELECTION_TO in params, "setSelection require 'to' param."
		
		regionFrom = params[SublimeSocketAPISettings.SETSELECTION_FROM]
		regionTo = params[SublimeSocketAPISettings.SETSELECTION_TO]

		pt = sublime.Region(regionFrom, regionTo)
		view.sel().add(pt)
		selected = str(pt)
		
		filePath = view.file_name()
		if filePath:
			# emit viewReactor
			viewParams = self.server.generateSublimeViewInfo(
				view,
				SublimeSocketAPISettings.VIEW_SELF,
				SublimeSocketAPISettings.VIEW_ID,
				SublimeSocketAPISettings.VIEW_BUFFERID,
				SublimeSocketAPISettings.VIEW_PATH,
				SublimeSocketAPISettings.VIEW_BASENAME,
				SublimeSocketAPISettings.VIEW_VNAME,
				SublimeSocketAPISettings.VIEW_SELECTED,
				SublimeSocketAPISettings.VIEW_ISEXIST)

			self.server.fireKVStoredItem(SublimeSocketAPISettings.REACTORTYPE_VIEW, SublimeSocketAPISettings.SS_VIEW_ON_SELECTION_MODIFIED_BY_SETSELECTION, viewParams, results)
			self.setResultsParams(results, self.setSelection, {"selected":selected})

		
		
	## get the target view-s information if params includes "filename.something" or some pathes represents filepath.
	def internal_detectViewInstance(self, name):
		viewDict = self.server.viewsDict()
		if viewDict:
			viewKeys = viewDict.keys()

			viewSearchSource = name

			# remove empty and 1 length string pattern.
			if not viewSearchSource or len(viewSearchSource) is 0:
				return None

			print("internal_detectViewInstance viewSearchSource", viewSearchSource)
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


	def internal_detectViewPath(self, view):
		instances = []
		viewsDict = self.server.viewsDict()
		
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
			assert view, "no view"
			
			path = self.internal_detectViewPath(view)
			assert path, "no path"

		if view and path:
			return (view, path)
		else:
			return (None, None)


	########## APIs for shortcut ST2-Display ##########

	## show message on ST
	def showStatusMessage(self, params, results):
		assert SublimeSocketAPISettings.SHOWSTATUSMESSAGE_MESSAGE in params, "showStatusMessage require 'message' param."
		message = params[SublimeSocketAPISettings.SHOWSTATUSMESSAGE_MESSAGE]
		sublime.status_message(message)

		self.setResultsParams(results, self.showStatusMessage, {"output":message})

	## append region on ST
	def appendRegion(self, params, results):
		assert SublimeSocketAPISettings.APPENDREGION_LINE in params, "appendRegion require 'line' param."
		assert SublimeSocketAPISettings.APPENDREGION_MESSAGE in params, "appendRegion require 'message' param."
		assert SublimeSocketAPISettings.APPENDREGION_CONDITION in params, "appendRegion require 'condition' param."

		line = params[SublimeSocketAPISettings.APPENDREGION_LINE]
		message = params[SublimeSocketAPISettings.APPENDREGION_MESSAGE]
		condition = params[SublimeSocketAPISettings.APPENDREGION_CONDITION]

		(view, path) = self.internal_getViewAndPathFromViewOrName(params, SublimeSocketAPISettings.APPENDREGION_VIEW, SublimeSocketAPISettings.APPENDREGION_NAME)
			
		# add region
		if view:
			lines = []
			regions = []
			point = self.getLineCount_And_SetToArray(view, line, lines)

			regions.append(view.line(point))

			identity = SublimeSocketAPISettings.REGION_UUID_PREFIX + str(regions[0])
			
			# show
			view.add_regions(identity, regions, condition, 'dot', sublime.DRAW_OUTLINED)

			# store region
			self.server.storeRegionToView(view, identity, regions[0], line, message)


			self.setResultsParams(results, self.appendRegion, {"result":"appended", 
				SublimeSocketAPISettings.APPENDREGION_LINE:line, 
				SublimeSocketAPISettings.APPENDREGION_MESSAGE:message, 
				SublimeSocketAPISettings.APPENDREGION_CONDITION:condition})

		# raise no view found
		else:
			currentParams = {}
			currentParams[SublimeSocketAPISettings.NOVIEWFOUND_PATH] = path
			currentParams[SublimeSocketAPISettings.NOVIEWFOUND_LINE] = line
			currentParams[SublimeSocketAPISettings.NOVIEWFOUND_MESSAGE] = message
			currentParams[SublimeSocketAPISettings.NOVIEWFOUND_CONDITION] = condition

			self.server.fireKVStoredItem(SublimeSocketAPISettings.REACTORTYPE_VIEW, SublimeSocketAPISettings.SS_FOUNDATION_NOVIEWFOUND, currentParams, results)
			
			currentParams["result"] = "failed to append region."
			self.setResultsParams(results, self.appendRegion, currentParams)
			
	
	## emit ss_f_runWithBuffer event
	def runWithBuffer(self, params, results):
		if SublimeSocketAPISettings.RUNWITHBUFFER_VIEW in params:
			view = params[SublimeSocketAPISettings.RUNWITHBUFFER_VIEW]

		else:
			view = sublime.active_window().active_view()
			params[SublimeSocketAPISettings.RUNWITHBUFFER_VIEW] = view

		self.server.fireKVStoredItem(SublimeSocketAPISettings.REACTORTYPE_VIEW, SublimeSocketAPISettings.SS_FOUNDATION_RUNWITHBUFFER, params, results)

		name = view.name()

		# set name "" -> "None" if None. avoid matching JSON's "null" & Python's "None".
		if not name:
			name = "None"
		
		self.setResultsParams(results, self.runWithBuffer, {"name":name})


	## emit notification mechanism
	def notify(self, params, results):
		assert SublimeSocketAPISettings.NOTIFY_TITLE in params, "notify require 'title' param."
		assert SublimeSocketAPISettings.NOTIFY_MESSAGE in params, "notify require 'message' param."

		title = params[SublimeSocketAPISettings.NOTIFY_TITLE]
		message = params[SublimeSocketAPISettings.NOTIFY_MESSAGE]
		
		env = sublime.platform() 

		if env == "osx":
			debug = False
			if SublimeSocketAPISettings.NOTIFY_DEBUG in params:
				debug = params[SublimeSocketAPISettings.NOTIFY_DEBUG]
			
			exe = "\"" + sublime.packages_path() + "/"+MY_PLUGIN_PATHNAME+"/tool/notification/MacNotifier.sh\""
			exeArray = ["-t", title, "-m", message, "-replaceunderscore", "", ]

			shellParams = {
				SublimeSocketAPISettings.RUNSHELL_MAIN: "/bin/sh",
				exe: exeArray,
				SublimeSocketAPISettings.RUNSHELL_DEBUG: debug
			}
			
			self.runShell(shellParams)
			self.setResultsParams(results, self.notify, {SublimeSocketAPISettings.NOTIFY_TITLE: title, SublimeSocketAPISettings.NOTIFY_MESSAGE: message})



	## get current project's file paths then set results
	def getAllFilePath(self, params, results):
		assert SublimeSocketAPISettings.GETALLFILEPATH_ANCHOR in params, "getAllFilePath require 'anchor' param."

		header = ""
		if SublimeSocketAPISettings.GETALLFILEPATH_HEADER in params:
			header = params[SublimeSocketAPISettings.GETALLFILEPATH_HEADER]

		footer = ""
		if SublimeSocketAPISettings.GETALLFILEPATH_FOOTER in params:
			footer = params[SublimeSocketAPISettings.GETALLFILEPATH_FOOTER]


		anchor = params[SublimeSocketAPISettings.GETALLFILEPATH_ANCHOR]

		self.setSublimeSocketWindowBasePath(results)

		filePath = self.sublimeSocketWindowBasePath

		if filePath:
			pass
		else:
			self.setResultsParams(results, self.getAllFilePath, {"result":"notexist"})
			return

		folderPath = os.path.dirname(filePath)
	
		depth = len(filePath.split("/"))-1
		
		basePath_default = "default"
		basePath = basePath_default

		folderPath2 = folderPath


		limitation = -1
		if SublimeSocketAPISettings.GETALLFILEPATH_LIMIT in params:
			limitation = params[SublimeSocketAPISettings.GETALLFILEPATH_LIMIT]


		for i in range(depth-1):
			for r,d,f in os.walk(folderPath):

				for files in f:
					if files == anchor:
						basePath = os.path.join(r,files)
						break
						
				if basePath != basePath_default:
					break

			if basePath != basePath_default:
				break

			
			if limitation == 0:
				self.setResultsParams(results, self.getAllFilePath, {"result":"depthover"})
				return

			limitation = limitation - 1

			# not hit, up
			folderPath = os.path.dirname(folderPath)

			

		baseDir = os.path.dirname(basePath)


		pathArray = []
		for r,d,f in os.walk(baseDir):
			for files in f:
				pathArray.append(os.path.join(r,files))

		delim = ","
		if SublimeSocketAPISettings.GETALLFILEPATH_DELIM in params:
			delim = params[SublimeSocketAPISettings.GETALLFILEPATH_DELIM]

		joinedPathsStr = delim.join(pathArray)

		self.setResultsParams(results, self.getAllFilePath, {"result":joinedPathsStr, SublimeSocketAPISettings.GETALLFILEPATH_HEADER:header, SublimeSocketAPISettings.GETALLFILEPATH_FOOTER:footer, SublimeSocketAPISettings.GETALLFILEPATH_DELIM:delim})

	# not depends on Sublime Text API. (but depends on shortcut.)
	def readFileData(self, params, results):
		assert SublimeSocketAPISettings.READFILEDATA_PATH in params, "readFileData require 'path' param."
		
		original_path = params[SublimeSocketAPISettings.READFILEDATA_PATH]
		path = original_path

		path = self.getKeywordBasedPath(path, 
			SublimeSocketAPISettings.RUNSETTING_PREFIX_SUBLIMESOCKET_PATH,
			sublime.packages_path() + "/"+MY_PLUGIN_PATHNAME+"/")

		currentFile = open(path, 'r')
		data = currentFile.read()
		currentFile.close()

		if not data:
			self.setResultsParams(results, self.readFileData, {"data":""})
		else:
			self.setResultsParams(results, self.readFileData, {"data":data})


	def eventEmit(self, params, results):
		assert SublimeSocketAPISettings.EVENTEMIT_TARGET in params, "eventEmit require 'target' param."
		assert SublimeSocketAPISettings.EVENTEMIT_EVENT in params, "eventEmit require 'event' param."

		eventName = params[SublimeSocketAPISettings.EVENTEMIT_EVENT]
		assert eventName.startswith(SublimeSocketAPISettings.REACTIVE_PREFIX_USERDEFINED_EVENT), "eventEmit only emit 'user-defined' event such as starts with 'event_' keyword."

		self.server.fireKVStoredItem(SublimeSocketAPISettings.REACTORTYPE_EVENT, eventName, params, results)
		self.setResultsParams(results, 
			self.eventEmit, 
			{SublimeSocketAPISettings.EVENTEMIT_TARGET:params[SublimeSocketAPISettings.EVENTEMIT_TARGET], SublimeSocketAPISettings.EVENTEMIT_EVENT:params[SublimeSocketAPISettings.EVENTEMIT_EVENT]})


	def cancelCompletion(self, params, results):
		print("cancelCompletionに来てる")
		(view, path) = self.internal_getViewAndPathFromViewOrName(params, SublimeSocketAPISettings.CANCELCOMPLETION_VIEW, SublimeSocketAPISettings.CANCELCOMPLETION_NAME)
		assert view, "cancelCompletion require 'view' or 'name' param."

		# hide completion
		view.run_command("hide_auto_complete")

		self.setResultsParams(results, self.cancelCompletion, {"cancelled":path})

	
	def runCompletion(self, params, results):
		assert SublimeSocketAPISettings.RUNCOMPLETION_COMPLETIONS in params, "runCompletion require 'completion' param."
		
		(view, path) = self.internal_getViewAndPathFromViewOrName(params, SublimeSocketAPISettings.RUNCOMPLETION_VIEW, SublimeSocketAPISettings.RUNCOMPLETION_NAME)
		assert view, "runCompletion require 'view' or 'name' param."
		
		completions = params[SublimeSocketAPISettings.RUNCOMPLETION_COMPLETIONS]		

		formatHead = ""
		if SublimeSocketAPISettings.RUNCOMPLETION_FORMATHEAD in params:
			formatHead = params[SublimeSocketAPISettings.RUNCOMPLETION_FORMATHEAD]

		formatTail = ""
		if SublimeSocketAPISettings.RUNCOMPLETION_FORMATTAIL in params:
			formatTail = params[SublimeSocketAPISettings.RUNCOMPLETION_FORMATTAIL]
		
		
		def transformToFormattedTuple(sourceDict):
			a = formatHead
			b = formatTail
			for key in sourceDict:
				a = a.replace(key, sourceDict[key])
				b = b.replace(key, sourceDict[key])
			
			return (a, b)
			
		completionStrs = list(map(transformToFormattedTuple, completions))
		
		# set completion
		self.server.updateCompletion(path, completionStrs)

		# display completions
		view.run_command("auto_complete")

		self.setResultsParams(results, self.runCompletion, {"completed":path})
			

	def openPage(self, params, results):
		assert SublimeSocketAPISettings.OPENPAGE_IDENTITY in params, "openPage require 'identity' param."
		identity = params[SublimeSocketAPISettings.OPENPAGE_IDENTITY]

		host = sublime.load_settings("SublimeSocket.sublime-settings").get('host')
		port = sublime.load_settings("SublimeSocket.sublime-settings").get('port')
		writtenIdentity = identity

		# create path of Preference.html
		currentPackagePath = sublime.packages_path() + "/"+MY_PLUGIN_PATHNAME+"/"
		originalHtmlPath = "resource/html/openpageSource.html"
		originalPath = currentPackagePath + originalHtmlPath

		preferenceFilePath = "tmp/" + identity + ".html"
		preferencePath = currentPackagePath + preferenceFilePath

		# prepare html contents
		htmlFile = open(originalPath, 'r')
		html = htmlFile.read()
		
		htmlFile.close()
			
		# replace host:port, identity
		html = html.replace(SublimeWSSettings.SS_HOST_REPLACE, host)
		html = html.replace(SublimeWSSettings.SS_PORT_REPLACE, str(port))
		html = html.replace(SublimeWSSettings.SS_IDENTITY_REPLACE, writtenIdentity)

		# generate preference
		outputFile = open(preferencePath, 'w')
		outputFile.write(html)
		outputFile.close()
		
		# set Target-App to open Preference.htnl
		targetAppPath = sublime.load_settings("SublimeSocket.sublime-settings").get('preference browser')

		shellParamDict = {"main":"/usr/bin/open", "-a":targetAppPath, "\"" + preferencePath + "\"":""
		}

		self.runShell(shellParamDict, results)
		pass

	def setSublimeSocketWindowBasePath(self, results):
		self.sublimeSocketWindowBasePath = sublime.active_window().active_view().file_name()
		print("sublimeSocketWindowBasePath", self.sublimeSocketWindowBasePath)


		self.setResultsParams(results, self.setSublimeSocketWindowBasePath, {"set":"ok"})
		
	## verify SublimeSocket API-version and SublimeSocket version
	def versionVerify(self, params, client, results):
		assert client, "versionVerify require 'client' object."
		assert SublimeSocketAPISettings.VERSIONVERIFY_SOCKETVERSION in params, "versionVerify require 'socketVersion' param."
		assert SublimeSocketAPISettings.VERSIONVERIFY_APIVERSION in params, "versionVerify require 'apiVersion' param."
		

		# targetted socket version
		targetSocketVersion = int(params[SublimeSocketAPISettings.VERSIONVERIFY_SOCKETVERSION])

		# targetted API version
		targetVersion = params[SublimeSocketAPISettings.VERSIONVERIFY_APIVERSION]
		

		# current socket version
		currentSocketVersion = SublimeSocketAPISettings.SOCKET_VERSION

		# current API version
		currentVersion			= SublimeSocketAPISettings.API_VERSION


		# check socket version
		if targetSocketVersion is not currentSocketVersion:
			self.sendVerifiedResultMessage(0, targetSocketVersion, SublimeSocketAPISettings.SOCKET_VERSION, targetVersion, currentVersion, client)
			return

		# SublimeSocket version matched.

		# check socket versipn
		targetVersionArray = targetVersion.split(".")

		targetMajor	= int(targetVersionArray[0])
		targetMinor	= int(targetVersionArray[1])
		# targetPVer	= int(targetVersionArray[2])

		
		currentVersionArray = currentVersion.split(".")

		currentMajor	= int(currentVersionArray[0])
		currentMinor	= int(currentVersionArray[1])
		# currentPVer		= int(currentVersionArray[2])

		code = SublimeSocketAPISettings.VERIFICATION_CODE_REFUSED_DIFFERENT_SUBLIMESOCKET

		isDryRun = False
		if SublimeSocketAPISettings.VERSIONVERIFY_DRYRUN in params:
			isDryRun = params[SublimeSocketAPISettings.VERSIONVERIFY_DRYRUN]

		# major check
		if targetMajor < currentMajor:
			code = SublimeSocketAPISettings.VERIFICATION_CODE_REFUSED_CLIENT_UPDATE
			self.sendVerifiedResultMessage(code, isDryRun, targetSocketVersion, SublimeSocketAPISettings.SOCKET_VERSION, targetVersion, currentVersion, client)

		elif targetMajor == currentMajor:
			if targetMinor < currentMinor:
				code = SublimeSocketAPISettings.VERIFICATION_CODE_VERIFIED_CLIENT_UPDATE
				self.sendVerifiedResultMessage(code, isDryRun, targetSocketVersion, SublimeSocketAPISettings.SOCKET_VERSION, targetVersion, currentVersion, client)

			elif targetMinor == currentMinor:
				code = SublimeSocketAPISettings.VERIFICATION_CODE_VERIFIED
				self.sendVerifiedResultMessage(code, isDryRun, targetSocketVersion, SublimeSocketAPISettings.SOCKET_VERSION, targetVersion, currentVersion, client)

			else:
				code = SublimeSocketAPISettings.VERIFICATION_CODE_REFUSED_SUBLIMESOCKET_UPDATE
				self.sendVerifiedResultMessage(code, isDryRun, targetSocketVersion, SublimeSocketAPISettings.SOCKET_VERSION, targetVersion, currentVersion, client)
				
		else:
			code = SublimeSocketAPISettings.VERIFICATION_CODE_REFUSED_SUBLIMESOCKET_UPDATE
			self.sendVerifiedResultMessage(code, isDryRun, targetSocketVersion, SublimeSocketAPISettings.SOCKET_VERSION, targetVersion, currentVersion, client)

		self.setResultsParams(results, self.versionVerify, {"result":code})

	## send result to client then exit or continue WebSocket connection.
	def sendVerifiedResultMessage(self, resultCode, isDryRun, targetSocketVersion, currentSocketVersion, targetAPIVersion, currentAPIVersion, client):
		# python-switch
		for case in PythonSwitch(resultCode):
			if case(SublimeSocketAPISettings.VERIFICATION_CODE_REFUSED_DIFFERENT_SUBLIMESOCKET):
				message = "REFUSED/DIFFERENT_SUBLIMESOCKET:	The current running SublimeSocket version = "+str(currentSocketVersion)+", please choose the other version of SublimeSocket. this client requires SublimeSocket "+str(targetSocketVersion)+", see https://github.com/sassembla/SublimeSocket"
				buf = self.encoder.text(message, mask=0)
				client.send(buf);

				if not isDryRun:
					client.close()
					self.server.deleteClientId(client.clientId)
			
				break
			if case(SublimeSocketAPISettings.VERIFICATION_CODE_VERIFIED):
				message = "VERIFIED:	The current running SublimeSocket api version = "+currentAPIVersion+", SublimeSocket "+str(currentSocketVersion)
				buf = self.encoder.text(message, mask=0)
				client.send(buf)
				break
			if case(SublimeSocketAPISettings.VERIFICATION_CODE_VERIFIED_CLIENT_UPDATE):
				message = "VERIFIED/CLIENT_UPDATE: The current running SublimeSocket api version = "+currentAPIVersion+", this client requires api version = "+str(targetAPIVersion)+", please update this client if possible."
				buf = self.encoder.text(message, mask=0)
				client.send(buf);
				break

			if case(SublimeSocketAPISettings.VERIFICATION_CODE_REFUSED_SUBLIMESOCKET_UPDATE):
				message = "REFUSED/SUBLIMESOCKET_UPDATE:	The current running SublimeSocket api version = "+currentAPIVersion+", this is out of date. please update SublimeSocket. this client requires SublimeSocket "+str(targetAPIVersion)+", see https://github.com/sassembla/SublimeSocket"
				buf = self.encoder.text(message, mask=0)
				client.send(buf);

				if not isDryRun:
					client.close()
					self.server.deleteClientId(client.clientId)

				break

			if case(SublimeSocketAPISettings.VERIFICATION_CODE_REFUSED_CLIENT_UPDATE):
				message = "REFUSED/CLIENT_UPDATE:	The current running SublimeSocket api version = "+currentAPIVersion+", this client requires api version = "+str(targetAPIVersion)+", required api version is too old. please update this client."
				buf = self.encoder.text(message, mask=0)
				client.send(buf);

				if not isDryRun:
					client.close()
					self.server.deleteClientId(client.clientId)
					
				break

		print("ss: " + message)

	def checkIfViewExist_appendRegion_Else_notFound(self, view, viewInstance, line, message, condition, results):
		# this check should be run in main thread
		return self.internal_appendRegion(viewInstance, line, message, condition)

	### region control


	## erase all regions of view/condition
	def eraseAllRegion(self, params, results):
		if SublimeSocketAPISettings.ERASEALLREGION_PATH in params:
			targetViewPath = params[SublimeSocketAPISettings.ERASEALLREGION_PATH]

			deletes = self.server.deleteAllRegionsInAllView(targetViewPath)
		else:
			deletes = self.server.deleteAllRegionsInAllView()
		
		self.setResultsParams(results, self.eraseAllRegion, {"erasedIdentities":deletes})


	## change lineCount to wordCount that is, includes the target-line index at SublimeText.
	def getLineCount_And_SetToArray(self, view, lineCount, lineArray):
		assert view is not None, "view should not be None."
		#check the namespace of inputted param
		len(lineArray)

		# Convert from 1 based to a 0 based line number
		line = int(lineCount) - 1
		# print "line	", line

		# Negative line numbers count from the end of the buffer
		if line < 0:
			lines, _ = view.rowcol(view.size())
			line = lines + line + 1
		pt = view.text_point(line, 0)

		#store params to local param.
		lineArray.append(pt)
		return pt

	## print message to console
	def printout(self, message):
		print("debug_message:", message)

	
	def formattingMessageParameters(self, params, formatKey, outputKey):
		currentFormat = params[formatKey]
		for key in params:
			if key != formatKey:
				currentParam = params[key]
				print("key is", key, "currentParam", currentParam)
				currentFormat = currentFormat.replace(key, currentParam)

		params[outputKey] = currentFormat
		del params[formatKey]

		return params

	def getKeywordBasedPath(self, path, keyword, replace):
		if path.startswith(keyword):
			filePathArray = path.split(keyword[-1])
			path = replace + filePathArray[1]

		return path

	
class InsertTextCommand(sublime_plugin.TextCommand):
	def run(self, edit, string=''):
		self.view.insert(edit, self.view.size(), string)


class ReduceTextCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		region = sublime.Region(self.view.size()-1, self.view.size())
		self.view.erase(edit, region)

