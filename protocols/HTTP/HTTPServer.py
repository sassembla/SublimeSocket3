# -*- coding: utf-8 -*-

import http.server
import socketserver

from ...PythonSwitch import PythonSwitch
from ... import SublimeSocketAPISettings


# this is prototype of http server. not yet implmented 1.1 & 2 of HTTP.
class HTTPServer:
	def __init__(self, server, transferId):
		self.methodName = SublimeSocketAPISettings.PROTOCOL_HTTP_SERVER
		self.transferId = transferId
		
		self.args = None
		
		self.host = ''
		self.port = ''
		
		self.sublimeSocketServer = server
		self.httpd = None


	def info(self):
		message = "SublimeSocket HTTPServing running @ " + str(self.host) + ':' + str(self.port)
		return message
		

	def currentArgs(self):
		return (self.methodName, self.args)


	def setup(self, params):
		assert "host" in params and "port" in params, "WebSocketServer require 'host' and 'port' param."
		
		# set for restart.
		self.args = params

		self.host = params["host"]
		self.port = params["port"]

		self.listening = False

	def spinup(self):
		self.listening = True
		Handler = http.server.SimpleHTTPRequestHandler

		self.httpd = socketserver.TCPServer((self.host, self.port), Handler)
		
		self.sublimeSocketServer.transferSpinupped('SublimeSocket HTTPServing started @ ' + str(self.host) + ':' + str(self.port))
		
		# while self.listening:
		# 	self.httpd.handle_request()
		self.httpd.serve_forever()

		message = "SublimeSocket HTTPServing closed @ " + str(self.host) + ":" + str(self.port)
		self.sublimeSocketServer.transferTeardowned(self.transferId, message)

	## teardown the server
	def teardown(self):
		self.listening = False
		if self.httpd:
			self.httpd.shutdown()
		

	## return current connection Ids.
	def connectionIdentities(self):
		return []

	## update specific client's id
	def updateClientId(self, clientId, newIdentity):
		pass

	def thisClientIsDead(self, clientId):
		pass
		

	def purgeConnection(self, clientId):
		pass
		

	# remove from Client dict
	def closeClient(self, clientId):
		pass
		

	# call SublimeSocket server. transfering datas.
	def call(self, data, clientId):
		self.sublimeSocketServer.transferInputted(data, self.transferId, clientId)


	def sendMessage(self, targetId, message):
		# HTTP2, serverPush
		pass
		

	def broadcastMessage(self, message):
		# HTTP2, serverPush
		pass




