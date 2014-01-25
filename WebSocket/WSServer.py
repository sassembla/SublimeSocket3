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
		
	def setup(self, params):
		assert "host" in params and "port" in params, "WebSocketServer require 'host' and 'port' param."
		self.host = params["host"]
		self.port = params["port"]


	def spinup(self):
		assert self.host and self.port, "WebSocketServer require set 'host' and 'port' param."
		self.socket = socket.socket()

		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		try:
			self.socket.bind((self.host, self.port))
		except socket.error as msg:
			reason = 'SublimeSocket WebSocketServing faild to spinup @ ' + str(self.host) + ':' + str(self.port) + " by " + str(msg)
			self.sublimeSocketServer.spinupFailed(reason)
			return

		self.socket.listen(1)
		self.sublimeSocketServer.spinupped('SublimeSocket WebSocketServing started @ ' + str(self.host) + ':' + str(self.port))


		self.listening = True
		while self.listening:
			(conn, addr) = self.socket.accept()

			print("わかんない、必要かなこれ。")
			# if self.listening is None:
			# 	return 0
			
			identity = str(uuid.uuid4())

			# genereate new client
			client = WSClient(self, identity)
			
			self.clients[identity] = client

			threading.Thread(target = client.handle, args = (conn,addr)).start()
			
		msg = 'SublimeSocket WebSocketServing closed @ ' + str(self.host) + ':' + str(self.port)
		self.sublimeSocketServer.teardowned(msg)		

	## tearDown the server
	def tearDown(self):
		# close all WebSocket clients
		for clientId in self.clients:
			client = self.clients[clientId]
			client.close()

		self.clients = []

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
			print("ss: server doesn't know about this client:", clientId)
	

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

		
