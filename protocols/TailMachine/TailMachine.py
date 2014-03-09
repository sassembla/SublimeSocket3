import os
import subprocess
import queue
import time
import uuid

import threading

from ...PythonSwitch import PythonSwitch
from ... import SublimeSocketAPISettings


class TailMachine:
	def __init__(self, server, serverIdentity):
		self.methodName = SublimeSocketAPISettings.TAIL_MACHINE
		
		self.args = None
		self.transferIdentity = serverIdentity

		self.path = "not set yet."

		self.sublimeSocketServer = server

	def info(self):
		message = "TailMachine tailing:" + self.path
		return message
		

	def currentArgs(self):
		return (self.methodName, self.args)


	def setup(self, params):
		assert "path" in params, "TailMachine require 'path' param."
		assert "reactors" in params, "TailMachine require 'reactors' param."
		
		# set for restart.
		self.args = params

		self.path = params["path"]

		print("ここでreactorsをSushiへと分解する", params["reactors"])
		self.reactors = params["reactors"]


	def spinup(self):
		if os.path.exists(self.path):
			command = ['tail', '-f', self.path]
			
			self.generateTailThread(command)

			self.sublimeSocketServer.transferSpinupped('TailMachine spinupped:' + self.path)

		else:
			print("failed!!:" + self.path)

	## teardown the server
	def teardown(self):
		self.sublimeSocketServer.transferSpinupped('TailMachine teardowned')


	## update specific client's id
	def updateClientId(self, clientId, newIdentity):
		print("updateClientId do nothing.")

	def thisClientIsDead(self, clientId):
		print("thisClientIsDead do nothing.")
		

	def purgeConnection(self, clientId):
		print("purgeConnection do nothing.")
		

	# remove from Client dict
	def closeClient(self, clientId):
		print("closeClient do nothing.", clientId)



	# call SublimeSocket server. transfering datas.
	def call(self, data):

		print("ここで、reactorの値にsourceを適応したSushiJSONを返す。reactorを分解しておく必要がある。", data)

		# self.sublimeSocketServer.transferInputted(data)


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
				print("m", m)
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





