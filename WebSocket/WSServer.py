# -*- coding: utf-8 -*-

import threading
import os
import socket
import string

import uuid


from .WSClient import WSClient
from .WSEncoder import WSEncoder

from ..PythonSwitch import PythonSwitch
from .. import SublimeSocketAPISettings


class WSServer:
	def __init__(self, server):
		self.methodName = SublimeSocketAPISettings.WEBSOCKET_SERVER
		self.clients = {}
		
		self.args = None

		
		self.socket = ''
		self.host = ''
		self.port = ''

		self.listening = False
		
		self.encoder = WSEncoder()

		self.sublimeSocketServer = server

	def info(self):
		return 'SublimeSocket WebSocketServing running @ ' + str(self.host) + ':' + str(self.port)

	def currentArgs(self):
		return (self.methodName, self.args)


	def setup(self, params):
		assert "host" in params and "port" in params, "WebSocketServer require 'host' and 'port' param."
		
		# set for restart.
		self.args = params

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
			self.sublimeSocketServer.transferSpinupFailed(reason)
			return

		self.socket.listen(1)
		self.sublimeSocketServer.transferSpinupped('SublimeSocket WebSocketServing started @ ' + str(self.host) + ':' + str(self.port))


		self.listening = True
		while self.listening:
			try:
				# when teardown, causes close then "Software caused connection abort"
				(conn, addr) = self.socket.accept()

				identity = str(uuid.uuid4())

				# genereate new client
				client = WSClient(self, identity)
				
				self.clients[identity] = client

				threading.Thread(target = client.handle, args = (conn,addr)).start()
			except socket.error as msg:
				print("WebSocketServer closed.", msg)
			
		msg = 'SublimeSocket WebSocketServing closed @ ' + str(self.host) + ':' + str(self.port)
		self.sublimeSocketServer.transferTeardowned(msg)		

	## teardown the server
	def teardown(self):
		# close all WebSocket clients
		clientsList = self.clients.copy()
		
		for clientId in clientsList:
			client = self.clients[clientId]
			client.close()

		self.clients = []

		# stop receiving
		self.listening = False

		# force close. may cause "[Errno 53] Software caused connection abort".
		self.socket.close()



	## update specific client's id
	def updateClientId(self, clientId, newIdentity):
		client = self.clients[clientId]

		# del from list
		del self.clients[clientId]

		# update
		client.clientId = newIdentity
		self.clients[newIdentity] = client


	def thisClientIsDead(self, clientId):
		self.closeClient(clientId)
		

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


	def call(self, data, clientId):
		self.sublimeSocketServer.transferInputted(data, clientId)


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

		
