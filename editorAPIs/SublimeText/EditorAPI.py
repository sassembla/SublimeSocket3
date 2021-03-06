# -*- coding: utf-8 -*-
import sublime, sublime_plugin
from itertools import chain
import os

# for log prefix.
from ... import SublimeSocketAPISettings


## sublime dependents apis and functions.
class EditorAPI:
	def generateViewInfo(
		self, 
		viewInstance, 
		pathSource,
		nameSource,
		viewKey, 
		viewPathKey, 
		viewNameKey, 
		viewSelectedsKey, 
		isViewExist):
		existOrNot = False
		
		if self.isBuffer(viewInstance.file_name()):
			fileName = viewInstance.name()
			name = fileName
			
		else:
			existOrNot = True
			fileName = viewInstance.file_name()
			name = os.path.basename(fileName)
		
		selecteds = []

		# generate selected-region's (from, to) set.
		for region in viewInstance.sel():
			# don't count 0 width selection.
			if region.a != region.b:
				regionTupel = (region.a, region.b)
				selecteds.append(regionTupel)

		return {
			viewKey : viewInstance,
			viewPathKey: fileName,
			viewNameKey: name,
			viewSelectedsKey: selecteds,
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

	def showPopupMenu(self, view, items, reactor):
		view.show_popup_menu(items, reactor);

	def openFile(self, name):
		return sublime.active_window().open_file(name)

	def windows(self):
		return sublime.windows()

	def generateRegion(self, theFrom, theTo):
		return sublime.Region(theFrom, theTo)

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

	def allOpenedPaths(self):
		views = list(chain.from_iterable([window.views() for window in self.windows()]))
		return [self.nameOfView(view) for view in views]

	def viewFromPath(self, fullpath):
		views = list(chain.from_iterable([window.views() for window in self.windows()]))
		for view in views:
			if self.nameOfView(view) == fullpath:
				return view

	def setNameToView(self, view, name):
		view.set_name(name)
		return view

	def nameOfView(self, view):
		return view.file_name()

	def runCommandOn(self, view, command, params=None):
		if params:
			view.run_command(command, params)
		else:
			view.run_command(command)

	def closeView(self, view):
		view.close()
		
	def closeAllViewsInCurrentWindow(self):
		self.runCommandOn(sublime.active_window(), "close_all")

	def allViewsInCurrentWindow(self):
		return sublime.active_window().views()

	def viewSize(self, view):
		return view.size()

	def addSelectionToView(self, view, pt):
		view.sel().add(pt)

	def selectedBody(self, view, region):
		return view.substr(region)
		
	def clearSelectionOfView(self, view):
		cleards = []
		cleardsSources = view.sel()
		for cleardsSource in cleardsSources:
			key = (cleardsSource.a, cleardsSource.b)
			value = view.substr(cleardsSource)
			
			cleards.append({key:value})

		view.sel().clear()

		return cleards
		
	def isRegionContained(self, region, selecteds, isExactly, isSameLine):
		selectionRegionList = [self.generateRegion(regionParam[0], regionParam[1]) for regionParam in selecteds]

		for selectionRegion in selectionRegionList:
			if selectionRegion.contains(region):
				if isExactly:
					if selectionRegion.a == region.a and selectionRegion.b-1 == region.b:
						return True
					else:
						return False
				elif isSameLine:
					pass

				return True

		return False

	def bodyOfView(self, view):
		currentRegion = sublime.Region(0, view.size())
		return view.substr(view.word(currentRegion))

	def crossedContents(self, view, fromParam, toParam):
		return view.substr(sublime.Region(fromParam, toParam))
		
	def selectionAsStr(self, view):
		sel = view.sel()
		if sel and 0 < len(sel):
			selRegion = view.sel()[0]
			(row, col) = view.rowcol(selRegion.a)
			return str(row)+","+str(col)

	def scrollTo(self, view, line, count):
		if line:
			count = view.text_point(line, 0)
		
		view.show_at_center(count)

	def getLineRegion(self, view, lineCount):
		# Convert from 1 based to a 0 based line number
		line = int(lineCount) - 1
		
		# Negative line numbers count from the end of the buffer
		if line < 0:
			lines, _ = view.rowcol(view.size())
			line = lines + line + 1

		return view.line(view.text_point(line, 0))

	def getTextPoint(self, view, line):
		return view.text_point(line, 0)
		
	def getLineFromPoint(self, view, count):
		return view.rowcol(count)

	def getViewSetting(self, view):
		return (view.settings().get('tab_size'), view.settings().get('translate_tabs_to_spaces'))	
