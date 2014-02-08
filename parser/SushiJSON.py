import json
import re

SUSHIJSON_CONCAT_DELIM				= "->"	# concat commands. every commands run in sequential.
SUSHIJSON_COMMAND_PARAMS_DELIM		= ":"	# only first ":" will be evaluated as delimiter / each commnand.
SUSHIJSON_COMMAND_KEYWORD_INJECT	= "<-"
SUSHIJSON_COMMAND_KEYWORD_DELIM		= ","

SUSHIJSON_COMMENT_DELIM				= "/"	# comment expression in API. ss@COMMENT/API...

SUSHIJSON_TEST_BEFOREAFTER_DELIM	= "beforeafter>" #delimiter of the slectors of "befrore" and "after"
SUSHIJSON_TESTCASE_DELIM			= "test>"	# test commands delim.
SUSHIJSON_API_SETTESTBEFOREAFTER	= "setTestBeforeAfter"
SETTESTBEFOREAFTER_BEFORESELECTORS	= "beforeselectors"
SETTESTBEFOREAFTER_AFTERSELECTORS	= "afterselectors"


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
	# こいつもネットワーク経由だったからバグが出なかったんだなー。ネットワーク経由で入力するにはあっちでファイル読まないと行けなくてダメだな。
	def parseTestSuite(self, data):
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
	def inject(self, command, params, injects):
		
		# erase comment
		if SUSHIJSON_COMMENT_DELIM in command:
			splitted = command.split(SUSHIJSON_COMMENT_DELIM, 1)
			command = splitted[1]

		# remove spaces " "
		command = command.replace(" ", "")

		# calc "<-" inject param.
		if injects and SUSHIJSON_COMMAND_KEYWORD_INJECT in command:
			
			splitted = command.split(SUSHIJSON_COMMAND_KEYWORD_INJECT, 1)
			command = splitted[0]
			
			accepts = splitted[1].split(SUSHIJSON_COMMAND_KEYWORD_DELIM)
			
			# empty "<-" means all injective will be inject.
			if len(accepts) == 1 and accepts[0] == "":
				accepts = list(injects)
			
			for acceptKey in accepts:
				assert acceptKey in injects, "cannot inject not injected param:" + acceptKey + " in " + commandbase
				params[acceptKey] = injects[acceptKey]

		return command, params
