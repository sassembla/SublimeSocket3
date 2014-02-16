import json
import re

SUSHIJSON_CONCAT_DELIM				= "->"	# concat commands. every commands run in sequential.
SUSHIJSON_COMMAND_PARAMS_DELIM		= ":"	# only first ":" will be evaluated as delimiter / each commnand.
SUSHIJSON_COMMAND_KEYWORD_INJECT	= "<-"
SUSHIJSON_COMMAND_KEYWORD_DELIM		= ","

SUSHIJSON_COMMENT_DELIM				= "/"	# comment expression in API. COMMENT/API...

SUSHIJSON_TEST_BEFOREAFTER_DELIM	= "beforeafter>" #delimiter of the slectors of "befrore" and "after"
SUSHIJSON_TESTCASE_DELIM			= "test>"	# test commands delim.
SUSHIJSON_API_SETTESTBEFOREAFTER	= "setTestBeforeAfter"
SETTESTBEFOREAFTER_BEFORESELECTORS	= "beforeselectors"
SETTESTBEFOREAFTER_AFTERSELECTORS	= "afterselectors"

SUSHIJSON_KEYWORD_SELECTORS			= "selectors"
SUSHIJSON_KEYWORD_INJECTS			= "injects"


class SushiJSONParser():

	@classmethod 
	def parseStraight(self, data):
		# remove //comment line
		removeCommented = re.sub(r'//.*', r'', data)
		
		# remove spaces
		removeSpaces = re.sub(r'(?m)^\s+', '', removeCommented)
		
		parsedCommandsAndParams = []

		# e.g. inputIdentity:{"id":"537d5da6-ce7d-42f0-387b-d9c606465dbb"}->showAlert...|>...
		commands = removeSpaces.split(SUSHIJSON_CONCAT_DELIM)		

		# command and param  SAMPLE:		inputIdentity:{"id":"537d5da6-ce7d-42f0-387b-d9c606465dbb"}
		for commandIdentityAndParams in commands :
			command_params = commandIdentityAndParams.split(SUSHIJSON_COMMAND_PARAMS_DELIM, 1)
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
					print("SushiJSON parse error ", e, "source", command_params[1])
					return None
			
			parsedCommandsAndParams.append((command, params))
			
		return parsedCommandsAndParams
		
	
	@classmethod
	def parseTestSuite(self, data):
		# remove comment line then remove \n from data, before parse. this sequence is need for generate testcases.
		data = re.sub(r'//.*', r'', data)
		data = data.replace("\n", "")
		
		splitted = data.split(SUSHIJSON_TESTCASE_DELIM)
		
		beforeAfterBase = splitted[0]

		command, params = self.parseStraight(beforeAfterBase)[0]
		assert SUSHIJSON_TEST_BEFOREAFTER_DELIM in command, "SushiJSONTests must start with " + SUSHIJSON_TEST_BEFOREAFTER_DELIM + " statement."

		# extract selectors.
		beforeSelectors = params[SETTESTBEFOREAFTER_BEFORESELECTORS]
		afterSelectors = params[SETTESTBEFOREAFTER_AFTERSELECTORS]

		testCases = splitted[1:]

		def addBeforeAndAfter(testCase):
			parsedCommandsAndParams = self.parseStraight(testCase)

			parsedCommandsAndParams.insert(0, (SETTESTBEFOREAFTER_BEFORESELECTORS, beforeSelectors))
			parsedCommandsAndParams.append((SETTESTBEFOREAFTER_AFTERSELECTORS, afterSelectors))
			
			return parsedCommandsAndParams
			
		return [addBeforeAndAfter(testCase) for testCase in testCases]


	@classmethod
	def composeParams(self, command, params, injects):
		
		# erase comment
		if SUSHIJSON_COMMENT_DELIM in command:
			splitted = command.split(SUSHIJSON_COMMENT_DELIM, 1)
			command = splitted[1]

		# remove spaces " "
		command = command.replace(" ", "")

		# calc "<-" inject param.
		if SUSHIJSON_COMMAND_KEYWORD_INJECT in command:
			commandBase = command

			splitted = command.split(SUSHIJSON_COMMAND_KEYWORD_INJECT, 1)
			command = splitted[0]

			if injects:
				accepts = splitted[1].split(SUSHIJSON_COMMAND_KEYWORD_DELIM)
			
				# empty "<-" means all injective will be inject.
				if len(accepts) == 1 and accepts[0] == "":
					accepts = list(injects)
				
				for acceptKey in accepts:
					assert acceptKey in injects, "failed to inject non-injected param:" + acceptKey + " in:" + str(injects) + " at:" + commandBase
					params[acceptKey] = injects[acceptKey]
			
		return command, params


	@classmethod
	# if inject parameter exist, inject it by the "inject" key information.
	def injectParams(self, sourceParams, APIDefinedInjectiveKeysAndValues):
		APIDefinedInjectiveKeys = APIDefinedInjectiveKeysAndValues.keys()

		# do nothing if user-setting injects exist.
		if SUSHIJSON_KEYWORD_INJECTS in sourceParams:
			pass
		else:
			sourceParams[SUSHIJSON_KEYWORD_INJECTS] = {}

		# there are 3 kind of parameter-type that should be retrieve.
		# check "sourceParams" and "sourceParams:{injects:{REVEALED-INJECTIVE-DICT}}" especially REVEALED-INJECTIVE-DICT's key.

		# key is...
		
		# 1.APIDefined-key, and not included "injects" param.	=> inject automatically.
		# 2.APIDefined-key, but revealed in "injects" 			=> inject key-value to value:source[key].
		# 3.not APIDefined-key									=> inject key-value to value:source[key].

		injectDict = sourceParams[SUSHIJSON_KEYWORD_INJECTS]

		resultInjectDict = {}
		for currentInjectsKey in injectDict.keys():

			# type 2
			if currentInjectsKey in APIDefinedInjectiveKeys:
				
				injectionTargetKey = injectDict[currentInjectsKey]
				
				if currentInjectsKey in sourceParams:
					resultInjectDict[injectionTargetKey] = sourceParams[currentInjectsKey]

				else:
					resultInjectDict[injectionTargetKey] = APIDefinedInjectiveKeysAndValues[currentInjectsKey]

			# type 3
			else:
				assert currentInjectsKey in sourceParams, "failed to inject:" + currentInjectsKey + " from:" + str(sourceParams)
				injectionTargetKey = injectDict[currentInjectsKey]
				
				resultInjectDict[injectionTargetKey] = sourceParams[currentInjectsKey]

		# else. type 1
		nonInjectedKeys = set(APIDefinedInjectiveKeys) - set(resultInjectDict.keys())
		for key in nonInjectedKeys:
			resultInjectDict[key] = APIDefinedInjectiveKeysAndValues[key]

		return resultInjectDict


