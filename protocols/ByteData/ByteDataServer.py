# -*- coding: utf-8 -*-


from ...PythonSwitch import PythonSwitch
from ... import SublimeSocketAPISettings

class ByteDataServer:
	def __init__(self, server, transferId):
		self.methodName = SublimeSocketAPISettings.PROTOCOL_BYTEDATA_SERVER
		self.transferId = transferId
		
		self.args = None
		self.reactors = []
		self.sublimeSocketServer = server


	def info(self):
		message = "SublimeSocket ByteDataServer running"
		# 返すとしたら、rev一覧
		return message


	def currentArgs(self):
		return (self.methodName, self.args)


	def setup(self, params):
		assert "reactors" in params, "ByteDataServer require 'reactors' param."

		# set for restart.
		self.args = params

		self.reactors = params["reactors"]


	def spinup(self):
		print("消えなければ良いので、ただのデータを返すハンドラ扱いでいいはず。変化させたければ、どっかのファイルを指すとか？Aに対して文字列Bを返す、で良いと思う。")

	## teardown the server
	def teardown(self):
		print("teardown　消えるだけ")
		

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



