## key-value pool
import copy

class KVS:
	def __init__(self):
		self.keyValueDict = {}

	## empty or not
	def isEmpty(self):
		if 0 == len(self.keyValueDict):
			return True
		else:
			return False

	## set (override if exist already)
	def setKeyValue(self, key, value):
		if key in self.keyValueDict:
			# print "overwritten:", key, "as:", value
			pass

		self.keyValueDict[key] = value

	def update(self, index, key, value):
		if index in self.keyValueDict:
			self.keyValueDict[index][key] = value
				

	## get value for key
	def get(self, key):
		if key in self.keyValueDict:
			return readonlyDict(self.keyValueDict[key])


	def getAll(self):
		return self.keyValueDict


	## get all key-value
	def items(self):
		return self.keyValueDict.items()


	## remove key-value
	def remove(self, key):
		if self.get(key):
			del self.keyValueDict[key]
			return True
		else:
			print("no '", key, "' key exists in KVS.")
			return False

	## remove all keys and values
	def clear(self):
		self.keyValueDict.clear()
		return True


class readonlyDict(dict):
	def __init__(self, *args, **kw):
		super(readonlyDict, self).__init__(*args, **kw)


	def __setitem__(self, key, value):
		assert False, "cannot overwrite the KVS-param directly."

	def __getitem__(self, key):
		val = super(readonlyDict, self).__getitem__(key)
		if type(val) == dict:
			return readonlyDict(val)

		return val
		
	def __delitem__(self, key):
		assert False, "cannot delete the KVS-param directly."		


	def setToKVS(self, key, value):
		super(readonlyDict, self).__setitem__(key, value)


	def delete(self, key):
		super(readonlyDict, self).__delitem__(key)

