# -*- coding: utf-8 -*-

import socket
import threading

from ...PythonSwitch import PythonSwitch
from ... import SublimeSocketAPISettings

BUF_SIZE = 1024

class ByteDataServer:
	def __init__(self, server, transferId):
		self.methodName = SublimeSocketAPISettings.PROTOCOL_BYTEDATA_SERVER
		self.transferId = transferId
		
		self.args = None

		self.socket = ''
		self.binders = []
		
		self.host = ''
		self.port = ''

		self.sublimeSocketServer = server


	def info(self):
		message = "SublimeSocket ByteDataServer running @ " + str(self.host) + ':' + str(self.port)
		return message


	def currentArgs(self):
		return (self.methodName, self.args)


	def setup(self, params):
		assert "binders" in params, "ByteDataServer require 'binders' param."
		assert "host" in params and "port" in params, "ByteDataServer require set 'host' and 'port' param."

		# set for restart.
		self.args = params

		self.binders = params["binders"]
		self.host = params["host"]
		self.port = params["port"]


	def spinup(self):
		assert self.host and self.port, "ByteDataServer require set 'host' and 'port' param."
		self.socket = socket.socket()

		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		try:
			self.socket.bind((self.host, self.port))
		except socket.error as msg:
			reason = 'SublimeSocket ByteDataServer faild to spinup @ ' + str(self.host) + ':' + str(self.port) + " by " + str(msg)
			self.sublimeSocketServer.transferSpinupFailed(reason)
			return

		self.socket.listen(1)
		self.sublimeSocketServer.transferSpinupped('SublimeSocket ByteDataServer started @ ' + str(self.host) + ':' + str(self.port))


		self.listening = True
		while self.listening:
			try:
				(conn, addr) = self.socket.accept()
				threading.Thread(target = self.handle, args = (conn, addr)).start()
			
			except socket.error as msg:
				errorMsg = "SublimeSocket ByteDataServer crashed @ " + str(self.host) + ":" + str(self.port) + " reason:" + str(msg)
				self.sublimeSocketServer.transferNoticed(errorMsg)
			
		message = "SublimeSocket ByteDataServer closed @ " + str(self.host) + ":" + str(self.port)
		self.sublimeSocketServer.transferTeardowned(self.transferId, message)


	def handle(self, conn, addr):
		line = bytearray()
		
		while len(line) < BUF_SIZE:
			c = self.receive(conn, 1)
			
			if c == b'\x00':
				break
			else:
				line = line + c

		decoded = str(line.decode('utf-8'))
		
		# check match or not
		for targetPatternDict in self.binders:
			for key in list(targetPatternDict):
				if decoded == key:
					buf = bytes(targetPatternDict[key], 'utf-8')
					lock = threading.Lock()
					lock.acquire()
					conn.send(buf)
					lock.release()
					conn.close()
					
				else:
					conn.close()
					
					
	def receive(self, conn, bufsize):
		try:
			bytes = conn.recv(bufsize)
		except:
			bytes = None

		if bytes:
			return bytes

		# recv error.
		return None


	## teardown the server
	def teardown(self):
		# stop receiving
		self.listening = False

		# force close. may cause "[Errno 53] Software caused connection abort".
		self.socket.close()
		

	## return current connection Ids.
	def connectionIdentities(self):
		# return empty.
		return []


	## update specific client's id
	def updateClientId(self, clientId, newIdentity):
		pass

	def thisClientIsDead(self, clientId):
		pass
		
	def purgeConnection(self, clientId):
		pass
		
	def closeClient(self, clientId):
		pass

	# call SublimeSocket server. transfering datas.
	def call(self, data, clientId):
		self.sublimeSocketServer.transferInputted(data, self.transferId, clientId)

	def sendMessage(self, targetId, message):
		pass

	def broadcastMessage(self, message):
		pass



