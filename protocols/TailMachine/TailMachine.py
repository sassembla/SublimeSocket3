import os
import subprocess
import queue
import time
import uuid
import json

import threading

from ...PythonSwitch import PythonSwitch
from ... import SublimeSocketAPISettings

TAIL_PATH = "tailPath"
TAIL_REACTORS = "reactors"
TAIL_REACTORS_SOURCE = "reactorsSource"

class TailMachine:
	def __init__(self, server, serverIdentity):
		self.methodName = SublimeSocketAPISettings.TAIL_MACHINE
		
		self.args = None
		self.transferIdentity = serverIdentity

		self.path = "not set yet."
		self.continuation = False

		self.params = {}


		self.sublimeSocketServer = server

	def info(self):
		message = "TailMachine tailing:" + self.path
		return message
		

	def currentArgs(self):
		return (self.methodName, self.args)


	def setup(self, params):
		assert TAIL_PATH in params, "TailMachine require 'tailPath' param."
		assert TAIL_REACTORS in params or TAIL_REACTORS_SOURCE in params, "TailMachine require 'reactors' or 'reactorsSource' param."
		
		if TAIL_REACTORS_SOURCE in params:
			assert False, "reactorsSource not yet supported."
			data
			reactorsData = json.loads(data)

		else:
			reactors = params[TAIL_REACTORS]
			reactorsData = json.loads(reactors)

		if "continuation" in params:
			self.continuation = params["continuation"]

		# set for restart.
		self.args = params
		self.path = params[TAIL_PATH]
		

		assert SublimeSocketAPISettings.RUNSELECTORSWITHINJECTS_SELECTORS in reactorsData, "TailMachine require 'selector' in reactor definition."
		self.selectors = reactorsData[SublimeSocketAPISettings.RUNSELECTORSWITHINJECTS_SELECTORS]


	def spinup(self):
		if os.path.exists(self.path):
			command = ['tail', '-f', self.path]
			
			self.generateTailThread(command)

			self.sublimeSocketServer.transferSpinupped('TailMachine spinupped:' + self.path)

		else:
			assert False, "TailMachine spinup failed:path not found:" + self.path

	## teardown the server
	def teardown(self):
		self.sublimeSocketServer.transferSpinupped('TailMachine teardowned')


	## update specific client's id
	def updateClientId(self, clientId, newIdentity):
		pass

	def thisClientIsDead(self, clientId):
		pass
		

	def purgeConnection(self, clientId):
		print("purgeConnection do nothing.")
		

	# remove from Client dict
	def closeClient(self, clientId):
		pass



	# call SublimeSocket server. transfering datas.
	def call(self, source):
		lineSource = source.decode("utf-8")

		# combine
		data = {"selectors":self.selectors, "injects":{"source":lineSource}}
		self.sublimeSocketServer.transferRunAPI(SublimeSocketAPISettings.API_RUNSELECTORSWITHINJECTS, data)


	def sendMessage(self, targetId, message):
		pass

	def broadcastMessage(self, targetIds, message):
		pass

	def generateTailThread(self, command):
		process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		# observe target.
		logQueue = queue.Queue()

		AsynchronousFileReader(process.stdout, logQueue).start()
		
		self.handler = Handler()
		threading.Thread(target = self.handler.handle, args = (self.call, logQueue)).start()


class Handler:
	def handle(self, call, queue):
		while 1:
			if queue.empty():
				pass
			else:
				m = queue.get()
				call(m)
			
			time.sleep(0.1)


class AsynchronousFileReader(threading.Thread):
	def __init__(self, fd, queue):
		assert callable(fd.readline)

		self._fd = fd
		self._queue = queue

		threading.Thread.__init__(self)

	def run(self):	
		for line in iter(self._fd.readline, ''):
			self._queue.put(line)





