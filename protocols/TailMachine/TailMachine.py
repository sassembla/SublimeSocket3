import os
import subprocess
import queue

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
		self.reactors = params["reactors"]


	def spinup(self):
		if os.path.exists(self.path):
			command = ['tail', '-f', self.path]
			process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			
			stdout_queue = queue.Queue()
			stdout_reader = AsynchronousFileReader(process.stdout, stdout_queue)
			stdout_reader.start()

			stderr_queue = queue.Queue()
			stderr_reader = AsynchronousFileReader(process.stderr, stderr_queue)
			stderr_reader.start()

			# ここをどうノンブロッキングで書くか。あとどうやってkillするか。
			# 寿命としては、新たなサーバ機能の一つなので、inしてくるラインか。ということは、server側に実装をもつべき。

			print("tailMachineの起動、ファイルパスチェックとかを行って開始。必要であればジェネレートする＞いいや。")
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
	def call(self, data, clientId):
		print("call with data", data, "to", clientId)


	def sendMessage(self, targetId, message):
		if message:
			pass
		else:
			return (False, "no data to:"+targetId)
		
		print("call with data", data, "to", clientId)


	def broadcastMessage(self, targetIds, message):
		print("broadcastMessage do nothing.")




class AsynchronousFileReader(threading.Thread):
    def __init__(self, fd, queue):
        assert callable(fd.readline)
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = queue
 
    def run(self):
        '''The body of the tread: read lines and put them on the queue.'''
        for line in iter(self._fd.readline, ''):
            self._queue.put(line)
 
    def eof(self):
        '''Check whether there is no more content to expect.'''
        return not self.is_alive() and self._queue.empty()






