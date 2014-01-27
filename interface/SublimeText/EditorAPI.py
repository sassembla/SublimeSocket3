# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import os

# for log prefix.
from ... import SublimeSocketAPISettings


## sublime dependents apis and functions.
class EditorAPI:
	def generateSublimeViewInfo(self, viewInstance, viewKey, viewIdKey, viewBufferIdKey, viewPathKey, viewBaseNameKey, viewVNameKey, viewSelectedKey, isViewExist):
		existOrNot = False

		if self.isBuffer(viewInstance.file_name()):
			fileName = viewInstance.name()
			baseName = fileName
			
		else:
			existOrNot = True
			fileName = viewInstance.file_name()
			baseName = os.path.basename(fileName)
			

		return {
			viewKey : viewInstance,
			viewIdKey: viewInstance.id(),
			viewBufferIdKey: viewInstance.buffer_id(),
			viewPathKey: fileName,
			viewBaseNameKey: baseName,
			viewVNameKey: viewInstance.name(),
			viewSelectedKey: viewInstance.sel(),
			isViewExist: existOrNot
		}


	def isBuffer(self, path):
		if path:
			if os.path.exists(path):
				return False
			
		return True

	def isNamed(self, view):
		name = view.name()
		if 0 < len(name):
			return True
		else:
			return False

	def packagePath(self):
		return sublime.packages_path() 


	def loadSettings(self, key):
		return sublime.load_settings("SublimeSocket.sublime-settings").get(key)

	def runAfterDelay(self, execution, delay):
		sublime.set_timeout(execution, delay)


	def showMessageDialog(self, message):
		sublime.message_dialog(message)

	def openFile(self, name):
		return sublime.active_window().open_file(name)

	def windows(self):
		return sublime.windows()

	def viewsOfWindow(self, window):
		return window.views()

	def generateRegion(self, index, size):
		return sublime.Region(index, size)

	def statusMessage(self, message):
		sublime.status_message(message)

	def printMessage(self, message):
		print(SublimeSocketAPISettings.LOG_prefix, message)

	def addRegionToView(self, view, identity, regions, condition, color):
		if color == "sublime.DRAW_OUTLINED":
			color = sublime.DRAW_OUTLINED
			view.add_regions(identity, regions, condition, 'dot', color)

	def convertRegionToTuple(self, region):
		return (region.a, region.b)

	def removeRegionFromView(self, view, regionIdentity):
		view.erase_regions(regionIdentity)

	def platform(self):
		return sublime.platform()

	def getFileName(self):
		return sublime.active_window().active_view().file_name()

	def setNameToView(self, view, name):
		view.set_name(name)
		return view

	def nameOfView(self, view):
		return view.file_name()

	def runCommandOnView(self, view, command, params=None):
		if params:
			view.run_command(command, params)
		else:
			view.run_command(command)

	def closeView(self, view):
		view.close()

	def viewSize(self, view):
		return view.size()

	def addSelectionToView(self, view, pt):
		view.sel().add(pt)
		
	def isRegionContained(self, region, targetRegion):
		return targetRegion.contains(region)

	def bodyOfView(self, view):
		currentRegion = sublime.Region(0, view.size())
		return view.substr(view.word(currentRegion))
		
	def selectionAsStr(self, view):
		sel = view.sel()[0]
		(row, col) = view.rowcol(sel.a)
		return str(row)+","+str(col)

	def getLineRegion(self, view, lineCount):
		# Convert from 1 based to a 0 based line number
		line = int(lineCount) - 1
		
		# Negative line numbers count from the end of the buffer
		if line < 0:
			lines, _ = view.rowcol(view.size())
			line = lines + line + 1

		return view.line(view.text_point(line, 0))
		
