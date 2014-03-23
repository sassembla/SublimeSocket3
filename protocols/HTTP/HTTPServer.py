# -*- coding: utf-8 -*-

# import os
# import socket
# import string
# import threading
# import uuid

# from .WSClient import WSClient
# from .WSEncoder import WSEncoder
# import http.server.HTTPServer
import http.server
import socketserver
# from SimpleHTTPServer import SimpleHTTPRequestHandler


from ...PythonSwitch import PythonSwitch
from ... import SublimeSocketAPISettings

class HTTPServer:
	def __init__(self, server, transferId):
		self.methodName = SublimeSocketAPISettings.HTTP_SERVER
		self.transferId = transferId
		
		self.args = None
		
		self.host = ''
		self.port = ''
		
		self.sublimeSocketServer = server




	def info(self):
		pass
		# message = "SublimeSocket WebSocketServing running @ " + str(self.host) + ':' + str(self.port)
		
		# for clientId in self.clientIds:
		# 	message = message + "\n	client:" + clientId
		# return message
		

	def currentArgs(self):
		return (self.methodName, self.args)


	def setup(self, params):
		assert "host" in params and "port" in params, "WebSocketServer require 'host' and 'port' param."
		
		# set for restart.
		self.args = params

		self.host = params["host"]
		self.port = params["port"]


	def spinup(self):
		Handler = http.server.SimpleHTTPRequestHandler

		httpd = socketserver.TCPServer((self.host, self.port), Handler)

		self.sublimeSocketServer.transferSpinupped('SublimeSocket HTTPServing started @ ' + str(self.host) + ':' + str(self.port))
		
		httpd.serve_forever()

		message = "SublimeSocket HTTPServing closed @ " + str(self.host) + ":" + str(self.port)
		self.sublimeSocketServer.transferTeardowned(self.transferId, message)

	## teardown the server
	def teardown(self):
		pass
		# # close all WebSocket clients
		# clientsList = self.clientIds.copy()
		
		# for clientId in clientsList:
		# 	client = self.clientIds[clientId]
		# 	client.close()

		# self.clientIds = {}

		# # stop receiving
		# self.listening = False

		# # force close. may cause "[Errno 53] Software caused connection abort".
		# self.socket.close()


	## return current connection Ids.
	def connectionIdentities(self):
		pass
		# return self.clientIds

	## update specific client's id
	def updateClientId(self, clientId, newIdentity):
		pass
		# client = self.clientIds[clientId]

		# # del from list
		# del self.clientIds[clientId]

		# # update
		# client.clientId = newIdentity
		# self.clientIds[newIdentity] = client


	def thisClientIsDead(self, clientId):
		self.closeClient(clientId)
		

	def purgeConnection(self, clientId):
		self.closeClient(clientId)
		

	# remove from Client dict
	def closeClient(self, clientId):
		pass
		# client = self.clientIds[clientId]
		# client.close()

		# if clientId in self.clientIds:
		# 	del self.clientIds[clientId]
	

	# call SublimeSocket server. transfering datas.
	def call(self, data, clientId):
		self.sublimeSocketServer.transferInputted(data, self.transferId, clientId)


	def sendMessage(self, targetId, message):
		pass
		# if message:
		# 	pass
		# else:
		# 	return (False, "no data to:"+targetId)
			
		# if targetId in self.clientIds:
		# 	client = self.clientIds[targetId]
		# 	buf = self.encoder.text(str(message), mask=0)
		# 	client.send(buf)
		# 	return (True, "done")
			
		# return (False, "no target found in:" + str(self.clientIds))


	def broadcastMessage(self, message):
		pass
		# buf = self.encoder.text(str(message), mask=0)
		
		# clients = self.clientIds.values()
		# targets = []

		# # broadcast
		# for client in clients:
		# 	client.send(buf)

		# 	targets.append(client.clientId)

		# return targets



