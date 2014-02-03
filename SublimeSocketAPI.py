# -*- coding: utf-8 -*-

import json
import subprocess
import shlex
import os
import time
import re
import uuid
import sys
import io

from functools import reduce
from .PythonSwitch import PythonSwitch

# choice editorApi by platform.
from .interface.SublimeText.EditorAPI import EditorAPI
from . import SublimeSocketAPISettings


## API Parse the action
class SublimeSocketAPI:
	def __init__(self, server):
		self.server = server

		self.editorAPI = EditorAPI()

		self.isTesting = False
		self.globalResults = []
		
		self.testBeforeSelectors = []
		self.testAfterSelectors = []

		self.counts = {}

		self.setSublimeSocketWindowBasePath(None)
		

	## initialize results as the part of globalResults.
	def initResult(self, resultIdentity):
		initializedResults = {resultIdentity:{}}
		self.globalResults.append(initializedResults)

		return self.globalResults[-1]

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
	def parse(self, data, clientId=None, results=None):
		
		# SAMPLE: inputIdentity:{"id":"537d5da6-ce7d-42f0-387b-d9c606465dbb"}->showAlert...|>...
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
					self.editorAPI.printMessage("JSON parse error " + str(e) + " source = " + command_params[1])
					return
					
			clientId = self.runAPI(command, params, clientId, None, results)
		return results


	def innerParse(self, data, clientId=None, results=None):
		currentResults = self.initResult("inner:"+str(uuid.uuid4()))
		innerResults = self.parse(data, clientId, currentResults)

		return self.addInnerResult(results, innerResults)


	## run the specified API with JSON parameters. Dict or Array of JSON.
	def runAPI(self, command, params, clientId=None, injectParams=None, results=None):		
		# erase comment
		if SublimeSocketAPISettings.API_COMMENT_DELIM in command:
			splitted = command.split(SublimeSocketAPISettings.API_COMMENT_DELIM, 1)
			command = splitted[1]

		# remove spaces " "
		command = command.replace(" ", "")

		# calc "<-" inject param.
		if injectParams and SublimeSocketAPISettings.COMMAND_KEYWORD_INJECT in command:
			
			splitted = command.split(SublimeSocketAPISettings.COMMAND_KEYWORD_INJECT, 1)
			command = splitted[0]
			
			accepts = splitted[1].split(SublimeSocketAPISettings.COMMAND_KEYWORD_DELIM)
			
			# empty "<-" means all injective will be inject.
			if len(accepts) == 1 and accepts[0] == "":
				accepts = list(injectParams)
			
			for acceptKey in accepts:
				if acceptKey in injectParams:
					params[acceptKey] = injectParams[acceptKey]


  		# python-switch
		for case in PythonSwitch(command):
			if case(SublimeSocketAPISettings.API_INPUTIDENTITY):
				clientId = self.inputIdentity(clientId, params, results)
				break

			if case(SublimeSocketAPISettings.API_RUNTESTS):
				self.runTests(params, clientId, results)
				break

			if case(SublimeSocketAPISettings.API_SETTESTBEFOREAFTER):
				self.setTestBeforeAfter(params, results)
				break

			if case(SublimeSocketAPISettings.API_ASSERTRESULT):
				self.assertResult(params, results)
				break

			if case(SublimeSocketAPISettings.API_COUNTUP):
				self.countUp(params, results)
				break			

			if case(SublimeSocketAPISettings.API_RESETCOUNTS):
				self.resetCounts(results)
				break

			if case(SublimeSocketAPISettings.API_RUNSETTING):
				filePath = params[SublimeSocketAPISettings.RUNSETTING_FILEPATH]

				result = self.runSetting(filePath, clientId, results)
				if clientId:
					self.server.sendMessage(clientId, result)

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

			if case(SublimeSocketAPISettings.API_SELECTEDREGIONS):
				self.selectedRegions(params, results)
				break

			if case(SublimeSocketAPISettings.API_COLLECTVIEWS):
				self.collectViews(results)
				break
				
			if case(SublimeSocketAPISettings.API_DEFINEFILTER):
				self.defineFilter(params, results)
				break

			if case(SublimeSocketAPISettings.API_FILTERING):
				self.filtering(params, results)
				break

			if case(SublimeSocketAPISettings.API_SETEVENTREACTOR):
				self.setEventReactor(params, clientId, results)
				break
				
			if case(SublimeSocketAPISettings.API_SETVIEWREACTOR):
				self.setViewReactor(params, clientId, results)
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

			if case(SublimeSocketAPISettings.API_CLEARSELECTION):
				self.clearSelection(params, results)
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

			if case(SublimeSocketAPISettings.API_SHOWTOOLTIP):
				self.showToolTip(params, results)
				break

			if case(SublimeSocketAPISettings.API_TRANSFORM):
				self.transform(params, results)
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
				self.versionVerify(params, clientId, results)
				break

			if case():
				self.editorAPI.printMessage("unknown command "+ command + " /")
				break

		return clientId


	def runReactor(self, reactorType, params, eventParam, results):
		for case in PythonSwitch(reactorType):
			if case(SublimeSocketAPISettings.REACTORTYPE_EVENT):
				# do nothing specially.
				break

			if case(SublimeSocketAPISettings.REACTORTYPE_VIEW):
				# add view param for react.
				assert SublimeSocketAPISettings.REACTOR_VIEWKEY_VIEWSELF in eventParam, "reactorType:view require 'view' info."
				
				# default injection
				params = self.insertInjectKeysToInjectionMap(params, SublimeSocketAPISettings.REACTOR_VIEWKEY_INJECTIONKEYS, SublimeSocketAPISettings.REACTOR_INJECT)
				break

		keys = []
		values = []
		for key, val in eventParam.items():
			keys.append(key)
			values.append(val)

		self.runAllSelector(
			params, 
			keys, 
			values,
			SublimeSocketAPISettings.REACTOR_INJECT, 
			results)


	def runAllSelector(self, params, injectiveKeys, injectiveValues, injectionMapKey, results):
		assert len(injectiveKeys) == len(injectiveValues), "cannot generate inective-keys and values:"+str(injectiveKeys)+" vs injects:"+str(injectiveValues)
		zippedInjectiveParams = dict(zip(injectiveKeys, injectiveValues))
		
		runnableParams = params.copy()

		# add injectionMap
		injectMapInjectedParams = self.insertInjectKeysToInjectionMap(runnableParams, injectiveKeys, injectionMapKey)

		selectors = injectMapInjectedParams[SublimeSocketAPISettings.REACTOR_SELECTORS]
		injectParams = self.injectParams(injectMapInjectedParams, zippedInjectiveParams)
		
		for selector in selectors:
			[self.runAPI(eachCommand, eachParams, None, injectParams, results) for eachCommand, eachParams in selector.items()]

		
	def runFoundationEvent(self, eventName, eventParam, reactors, results):
		for case in PythonSwitch(eventName):
			if case(SublimeSocketAPISettings.SS_FOUNDATION_NOVIEWFOUND):
				self.foundation_noViewFound(reactors, eventParam, results)
				break


	def foundation_noViewFound(self, reactDicts, eventParam, results):
		for target in list(reactDicts):
			params = reactDicts[target]
			
			keys = []
			values = []
			for key, val in eventParam.items():
				keys.append(key)
				values.append(val)

			self.runAllSelector(
				params, 
				keys, 
				values, 
				SublimeSocketAPISettings.REACTOR_INJECT, 
				results)


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
	def runSetting(self, filePath, clientId, results):
		
		# check contains PREFIX or not
		filePath = self.getKeywordBasedPath(filePath, 
			SublimeSocketAPISettings.RUNSETTING_PREFIX_SUBLIMESOCKET_PATH,
			self.editorAPI.packagePath()+ "/"+SublimeSocketAPISettings.MY_PLUGIN_PATHNAME+"/")

		self.editorAPI.printMessage("runSetting:" + filePath)
		
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
		self.innerParse(commands, clientId, currentResults)

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
				
			self.editorAPI.runAfterDelay(self.runShell(params), delay)
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
					self.editorAPI.packagePath() + "/"+SublimeSocketAPISettings.MY_PLUGIN_PATHNAME+"/")

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
			self.editorAPI.printMessage("runnable " + runnable)
		
		if len(runnable):
			subprocess.call(runnable, shell=True)
			if results:
				self.setResultsParams(results, self.runShell, {"runnable":runnable})
			

	## emit message to clients.
	# broadcast messages if no-"target" key.
	def broadcastMessage(self, params, results):
		assert SublimeSocketAPISettings.OUTPUT_MESSAGE in params, "broadcastMessage require 'message' param."
		
		message = params[SublimeSocketAPISettings.OUTPUT_MESSAGE]

		clientNames = self.server.broadcastMessage(message)
		
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
		
		
		succeeded, reason = self.server.sendMessage(target, message)

		if succeeded:
			self.setResultsParams(results, self.monocastMessage, {SublimeSocketAPISettings.OUTPUT_TARGET:target, SublimeSocketAPISettings.OUTPUT_MESSAGE:message})

		else:
			self.editorAPI.printMessage("monocastMessage failed. target: " + target + " " + reason)
			self.setResultsParams(results, self.monocastMessage, {SublimeSocketAPISettings.OUTPUT_TARGET:"", SublimeSocketAPISettings.OUTPUT_MESSAGE:message})
	


	## send message to the other via SS.
	def showAtLog(self, params, results=None):
		if SublimeSocketAPISettings.LOG_FORMAT in params:
			params = self.formattingMessageParameters(params, SublimeSocketAPISettings.LOG_FORMAT, SublimeSocketAPISettings.LOG_MESSAGE)
			self.showAtLog(params, results)
			return

		assert SublimeSocketAPISettings.LOG_MESSAGE in params, "showAtLog require 'message' param."
		message = params[SublimeSocketAPISettings.LOG_MESSAGE]
		self.editorAPI.printMessage(message)

		self.setResultsParams(results, self.showAtLog, {"output":message})


	def showDialog(self, params, results):
		if SublimeSocketAPISettings.SHOWDIALOG_FORMAT in params:
			params = self.formattingMessageParameters(params, SublimeSocketAPISettings.SHOWDIALOG_FORMAT, SublimeSocketAPISettings.SHOWDIALOG_MESSAGE)
			self.showDialog(params, results)
			return

		assert SublimeSocketAPISettings.SHOWDIALOG_MESSAGE in params, "showDialog require 'message' param."
		message = params[SublimeSocketAPISettings.LOG_MESSAGE]

		self.editorAPI.showMessageDialog(message)

		self.setResultsParams(results, self.showDialog, {"output":message})


	def showToolTip(self, params, results):
		assert SublimeSocketAPISettings.SHOWTOOLTIP_ONSELECTED in params, "showToolTip require 'onselected' params."
		selects = params[SublimeSocketAPISettings.SHOWTOOLTIP_ONSELECTED]

		if selects:
			pass
		else:
			return

		assert SublimeSocketAPISettings.SHOWTOOLTIP_ONCANCELLED in params, "showToolTip require 'oncancelled' param."
		cancelled = params[SublimeSocketAPISettings.SHOWTOOLTIP_ONCANCELLED]
		

		finallyBlock = []
		if SublimeSocketAPISettings.SHOWTOOLTIP_FINALLY in params:
			finallyBlock = params[SublimeSocketAPISettings.SHOWTOOLTIP_FINALLY]

		view, path = self.internal_getViewAndPathFromViewOrName(params, SublimeSocketAPISettings.SHOWTOOLTIP_VIEW, SublimeSocketAPISettings.SHOWTOOLTIP_NAME)

		assert view, "showToolTip require 'view' or 'name' param."

		def getItemKey(item):
			itemList = list(item)
			assert len(itemList) == 1, "multiple items found in one items. not valid. at:"+str(item)
			key = itemList[0]
			return key

		tooltipItemKeys = [getItemKey(item) for item in selects]

		# run after the tooltip selected or cancelled.
		def toolTipClosed(index):
			selectedItem = "cancelled"
			
			if -1 < index:
				if index < len(selects):
					selectedItem = tooltipItemKeys[index]

					itemDict = selects[index]
					key = list(itemDict)[0]

					# rename from "onselected" to "selector".
					selectorInsideParams = params
					selectorInsideParams[SublimeSocketAPISettings.REACTOR_SELECTORS] = itemDict[key]
					
					self.runAllSelector(
						selectorInsideParams, 
						SublimeSocketAPISettings.SHOWTOOLTIP_INJECTIONKEYS, 
						[view, path, selectedItem], 
						SublimeSocketAPISettings.REACTOR_INJECT, 
						results)
			else:
				if cancelled:
					# rename from "cancelled" to "selector".
					selectorInsideParams = params
					selectorInsideParams[SublimeSocketAPISettings.REACTOR_SELECTORS] = cancelled
					
					self.runAllSelector(
						selectorInsideParams, 
						SublimeSocketAPISettings.SHOWTOOLTIP_INJECTIONKEYS, 
						[view, path, selectedItem], 
						SublimeSocketAPISettings.REACTOR_INJECT, 
						results)

			if finallyBlock:
				# rename from "finally" to "selector".
				selectorInsideParams = params
				selectorInsideParams[SublimeSocketAPISettings.REACTOR_SELECTORS] = finallyBlock

				self.runAllSelector(
					selectorInsideParams, 
					SublimeSocketAPISettings.SHOWTOOLTIP_INJECTIONKEYS, 
					[view, path, selectedItem], 
					SublimeSocketAPISettings.REACTOR_INJECT, 
					results)

			self.setResultsParams(results, self.showToolTip, {"items":tooltipItemKeys})

		print("最悪、ここでuniqueかけることができる。そも入れる時点でかさなってるかどうかチェックすればいいわなあ、、", tooltipItemKeys)
		self.editorAPI.showPopupMenu(view, tooltipItemKeys, toolTipClosed)


	def transform(self, params, results):
		assert SublimeSocketAPISettings.TARANSFORM_TRANSFORMER in params, "transform require 'transformer' params."
		assert SublimeSocketAPISettings.TARANSFORM_SELECTOR in params,  "transform require 'selector' params."
		
		debug = False
		if SublimeSocketAPISettings.TARANSFORM_DEBUG in params:
			debug = params[SublimeSocketAPISettings.TARANSFORM_DEBUG]
		
		transformer = params[SublimeSocketAPISettings.TARANSFORM_TRANSFORMER]
		transformerName = self.getKeywordBasedPath(transformer, 
			SublimeSocketAPISettings.RUNSETTING_PREFIX_SUBLIMESOCKET_PATH,
			self.editorAPI.packagePath() + "/"+SublimeSocketAPISettings.MY_PLUGIN_PATHNAME+"/")

		if debug:
			print("transformer's path:"+transformerName)

		selector = params[SublimeSocketAPISettings.TARANSFORM_SELECTOR]
		assert len(selector) == 1, "only one selector can run through transform."

		inputs = params.copy()

		assert os.path.exists(transformerName), "transformer not exist at:"+transformerName
		
		
		code = None
		with open(transformerName, encoding='utf8') as f:
			code = compile(f.read(), transformerName, "exec")
		
		assert code, "no transformer generated. failed to generate from:"+transformerName
		
		start = str(uuid.uuid4())
		delim = str(uuid.uuid4())
		keyHeader = "key:"
		valHeader = "val:"
		
		result = []

		before = sys.stdout
		try:
			def output(paramDict):
				print(start)
				iterated = False
				for key, val in paramDict.items():
					if iterated:
						print(delim)

					print(keyHeader+key)

					# convert to JSON
					jsonVal = json.dumps(val)
				
					print(valHeader+jsonVal)

					iterated = True
			
			# set stdout
			sys.stdout = TransformerStream(result)
		
			# run transformer.py DSL.
			exec(code, {"inputs":params, "keys":list(params), "output":output}, None)

			
		except Exception as e:
			print("failed to run transform:"+str(e))
		finally:
			# reset stdout.
			sys.stdout = before

		if debug:
			print("unfixed result:"+str(result))
		
		def composeResultList(keyOrValueOrDelim):
			if keyOrValueOrDelim.startswith(keyHeader):
				key = keyOrValueOrDelim[len(keyHeader):]
				assert key, "no key found error in transform. output(parametersDict) key is None or something wrong."
				return key

			elif keyOrValueOrDelim.startswith(valHeader):
				jsonVal = keyOrValueOrDelim[len(valHeader):]
				assert jsonVal, "no value found error in transform. output(parametersDict) value is None or something wrong."

				# re-pack to value, list, dict.
				val = json.loads(jsonVal)
				return val

		
		naturalResultList = [s for s in result if s != "\n" and s != delim]
		
		if start in naturalResultList:
			pass
		else:
			assert False, "at:" + transformerName + " failed to get result. reason:"+str(naturalResultList)
		
		index = naturalResultList.index(start)+1 #next to start

		resultList = [composeResultList(s) for s in naturalResultList[index:]]
		resultParam = dict(zip(resultList[0::2], resultList[1::2]))

		if debug:
			print("resultParam:"+str(resultParam))

		# run selector.
		# inject all keys and values.
		keys = []
		values = []

		for key, val in resultParam.items():
			keys.append(key)
			values.append(val)

		selectorParams = {
			SublimeSocketAPISettings.REACTOR_SELECTORS:[selector]
		}
		print("selectorParams", selectorParams)
		self.runAllSelector(
			selectorParams, 
			keys, 
			values, 
			SublimeSocketAPISettings.REACTOR_INJECT, 
			results)



	## run testus
	def runTests(self, params, clientId, results):
		assert SublimeSocketAPISettings.RUNTESTS_PATH in params, "runTests require 'path' param."
		filePath = params[SublimeSocketAPISettings.RUNTESTS_PATH]

		# check contains PREFIX of path or not
		filePath = self.getKeywordBasedPath(filePath, 
			SublimeSocketAPISettings.RUNSETTING_PREFIX_SUBLIMESOCKET_PATH,
			self.editorAPI.packagePath() + "/"+SublimeSocketAPISettings.MY_PLUGIN_PATHNAME+"/")
		
		settingFile = open(filePath, 'r', encoding='utf8')
		
		setting = settingFile.read()
		settingFile.close()

		# remove //comment line
		removeCommented_setting = re.sub(r'//.*', r'', setting)
		
		# remove spaces
		removeSpaces_setting = re.sub(r'(?m)^\s+', '', removeCommented_setting)
		
		# remove CRLF
		removeCRLF_setting = removeSpaces_setting.replace("\n", "")
		testSources = removeCRLF_setting
		
		# load test delimited scripts.
		testCases = testSources.split(SublimeSocketAPISettings.API_TESTCASE_DELIM)
		
		def runTestCase(testCase):
			passedCount = 0
			failedCount = 0

			# start test
			self.isTesting = True
		
			# reset globalResults
			self.globalResults = []

			currentTestResults = self.initResult("test:"+str(uuid.uuid4()))

			# before block
			if self.testBeforeSelectors:

				self.runAllSelector(
					{SublimeSocketAPISettings.SETTESTBEFOREAFTER_SELECTORS:self.testBeforeSelectors}, 
					[], [], SublimeSocketAPISettings.REACTOR_SELECTORS,
					currentTestResults)

			# parse then get results
			currentTestResults = self.parse(testCase, clientId, currentTestResults)
			
			# after block
			if self.testAfterSelectors:

				self.runAllSelector(
					{SublimeSocketAPISettings.SETTESTBEFOREAFTER_SELECTORS:self.testAfterSelectors}, 
					[], [], SublimeSocketAPISettings.REACTOR_SELECTORS,
					currentTestResults)

			# end test
			self.isTesting = False


			# reduce results
			for resultKey in currentTestResults:
				for apiNameAndId in list(currentTestResults[resultKey]):

					# result of assertResult
					if SublimeSocketAPISettings.API_ASSERTRESULT in apiNameAndId[0]:
						assertResultResult = currentTestResults[resultKey][apiNameAndId]

						if SublimeSocketAPISettings.ASSERTRESULT_PASSEDORFAILED in assertResultResult:
							
							if SublimeSocketAPISettings.ASSERTRESULT_VALUE_PASS in assertResultResult[SublimeSocketAPISettings.ASSERTRESULT_PASSEDORFAILED]:
								passedCount = passedCount + 1
								
							else:
								failedCount = failedCount + 1

							result = assertResultResult[SublimeSocketAPISettings.ASSERTRESULT_RESULT]
							self.server.broadcastMessage(result)


			return (passedCount, failedCount)

		resultCounts = [runTestCase(testCase) for testCase in testCases]
		

		# reset counts
		testPassedCount = 0
		testFailedCount = 0

		for passed, failed in resultCounts:
			testPassedCount = testPassedCount + passed
			testFailedCount = testFailedCount + failed

		# count ASSERTRESULT_VALUE_PASS or ASSERTRESULT_VALUE_FAIL
		totalResultMessage = "TOTAL:" + str(testPassedCount + testFailedCount) + " passed:" + str(testPassedCount) + " failed:" + str(testFailedCount)
		self.server.broadcastMessage(totalResultMessage)


	def setTestBeforeAfter(self, params, results):
		assert SublimeSocketAPISettings.SETTESTBEFOREAFTER_BEFORESELECTORS in params, "setTestBeforeAfter require 'beforeselectors' param."
		assert SublimeSocketAPISettings.SETTESTBEFOREAFTER_AFTERSELECTORS in params, "setTestBeforeAfter require 'afterselectors' param."
		
		self.testBeforeSelectors = params[SublimeSocketAPISettings.SETTESTBEFOREAFTER_BEFORESELECTORS]
		self.testAfterSelectors = params[SublimeSocketAPISettings.SETTESTBEFOREAFTER_AFTERSELECTORS]
	

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
			
			def checkIsResultsOf(currentContext, currentContextKeyword):
				key = list(currentContext)[0]
				
				if currentContextKeyword in key:
					return True
					
				return False

			def collectResultsContextValues(currentContext):
				key = list(currentContext)[0]
				value = currentContext[key]

				return value
				
			unmergedResultsList = [collectResultsContextValues(context) for context in self.globalResults if checkIsResultsOf(context, contextKeyword)]

			resultValues = {}
			mergedResults = {}
			
			for item in unmergedResultsList:
				for key in list(item):
					resultValues[key] = item[key]
			
			results = {contextKeyword:resultValues}
			
		# load results for check
		resultBodies = self.resultBody(results)
		if debug:
			self.editorAPI.printMessage("\nassertResult:\nid:" + identity + "\nresultBodies:" + str(resultBodies) + "\n:assertResult\n")


		assertionIdentity = params[SublimeSocketAPISettings.ASSERTRESULT_ID]
		message = params[SublimeSocketAPISettings.ASSERTRESULT_DESCRIPTION]
		
		

		def setAssertionResult(passedOrFailed, assertionIdentity, message, results):

			def assertionMessage(assertType, currentIdentity, currentMessage):
				return assertType + " " + currentIdentity + " : " + currentMessage

			resultMessage = assertionMessage(passedOrFailed,
								assertionIdentity, 
								message)
			
			self.setResultsParams(results, self.assertResult, {SublimeSocketAPISettings.ASSERTRESULT_RESULT:resultMessage, SublimeSocketAPISettings.ASSERTRESULT_PASSEDORFAILED:passedOrFailed})
			

		# contains
		if SublimeSocketAPISettings.ASSERTRESULT_CONTAINS in params:
			currentDict = params[SublimeSocketAPISettings.ASSERTRESULT_CONTAINS]
			if debug:
				self.editorAPI.printMessage("start assertResult 'contains' in " + identity + " " + str(resultBodies))

			# match
			for key in currentDict:
				for resultKey in resultBodies:
					if resultKey[0] == key:
						assertValue = currentDict[key]
						assertTarget = resultBodies[resultKey]
						if debug:
							self.editorAPI.printMessage("expected:" + str(assertValue) + "\n" + "actual:" + str(assertTarget) + "\n")

						if assertValue == assertTarget:
							setAssertionResult(SublimeSocketAPISettings.ASSERTRESULT_VALUE_PASS,
								assertionIdentity, 
								key + ":" + str(assertValue) + " in " + str(resultBodies[resultKey]),
								results)
							return

			# fail
			if debug:
				self.editorAPI.printMessage("failed assertResult 'contains' in" + identity)

			setAssertionResult(SublimeSocketAPISettings.ASSERTRESULT_VALUE_FAIL,
				assertionIdentity, 
				message,
				results)
			return


		# not contains
		if SublimeSocketAPISettings.ASSERTRESULT_NOTCONTAINS in params:
			currentDict = params[SublimeSocketAPISettings.ASSERTRESULT_NOTCONTAINS]
			if debug:
				self.editorAPI.printMessage("start assertResult 'not contains' in " + identity + " " + str(resultBodies))

			# match
			for key in currentDict:
				for resultKey in resultBodies:
					if resultKey[0] == key:
						assertValue = currentDict[key]
						assertTarget = resultBodies[resultKey]

						if assertValue == assertTarget:
							if debug:
								self.editorAPI.printMessage("failed assertResult 'not contains' in " + identity)

							setAssertionResult(SublimeSocketAPISettings.ASSERTRESULT_VALUE_FAIL,
								assertionIdentity, 
								key + ":" + str(assertValue) + " in " + str(resultBodies[resultKey]),
								results)
							return

			# pass
			setAssertionResult(SublimeSocketAPISettings.ASSERTRESULT_VALUE_PASS,
								assertionIdentity, 
								message,
								results)
			return


		# is empty or not
		elif SublimeSocketAPISettings.ASSERTRESULT_ISEMPTY in params:
			if debug:
				self.editorAPI.printMessage("start assertResult 'isempty' in " + identity + " " + str(resultBodies))

			# match
			if not resultBodies:
				setAssertionResult(SublimeSocketAPISettings.ASSERTRESULT_VALUE_PASS,
					assertionIdentity, 
					"is empty.",
					results)
				return

			# fail
			if debug:
				self.editorAPI.printMessage("failed assertResult 'empty' in " + identity)

			setAssertionResult(SublimeSocketAPISettings.ASSERTRESULT_VALUE_FAIL,
				assertionIdentity, 
				message,
				results)
			return

			

		# is not empty or empty
		elif SublimeSocketAPISettings.ASSERTRESULT_ISNOTEMPTY in params:
			if debug:
				self.editorAPI.printMessage("start assertResult 'isnotempty' in " + identity + str(resultBodies))

			targetAPIKey = params[SublimeSocketAPISettings.ASSERTRESULT_ISNOTEMPTY]
			
			for resultKey in resultBodies:
				if resultKey[0] == targetAPIKey:
					setAssertionResult(SublimeSocketAPISettings.ASSERTRESULT_VALUE_PASS,
						assertionIdentity, 
						"is not empty.",
						results)
					return

			# fail
			if debug:
				self.editorAPI.printMessage("failed assertResult 'isnotempty' in " + identity)

			setAssertionResult(SublimeSocketAPISettings.ASSERTRESULT_VALUE_FAIL,
				assertionIdentity, 
				message,
				results)
			return
			
		if debug:
				self.editorAPI.printMessage("assertion aborted in assertResult API. " + message + " " + identity)

		setAssertionResult(SublimeSocketAPISettings.ASSERTRESULT_VALUE_FAIL,
			assertionIdentity,
			"assertion aborted in assertResult API.",
			results)
		return
		
	
	## input identity to client.
	def inputIdentity(self, clientId, params, results):
		assert SublimeSocketAPISettings.IDENTITY_ID in params, "updateClientId requre 'id' param"
		newIdentity = params[SublimeSocketAPISettings.IDENTITY_ID]

		self.server.transfer.updateClientId(clientId, newIdentity)
		self.setResultsParams(results, self.inputIdentity, {"inputIdentity":newIdentity})

		return newIdentity

	## create buffer then set contents if exist.
	def createBuffer(self, params, results):
		assert SublimeSocketAPISettings.CREATEBUFFER_NAME in params, "createBuffer require 'name' param"
		
		name = params[SublimeSocketAPISettings.CREATEBUFFER_NAME]

		if self.editorAPI.isBuffer(name):
			pass
		else:
			result = "failed to create buffer "+ name +" because of the file is already exists."
			self.setResultsParams(results, self.createBuffer, {"result":result, SublimeSocketAPISettings.CREATEBUFFER_NAME:name})
			return


		# renew event will run, but the view will not store KVS because of no-name view.
		view = self.editorAPI.openFile(name)

		# buffer generated then set name and store to KVS.
		message = "buffer "+ name +" created."
		result = message

		self.editorAPI.setNameToView(view, name)
		
		# restore to KVS with name
		viewParams = self.editorAPI.generateSublimeViewInfo(
						view,
						SublimeSocketAPISettings.VIEW_SELF,
						SublimeSocketAPISettings.VIEW_ID,
						SublimeSocketAPISettings.VIEW_BUFFERID,
						SublimeSocketAPISettings.VIEW_PATH,
						SublimeSocketAPISettings.VIEW_BASENAME,
						SublimeSocketAPISettings.VIEW_VNAME,
						SublimeSocketAPISettings.VIEW_SELECTEDS,
						SublimeSocketAPISettings.VIEW_ISEXIST
					)

		emitIdentity = str(uuid.uuid4())
		viewParams[SublimeSocketAPISettings.REACTOR_VIEWKEY_EMITIDENTITY] = emitIdentity

		self.fireReactor(
			SublimeSocketAPISettings.REACTORTYPE_VIEW,
			SublimeSocketAPISettings.SS_EVENT_RENAMED, 
			viewParams,
			results)

		# if "contents" exist, set contents to buffer.
		if SublimeSocketAPISettings.CREATEBUFFER_CONTENTS in params:
			contents = params[SublimeSocketAPISettings.CREATEBUFFER_CONTENTS]
			self.editorAPI.runCommandOnView('insert_text', {'string': contents})
		
		self.setResultsParams(results, self.createBuffer, {"result":result, SublimeSocketAPISettings.CREATEBUFFER_NAME:name})
		
	
	## open file
	def openFile(self, params, results):
		assert SublimeSocketAPISettings.OPENFILE_PATH in params, "openFile require 'path' key."
		original_path = params[SublimeSocketAPISettings.OPENFILE_PATH]
		name = original_path

		name = self.getKeywordBasedPath(name, 
			SublimeSocketAPISettings.RUNSETTING_PREFIX_SUBLIMESOCKET_PATH,
			self.editorAPI.packagePath() + "/"+SublimeSocketAPISettings.MY_PLUGIN_PATHNAME+"/")

		if self.editorAPI.isBuffer(name):
			message = "file " + original_path + " is not exist."
			self.editorAPI.printMessage(message)

			result = message
		

		else:
			view = self.editorAPI.openFile(name)
		
			message = "file " + original_path + " is opened."
			self.editorAPI.printMessage(message)
		
			result = message

			viewParams = self.editorAPI.generateSublimeViewInfo(
							view,
							SublimeSocketAPISettings.VIEW_SELF,
							SublimeSocketAPISettings.VIEW_ID,
							SublimeSocketAPISettings.VIEW_BUFFERID,
							SublimeSocketAPISettings.VIEW_PATH,
							SublimeSocketAPISettings.VIEW_BASENAME,
							SublimeSocketAPISettings.VIEW_VNAME,
							SublimeSocketAPISettings.VIEW_SELECTEDS,
							SublimeSocketAPISettings.VIEW_ISEXIST
						)

			emitIdentity = str(uuid.uuid4())
			viewParams[SublimeSocketAPISettings.REACTOR_VIEWKEY_EMITIDENTITY] = emitIdentity

			
			self.fireReactor(
				SublimeSocketAPISettings.REACTORTYPE_VIEW,
				SublimeSocketAPISettings.SS_EVENT_LOADING, 
				viewParams,
				results)

		self.setResultsParams(results, self.openFile, {SublimeSocketAPISettings.OPENFILE_PATH:original_path, "result":result})
	
	## close file. if specified -> close the file. if not specified -> close current file.
	def closeFile(self, params, results):
		assert SublimeSocketAPISettings.CLOSEFILE_NAME in params, "closeFile require 'name' param."
		
		name = params[SublimeSocketAPISettings.CLOSEFILE_NAME]
		view = self.internal_detectViewInstance(name)
		
		self.editorAPI.closeView(view)
		self.setResultsParams(results, self.closeFile, {"name":name})


	def closeAllBuffer(self, results):
		closed = []

		def close(window):
			for view in self.editorAPI.viewsOfWindow(window):
				path = self.internal_detectViewPath(view)
				if self.editorAPI.isBuffer(path):
					closed.append(path)

					self.editorAPI.closeView(view)

		[close(window) for window in self.editorAPI.windows()]

		self.setResultsParams(results, self.closeAllBuffer, {"closed":closed})

	# run selected regions.
	def selectedRegions(self, params, results):
		assert SublimeSocketAPISettings.SELECTEDREGIONS_SELECTEDS in params, "selectedRegions require 'selecteds' param."
		assert SublimeSocketAPISettings.SELECTEDREGIONS_TARGET in params, "selectedRegions require 'target' param."
		assert SublimeSocketAPISettings.SELECTEDREGIONS_SELECTORS in params, "selectedRegions require 'selectors' param."

		(view, path) = self.internal_getViewAndPathFromViewOrName(params, SublimeSocketAPISettings.SELECTEDREGIONS_VIEW, SublimeSocketAPISettings.SELECTEDREGIONS_NAME)
		
		selecteds = params[SublimeSocketAPISettings.SELECTEDREGIONS_SELECTEDS]
		regionsDict = self.server.regionsDict()
		
		# run selector if selected region contains 
		if path in regionsDict:
			target = params[SublimeSocketAPISettings.SELECTEDREGIONS_TARGET]

			# if already sekected, no event running.
			currentSelectedRegionIdsSet = self.server.selectingRegionIds(path)

			regionsDictOfThisView = regionsDict[path]

			# search each region identity
			def isRegionSelected(regionData):
				regionFrom = regionData[SublimeSocketAPISettings.REGION_FROM]
				regionTo = regionData[SublimeSocketAPISettings.REGION_TO]
				region = self.editorAPI.generateRegion(regionFrom, regionTo)

				if self.editorAPI.isRegionContained(region, selecteds):
					return True
				return False

			latestContainedRegionIdentities = [regionIdentity for regionIdentity, regionData in regionsDictOfThisView.items() if isRegionSelected(regionData)]
			
			# run each region's each regionDatas.
			for containedRegionId in latestContainedRegionIdentities:
				
				if containedRegionId in currentSelectedRegionIdsSet:
					continue
				else:
					pass

				regionDatas = regionsDictOfThisView[containedRegionId]
				line = regionDatas[SublimeSocketAPISettings.SELECTEDREGIONS_LINE]
				fromParam = regionDatas[SublimeSocketAPISettings.SELECTEDREGIONS_FROM]
				toParam = regionDatas[SublimeSocketAPISettings.SELECTEDREGIONS_TO]
				messages = regionDatas[SublimeSocketAPISettings.SELECTEDREGIONS_MESSAGES]

				# add the line contents of this region. selection x region
				crossed = self.editorAPI.crossedContents(view, fromParam, toParam)

				self.runAllSelector(
					params, 
					SublimeSocketAPISettings.SELECTEDREGIONS_INJECTIONKEYS, 
					[view, path, crossed, target, line, fromParam, toParam, messages], 
					SublimeSocketAPISettings.SELECTEDREGIONS_INJECT, 
					results)

			# update current contained region for preventing double-run.
			self.server.updateSelectingRegionIdsAndResetOthers(path, latestContainedRegionIdentities)
			currentSelectedRegionIdsSet = self.server.selectingRegionIds(path)

	def defineFilter(self, params, results):
		assert SublimeSocketAPISettings.DEFINEFILTER_NAME in params, "defineFilter require 'name' key."

		# load defined filters
		filterNameAndPatternsArray = self.server.filtersDict()

		filterName = params[SublimeSocketAPISettings.DEFINEFILTER_NAME]

		patterns = params[SublimeSocketAPISettings.DEFINEFILTER_PATTERNS]
		assert type(patterns) == list, "defineFilter require: filterPatterns must be list."

		def mustBeSingleDict(filterDict):
			assert len(filterDict) is 1, "defineFilter. too many filter in one dictionary. len is "+str(len(filterDict))
			

		[mustBeSingleDict(currentFilterDict) for currentFilterDict in patterns]

		filterNameAndPatternsArray[filterName] = patterns
		self.server.updateFiltersDict(filterNameAndPatternsArray)

		self.setResultsParams(results, self.defineFilter, {"defined":params})
		

	def filtering(self, params, results):
		assert SublimeSocketAPISettings.FILTERING_NAME in params, "filtering require 'filterName' param."
		filterName = params[SublimeSocketAPISettings.FILTERING_NAME]


		debug = False
		if SublimeSocketAPISettings.FILTERING_DEBUG in params:
			debug = params[SublimeSocketAPISettings.FILTERING_DEBUG]



		filtersDict = self.server.filtersDict()
		if filterName in filtersDict:
			pass

		else:
			self.editorAPI.printMessage("filterName:"+str(filterName) + " " + "is not yet defined.")
			return

		filterSource = params[SublimeSocketAPISettings.FILTERING_SOURCE]

		# get filter key-values array
		filterPatternsArray = filtersDict[filterName]

		# print "filterPatternsArray", filterPatternsArray
		currentResults = []
		for pattern in filterPatternsArray:
			
			for key_executableDictPair in pattern.items():
				(key, executablesDict) = key_executableDictPair

			
			if debug:
				self.editorAPI.printMessage("filterName:"+str(filterName))
				self.editorAPI.printMessage("pattern:" + pattern)
				self.editorAPI.printMessage("executablesDict:" + executablesDict)

			dotall = False
			if SublimeSocketAPISettings.DEFINEFILTER_DOTALL in executablesDict:
				dotall = executablesDict[SublimeSocketAPISettings.DEFINEFILTER_DOTALL]

			# search
			if dotall:
				searchResult = re.finditer(re.compile(r'%s' % key, re.M | re.DOTALL), filterSource)				
			else:
				searchResult = re.finditer(re.compile(r'%s' % key, re.M), filterSource)

			
			for searched in searchResult:
				if searched:
					executablesArray = executablesDict[SublimeSocketAPISettings.DEFINEFILTER_SELECTORS]
					
					if debug:
						self.editorAPI.printMessage("matched defineFilter selectors:" + executablesArray)
						self.editorAPI.printMessage("filterSource\n---------------------\n" + filterSource + "\n---------------------")
						self.editorAPI.printMessage("matched group():" + searched.group())
						self.editorAPI.printMessage("matched groups():" + searched.groups())
					
						if SublimeSocketAPISettings.DEFINEFILTER_COMMENT in executablesDict:
							self.editorAPI.printMessage("matched defineFilter comment:" + executablesDict[SublimeSocketAPISettings.DEFINEFILTER_COMMENT])

					currentGroupSize = len(searched.groups())
					
					# run
					for executableDict in executablesArray:
						
						# execute
						for executableDictKey in executableDict.keys():
							command = executableDictKey
							break
						
						
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
							self.editorAPI.printMessage("filtering warning:unknown type")
						
						if debug:
							self.editorAPI.printMessage("filtering command:" + command + " params:" + params)

						# execute
						self.runAPI(command, params, None, None, results)
						
						# report
						currentResults.append({filterName:params})

				else:
					if debug:
						self.editorAPI.printMessage("filtering not match")

		# return succeded signal
		if 0 < len(currentResults):
			# set params into results
			self.setResultsParams(results, self.filtering, currentResults)


	## set reactor for reactive-event
	def setEventReactor(self, params, clientId, results):
		reactors = self.setReactor(SublimeSocketAPISettings.REACTORTYPE_EVENT, params)
		self.setResultsParams(results, self.setEventReactor, {"eventreactors":reactors})

	## set reactor for view
	def setViewReactor(self, params, clientId, results):
		reactors = self.setReactor(SublimeSocketAPISettings.REACTORTYPE_VIEW, params)
		self.setResultsParams(results, self.setViewReactor, {"viewreactors":reactors})
		
	## erase all reactors
	def resetReactors(self, params, results):
		deletedReactors = self.removeAllReactors()

		self.setResultsParams(results, self.resetReactors, {"deletedReactors":deletedReactors})


	def viewEmit(self, params, results):
		assert SublimeSocketAPISettings.VIEWEMIT_IDENTITY in params, "viewEmit require 'identity' param."
		assert SublimeSocketAPISettings.VIEWEMIT_SELECTORS in params, "viewEmit require 'selectors' param."
		
		identity = params[SublimeSocketAPISettings.VIEWEMIT_IDENTITY]

		# delay
		delay = 0
		if SublimeSocketAPISettings.VIEWEMIT_DELAY in params:
			delay = params[SublimeSocketAPISettings.VIEWEMIT_DELAY]

		(view, path) = self.internal_getViewAndPathFromViewOrName(params, SublimeSocketAPISettings.VIEWEMIT_VIEW, SublimeSocketAPISettings.VIEWEMIT_NAME)
		
		if view:
			name = path
			if SublimeSocketAPISettings.VIEWEMIT_NAME in params:
					name = params[SublimeSocketAPISettings.VIEWEMIT_NAME]

			if not self.isExecutableWithDelay(SublimeSocketAPISettings.SS_FOUNDATION_VIEWEMIT, identity, delay):
				self.setResultsParams(results, self.viewEmit, {
						SublimeSocketAPISettings.VIEWEMIT_IDENTITY:identity, 
						SublimeSocketAPISettings.VIEWEMIT_NAME:name,
						"result": "cancelled"
					}
				)

			else:
				body = self.editorAPI.bodyOfView(view)
				modifiedPath = path.replace(":","&").replace("\\", "/")

				# get modifying line num
				rowColStr = self.editorAPI.selectionAsStr(view)

				self.runAllSelector(
					params, 
					SublimeSocketAPISettings.VIEWEMIT_INJECTIONKEYS, 
					[view, body, modifiedPath, rowColStr, identity], 
					SublimeSocketAPISettings.VIEWEMIT_INJECT, 
					results)

				self.setResultsParams(results, self.viewEmit, {
						SublimeSocketAPISettings.VIEWEMIT_IDENTITY:identity, 
						SublimeSocketAPISettings.VIEWEMIT_NAME:name,
						"result": "done"
					}
				)


	def modifyView(self, params, results):
		(view, path) = self.internal_getViewAndPathFromViewOrName(params, SublimeSocketAPISettings.MODIFYVIEW_VIEW, SublimeSocketAPISettings.MODIFYVIEW_NAME)
		if view:
			if SublimeSocketAPISettings.MODIFYVIEW_ADD in params:
				self.editorAPI.runCommandOnView(view, 'insert_text', {'string': params[SublimeSocketAPISettings.MODIFYVIEW_ADD]})
				
			if SublimeSocketAPISettings.MODIFYVIEW_REDUCE in params:
				self.editorAPI.runCommandOnView(view, 'reduce_text')


	## generate selection to view
	def setSelection(self, params, results):
		(view, path) = self.internal_getViewAndPathFromViewOrName(params, SublimeSocketAPISettings.SETSELECTION_VIEW, SublimeSocketAPISettings.SETSELECTION_NAME)
		
		assert view, "setSelection require 'view' or 'name' param."
		
		assert SublimeSocketAPISettings.SETSELECTION_SELECTIONS in params, "setSelection require 'selections' param."
		
		selections = params[SublimeSocketAPISettings.SETSELECTION_SELECTIONS]
		
		for selection in selections:
			regionFrom = selection[SublimeSocketAPISettings.SETSELECTION_FROM]
			regionTo = selection[SublimeSocketAPISettings.SETSELECTION_TO]
			
			if regionTo < 0:
				regionFrom = 0
				regionTo = self.editorAPI.viewSize(view)

			region = self.editorAPI.generateRegion(regionFrom, regionTo)
			
			self.editorAPI.addSelectionToView(view, region)
			selected = str(region)
		
		# emit viewReactor
		viewParams = self.editorAPI.generateSublimeViewInfo(
			view,
			SublimeSocketAPISettings.VIEW_SELF,
			SublimeSocketAPISettings.VIEW_ID,
			SublimeSocketAPISettings.VIEW_BUFFERID,
			SublimeSocketAPISettings.VIEW_PATH,
			SublimeSocketAPISettings.VIEW_BASENAME,
			SublimeSocketAPISettings.VIEW_VNAME,
			SublimeSocketAPISettings.VIEW_SELECTEDS,
			SublimeSocketAPISettings.VIEW_ISEXIST)
		print("viewParams", viewParams)

		emitIdentity = str(uuid.uuid4())
		viewParams[SublimeSocketAPISettings.REACTOR_VIEWKEY_EMITIDENTITY] = emitIdentity

		self.fireReactor(SublimeSocketAPISettings.REACTORTYPE_VIEW, SublimeSocketAPISettings.SS_VIEW_ON_SELECTION_MODIFIED_BY_SETSELECTION, viewParams, results)
		self.setResultsParams(results, self.setSelection, {"selected":selected})


	def clearSelection(self, params, results):
		(view, path) = self.internal_getViewAndPathFromViewOrName(params, SublimeSocketAPISettings.CLEARSELECTION_VIEW, SublimeSocketAPISettings.CLEARSELECTION_NAME)
		assert view, "clearSelection require 'view' or 'name' param."
		
		# self.editorAPI.clearSelectionOfView(view)
		self.editorAPI.runCommandOnView(view, 'clear_selection')
		self.setResultsParams(results, self.clearSelection, {"cleared":True})



	########## APIs for shortcut ST GUI ##########

	## show message on ST
	def showStatusMessage(self, params, results):
		assert SublimeSocketAPISettings.SHOWSTATUSMESSAGE_MESSAGE in params, "showStatusMessage require 'message' param."
		message = params[SublimeSocketAPISettings.SHOWSTATUSMESSAGE_MESSAGE]
		self.editorAPI.statusMessage(message)

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
			regions = []
			regions.append(self.editorAPI.getLineRegion(view, line))

			identity = SublimeSocketAPISettings.REGION_UUID_PREFIX + str(regions[0])
			
			# add region to displaying region in view.
			self.editorAPI.addRegionToView(view, identity, regions, condition, "sublime.DRAW_OUTLINED")
			
			# store region
			regionFrom, regionTo = self.editorAPI.convertRegionToTuple(regions[0])
			

			self.server.storeRegion(path, identity, line, regionFrom, regionTo, message)

			self.setResultsParams(results, self.appendRegion, {"result":"appended", 
				SublimeSocketAPISettings.APPENDREGION_LINE:line, 
				SublimeSocketAPISettings.APPENDREGION_MESSAGE:message, 
				SublimeSocketAPISettings.APPENDREGION_CONDITION:condition})

		# raise no view found
		else:
			# use name param to notify the name of the view which not opened in editor.
			if SublimeSocketAPISettings.APPENDREGION_NAME in params:
				name = params[SublimeSocketAPISettings.APPENDREGION_NAME]
			else:
				return

			currentParams = {}
			currentParams[SublimeSocketAPISettings.NOVIEWFOUND_PATH] = name
			currentParams[SublimeSocketAPISettings.NOVIEWFOUND_LINE] = line
			currentParams[SublimeSocketAPISettings.NOVIEWFOUND_MESSAGE] = message
			currentParams[SublimeSocketAPISettings.NOVIEWFOUND_CONDITION] = condition

			self.fireReactor(SublimeSocketAPISettings.REACTORTYPE_VIEW, SublimeSocketAPISettings.SS_FOUNDATION_NOVIEWFOUND, currentParams, results)
			
			currentParams["result"] = "failed to append region."
			self.setResultsParams(results, self.appendRegion, currentParams)


	## emit notification mechanism
	def notify(self, params, results):
		assert SublimeSocketAPISettings.NOTIFY_TITLE in params, "notify require 'title' param."
		assert SublimeSocketAPISettings.NOTIFY_MESSAGE in params, "notify require 'message' param."

		title = params[SublimeSocketAPISettings.NOTIFY_TITLE]
		message = params[SublimeSocketAPISettings.NOTIFY_MESSAGE]
		
		env = self.editorAPI.platform()

		if env == "osx":
			debug = False
			if SublimeSocketAPISettings.NOTIFY_DEBUG in params:
				debug = params[SublimeSocketAPISettings.NOTIFY_DEBUG]
			
			exe = "\"" + self.editorAPI.packagePath() + "/"+SublimeSocketAPISettings.MY_PLUGIN_PATHNAME+"/tool/notification/MacNotifier.sh\""
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
			self.editorAPI.packagePath() + "/"+SublimeSocketAPISettings.MY_PLUGIN_PATHNAME+"/")

		currentFile = open(path, 'r')
		data = currentFile.read()
		currentFile.close()

		if not data:
			self.setResultsParams(results, self.readFileData, {"data":""})
		else:
			self.setResultsParams(results, self.readFileData, {"data":data})


	def eventEmit(self, params, results):
		assert SublimeSocketAPISettings.EVENTEMIT_TARGET in params, "eventEmit require 'target' param."
		assert SublimeSocketAPISettings.EVENTEMIT_EVENT in params, "eventEmit require 'eventemit' param."

		eventName = params[SublimeSocketAPISettings.EVENTEMIT_EVENT]
		assert eventName.startswith(SublimeSocketAPISettings.REACTIVE_PREFIX_USERDEFINED_EVENT), "eventEmit only emit 'user-defined' event such as starts with 'event_' keyword."

		self.fireReactor(SublimeSocketAPISettings.REACTORTYPE_EVENT, eventName, params, results)
		self.setResultsParams(results, 
			self.eventEmit, 
			{SublimeSocketAPISettings.EVENTEMIT_TARGET:params[SublimeSocketAPISettings.EVENTEMIT_TARGET], SublimeSocketAPISettings.EVENTEMIT_EVENT:params[SublimeSocketAPISettings.EVENTEMIT_EVENT]})


	def cancelCompletion(self, params, results):
		(view, path) = self.internal_getViewAndPathFromViewOrName(params, SublimeSocketAPISettings.CANCELCOMPLETION_VIEW, SublimeSocketAPISettings.CANCELCOMPLETION_NAME)
		if view:
			# hide completion
			self.editorAPI.runCommandOnView(view, "hide_auto_complete")

			self.setResultsParams(results, self.cancelCompletion, {"cancelled":path})

	
	def runCompletion(self, params, results):
		assert SublimeSocketAPISettings.RUNCOMPLETION_COMPLETIONS in params, "runCompletion require 'completion' param."
		
		(view, path) = self.internal_getViewAndPathFromViewOrName(params, SublimeSocketAPISettings.RUNCOMPLETION_VIEW, SublimeSocketAPISettings.RUNCOMPLETION_NAME)
		
		assert view, "runCompletion require 'view' or 'name' param." + params
		
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
		self.updateCompletion(path, completionStrs)

		# display completions
		self.editorAPI.runCommandOnView(view, "auto_complete")

		self.setResultsParams(results, self.runCompletion, {"completed":path})
			

	def setSublimeSocketWindowBasePath(self, results):
		self.sublimeSocketWindowBasePath = self.editorAPI.getFileName()
		self.setResultsParams(results, self.setSublimeSocketWindowBasePath, {"set":"ok"})
		
	## verify SublimeSocket API-version and SublimeSocket version
	def versionVerify(self, params, clientId, results):
		assert clientId, "versionVerify require 'client' object."
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
			self.sendVerifiedResultMessage(code, isDryRun, targetSocketVersion, SublimeSocketAPISettings.SOCKET_VERSION, targetVersion, currentVersion, clientId)

		elif targetMajor == currentMajor:
			if targetMinor < currentMinor:
				code = SublimeSocketAPISettings.VERIFICATION_CODE_VERIFIED_CLIENT_UPDATE
				self.sendVerifiedResultMessage(code, isDryRun, targetSocketVersion, SublimeSocketAPISettings.SOCKET_VERSION, targetVersion, currentVersion, clientId)

			elif targetMinor == currentMinor:
				code = SublimeSocketAPISettings.VERIFICATION_CODE_VERIFIED
				self.sendVerifiedResultMessage(code, isDryRun, targetSocketVersion, SublimeSocketAPISettings.SOCKET_VERSION, targetVersion, currentVersion, clientId)

			else:
				code = SublimeSocketAPISettings.VERIFICATION_CODE_REFUSED_SUBLIMESOCKET_UPDATE
				self.sendVerifiedResultMessage(code, isDryRun, targetSocketVersion, SublimeSocketAPISettings.SOCKET_VERSION, targetVersion, currentVersion, clientId)
				
		else:
			code = SublimeSocketAPISettings.VERIFICATION_CODE_REFUSED_SUBLIMESOCKET_UPDATE
			self.sendVerifiedResultMessage(code, isDryRun, targetSocketVersion, SublimeSocketAPISettings.SOCKET_VERSION, targetVersion, currentVersion, clientId)

		self.setResultsParams(results, self.versionVerify, {"result":code})

	## send result to client then exit or continue WebSocket connection.
	def sendVerifiedResultMessage(self, resultCode, isDryRun, targetSocketVersion, currentSocketVersion, targetAPIVersion, currentAPIVersion, clientId):
		# python-switch
		for case in PythonSwitch(resultCode):
			if case(SublimeSocketAPISettings.VERIFICATION_CODE_REFUSED_DIFFERENT_SUBLIMESOCKET):
				message = "REFUSED/DIFFERENT_SUBLIMESOCKET:	The current running SublimeSocket version = "+str(currentSocketVersion)+", please choose the other version of SublimeSocket. this client requires SublimeSocket "+str(targetSocketVersion)+", see https://github.com/sassembla/SublimeSocket"

				self.server.sendMessage(clientId, message)

				if not isDryRun:
					self.server.closeClient(clientId)
			
				break
			if case(SublimeSocketAPISettings.VERIFICATION_CODE_VERIFIED):
				message = "VERIFIED:	The current running SublimeSocket api version = "+currentAPIVersion+", SublimeSocket "+str(currentSocketVersion)
				self.server.sendMessage(clientId, message)
				break
			if case(SublimeSocketAPISettings.VERIFICATION_CODE_VERIFIED_CLIENT_UPDATE):
				message = "VERIFIED/CLIENT_UPDATE: The current running SublimeSocket api version = "+currentAPIVersion+", this client requires api version = "+str(targetAPIVersion)+", please update this client if possible."
				self.server.sendMessage(clientId, message)
				break

			if case(SublimeSocketAPISettings.VERIFICATION_CODE_REFUSED_SUBLIMESOCKET_UPDATE):
				message = "REFUSED/SUBLIMESOCKET_UPDATE:	The current running SublimeSocket api version = "+currentAPIVersion+", this is out of date. please update SublimeSocket. this client requires SublimeSocket "+str(targetAPIVersion)+", see https://github.com/sassembla/SublimeSocket"
				self.server.sendMessage(clientId, message)
				
				if not isDryRun:
					self.server.closeClient(clientId)

				break

			if case(SublimeSocketAPISettings.VERIFICATION_CODE_REFUSED_CLIENT_UPDATE):
				message = "REFUSED/CLIENT_UPDATE:	The current running SublimeSocket api version = "+currentAPIVersion+", this client requires api version = "+str(targetAPIVersion)+", required api version is too old. please update this client."
				self.server.sendMessage(clientId, message)
				
				if not isDryRun:
					self.server.closeClient(clientId)
					
				break

		self.editorAPI.printMessage("verify: " + message)

	def checkIfViewExist_appendRegion_Else_notFound(self, view, viewInstance, line, message, condition, results):
		# this check should be run in main thread
		return self.server.internal_appendRegion(viewInstance, line, message, condition)

	### region control


	## erase all regions of view/condition
	def eraseAllRegion(self, params, results):
		
		regionsDict = self.server.regionsDict()
		if regionsDict:
			deletes = {}
			deleteTargetPaths = []

			# if target view specified and it exist, should erase specified view's regions only.
			if SublimeSocketAPISettings.ERASEALLREGION_NAME in params:
				(view, path) = self.internal_getViewAndPathFromViewOrName(params, None, SublimeSocketAPISettings.ERASEALLREGION_NAME)
				
				if path in regionsDict:
					deleteTargetPaths.append(path)

				# if not found, do nothing.
				else:
					pass

			else:
				deleteTargetPaths = list(regionsDict)

		
			def eraseAllRegions(path):
				targetRegionsDict = regionsDict[path]
				
				deletedRegionIdentities = []
				for regionIdentity in targetRegionsDict:
					view = self.internal_detectViewInstance(path)
					self.editorAPI.removeRegionFromView(view, regionIdentity)

					deletedRegionIdentities.append(regionIdentity)
				

				if deletedRegionIdentities:
					deletes[path] = deletedRegionIdentities

			[eraseAllRegions(path) for path in deleteTargetPaths]
			
			for delPath in deletes:
				del regionsDict[delPath]

			self.server.updateRegionsDict(regionsDict)
			
			self.setResultsParams(results, self.eraseAllRegion, {"erasedIdentities":deletes})

	
	def formattingMessageParameters(self, params, formatKey, outputKey):
		currentFormat = params[formatKey]

		for key in params:
			if key != formatKey:
				currentParam = str(params[key])
				currentFormat = currentFormat.replace(key, currentParam)

		
		params[outputKey] = currentFormat
		del params[formatKey]

		return params

	def getKeywordBasedPath(self, path, keyword, replace):
		if path.startswith(keyword):
			filePathArray = path.split(keyword[-1])
			path = replace + filePathArray[1]

		return path

	# if inject parameter exist, inject it by the "injet" information.
	def injectParams(self, injectInfoDict, injectSourceDict):
		if SublimeSocketAPISettings.REACTOR_INJECT in injectInfoDict:
			
			injectDict = injectInfoDict[SublimeSocketAPISettings.REACTOR_INJECT].copy()
			
			# set the value of the name as vector.
			keys = list(injectDict)
			
			def replaceInject(key):
				assert key in injectSourceDict, "failed to inject parameter. parameter not found:"+key
				value = injectSourceDict[key]

				injectTargetKey = injectDict[key]
				
				injectDict[injectTargetKey] = value

			[replaceInject(key) for key in keys]			
			return injectDict

		return None


	# expand injected list.
	# if already injected, never overwrite.
	def insertInjectKeysToInjectionMap(self, params, injectionInterpolateKeys, injectKeyword):
		if injectKeyword in params:
			pass
		else:
			params[injectKeyword] = {}
			
		for key in injectionInterpolateKeys:
			if not key in params[injectKeyword]:
				# set key: key for generating injection map.
				params[injectKeyword][key] = key

		return params















	# view series

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

		if viewParamKey and viewParamKey in params:
			view = params[viewParamKey]
			
			path = self.internal_detectViewPath(view)
			
				
		elif nameParamKey and nameParamKey in params:
			name = params[nameParamKey]
			
			view = self.internal_detectViewInstance(name)
			path = self.internal_detectViewPath(view)


		if view and path:
			return (view, path)
		else:
			return (None, None)


	## get the target view-s information if params includes "filename.something" or some pathes represents filepath.
	def internal_detectViewInstance(self, name):
		viewDict = self.server.viewsDict()
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


	## collect current views
	def collectViews(self, results):
		collectedViews = []
		for views in [window.views() for window in self.editorAPI.windows()]:
			for view in views:
				viewParams = self.editorAPI.generateSublimeViewInfo(
					view,
					SublimeSocketAPISettings.VIEW_SELF,
					SublimeSocketAPISettings.VIEW_ID,
					SublimeSocketAPISettings.VIEW_BUFFERID,
					SublimeSocketAPISettings.VIEW_PATH,
					SublimeSocketAPISettings.VIEW_BASENAME,
					SublimeSocketAPISettings.VIEW_VNAME,
					SublimeSocketAPISettings.VIEW_SELECTEDS,
					SublimeSocketAPISettings.VIEW_ISEXIST
				)

				emitIdentity = str(uuid.uuid4())
				viewParams[SublimeSocketAPISettings.REACTOR_VIEWKEY_EMITIDENTITY] = emitIdentity


				self.fireReactor(
					SublimeSocketAPISettings.REACTORTYPE_VIEW,
					SublimeSocketAPISettings.SS_EVENT_COLLECT, 
					viewParams,
					results
				)

				collectedViews.append(viewParams[SublimeSocketAPISettings.VIEW_PATH])

		self.setResultsParams(results, self.collectViews, {"collected":collectedViews})
	

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
		viewDict = self.server.viewsDict()


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
		self.server.updateViewsDict(viewDict)

	def runDeletion(self, eventParam):
		view = eventParam[SublimeSocketAPISettings.VIEW_SELF]
		path = eventParam[SublimeSocketAPISettings.REACTOR_VIEWKEY_PATH]

		viewsDict = self.server.viewsDict()
		regionsDict = self.server.regionsDict()

		# delete
		if path in viewsDict:
			del viewsDict[path]
			self.server.updateViewsDict(viewsDict)

		if path in regionsDict:
			del regionsDict[path]
			self.server.updateReactorsDict(regionsDict)



	# reactor series

	## set reactor to KVS
	def setReactor(self, reactorType, params):
		assert SublimeSocketAPISettings.REACTOR_TARGET in params, "setXReactor require 'target' param."
		assert SublimeSocketAPISettings.REACTOR_REACT in params, "setXReactor require 'react' param."
		assert SublimeSocketAPISettings.REACTOR_SELECTORS in params, "setXReactor require 'selectors' param."

		reactorsDict = self.server.reactorsDict()
		reactorsLogDict = self.server.reactorsLogDict()

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


		self.server.updateReactorsDict(reactorsDict)
		self.server.updateReactorsLogDict(reactorsLogDict)
			

		return reactorsDict


	def removeAllReactors(self):
		reactorsDict = self.server.reactorsDict()
		deletedReactorsDict = reactorsDict.copy()

		self.server.updateReactorsDict({})
		self.server.updateReactorsLogDict({})
		
		return deletedReactorsDict


	def fireReactor(self, reactorType, eventName, eventParam, results):
		reactorsDict = self.server.reactorsDict()
		reactorsLogDict = self.server.reactorsLogDict()

		# run when the event occured adopt. start with specific "user-defined" event identity that defined as REACTIVE_PREFIX_USERDEFINED_EVENT.
		if eventName.startswith(SublimeSocketAPISettings.REACTIVE_PREFIX_USERDEFINED_EVENT):
			# if exist, continue
			if reactorsDict and eventName in reactorsDict:
				
				target = eventParam[SublimeSocketAPISettings.REACTOR_TARGET]
				if target in reactorsDict[eventName]:
					params = reactorsDict[eventName][target]

					delay = reactorsDict[eventName][target][SublimeSocketAPISettings.REACTOR_DELAY]

					if not self.isExecutableWithDelay(eventName, target, delay):
						pass
					else:
						# inject all keys and values.
						keys = []
						values = []

						for key, val in eventParam.items():
							keys.append(key)
							values.append(val)

						self.runAllSelector(
							params, 
							keys, 
							values, 
							SublimeSocketAPISettings.REACTOR_INJECT, 
							results)

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
					
					delay = reactorsDict[eventName][reactorKey][SublimeSocketAPISettings.REACTOR_DELAY]
					if not self.isExecutableWithDelay(eventName, reactorKey, delay):
						pass

					else:
						reactorParams = reactorDict[reactorKey]
						self.runReactor(reactorType, reactorParams, eventParam, results)


	# completion series

	## return completion then delete.
	def consumeCompletion(self, viewIdentity, eventName):
		completions = self.server.completionsDict()
		if completions:
			if viewIdentity in list(completions):
				completion = completions[viewIdentity]
				
				self.server.deleteCompletion(viewIdentity)
				return completion

		return None

	def updateCompletion(self, viewIdentity, composedCompletions):
		completionsDict = self.server.completionsDict()

		completionsDict[viewIdentity] = composedCompletions
		self.server.updateCompletionsDict(completionsDict)
		

	# other

	def isExecutableWithDelay(self, name, target, elapsedWaitDelay):
		currentTime = round(int(time.time()*1000))
		reactorsLogDict = self.server.reactorsLogDict()

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
		self.server.updateReactorsLogDict(reactorsLogDict)
		
		return True

class TransformerStream:
	def __init__(self, buf):
		self.buf = buf

	def write(self, text):
		self.buf.append(text)
		pass
