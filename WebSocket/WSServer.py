# -*- coding: utf-8 -*-

import threading
import os
import socket
import string

import uuid


from .WSClient import WSClient
from .WSEncoder import WSEncoder

from ..PythonSwitch import PythonSwitch


class WSServer:
	def __init__(self, server):
		self.clients = {}
		
		self.socket = ''
		self.host = ''
		self.port = ''

		self.listening = False
		
		self.encoder = WSEncoder()

		self.sublimeSocketServer = server
		

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


		# spinupと、teardownがある。 beforeとafterでハンドラつけるか。
		self.sublimeSocketServer.spinupped('SublimeSocket WebSocketServing started @ ' + str(host) + ':' + str(port))


		self.listening = True
		while self.listening:
			(conn, addr) = self.socket.accept()

			if self.listening is None:
				return 0
			
			identity = str(uuid.uuid4())

			# genereate new client
			client = WSClient(self, identity)
			
			self.clients[identity] = client

			threading.Thread(target = client.handle, args = (conn,addr)).start()
				
		return 0
		

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
	

	## update specific client's id
	def updateClientId(self, clientId, newIdentity):
		client = self.clients[clientId]

		# del from list
		del self.clients[clientId]

		# update
		client.clientId = newIdentity
		self.clients[newIdentity] = client



	# remove from Client dict
	def closeClient(self, clientId):
		client = self.clients[clientId]
		client.close()

		if clientId in self.clients:
			del self.clients[clientId]
		else:
			print("ss: server don't know about client:", clientId)
	

	## show current status & connectionIds
	def showCurrentStatusAndConnections(self):
		print("ss: server host:", self.host, "	port:", self.port)
		
		print("ss: connections:")
		for client in self.clients:
			print("	", client)


	def callSublimeServer(self, data, clientId):
		self.sublimeSocketServer.callSublimeServer(data, clientId)


	def sendMessage(self, targetId, message):
		if targetId in self.clients:
			client = self.clients[targetId]
			buf = self.encoder.text(str(message), mask=0)
			client.send(buf)
			return True
		
		return False


	def broadcastMessage(self, message):
		buf = self.encoder.text(str(message), mask=0)
		
		clients = self.clients.values()

		clientNames = list(self.clients.keys())
		
		for client in clients:
			client.send(buf)

		return clientNames

		
