# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import threading

from .OpenHTML import Openhtml
from .SublimeSocketServer import SublimeSocketServer
from . import SublimeSocketAPISettings

import uuid


# SublimeSocket server's thread
thread = None


# states are below.
# not active -> active <-> serving <-> transfering

#                   serving:on
#                   serving:off
#                   serving:restart
# 
#                              transfer:restart
#                              transfer:change
#                              transfer:close

class Socket_on(sublime_plugin.TextCommand):
  def run(self, edit):

    defaultTransferMethod = sublime.load_settings("SublimeSocket.sublime-settings").get("defaultTransferMethod")
    self.startServer(defaultTransferMethod, [])


  @classmethod
  def restartServer(self):
    global thread
    if thread and thread.is_alive():
      thread.restartServer()

    else:
      notActivatedMessage = "SublimeSocket not yet activated."
      sublime.status_message(notActivatedMessage)
      print("ss:", notActivatedMessage)


  @classmethod
  def startServer(self, transferMethod, args):
    global thread
    if thread and thread.is_alive():
      thread.setupThread(transferMethod, args)

    else:
      thread = SublimeSocketThread(transferMethod, args)
      thread.start()


class Socket_on_then_test(sublime_plugin.TextCommand):
  def run(self, edit):
    Socket_on.startServer("WebSocketServer", ["runTests"])

class Socket_restart(sublime_plugin.TextCommand):
  def run(self, edit):
    Socket_on.restartServer()

class Socket_off(sublime_plugin.TextCommand):
  def run(self, edit):
    global thread

    if thread and thread.is_alive():
      thread.teardownServer()

    else:
      message = "SublimeSocket not yet activated."
      sublime.status_message(message)
      print("ss:", message)
      

class Transfer_info(sublime_plugin.TextCommand):
  def run(self, edit):
    global thread

    if thread and thread.is_alive():
      message = thread.server.showTransferInfo()
      sublime.status_message(message)
      print("ss:", message)

    else:
      message = "SublimeSocket not yet activated."
      sublime.status_message(message)
      print("ss:", message)





# threading
class SublimeSocketThread(threading.Thread):
  def __init__(self, transferMethod, args):
    threading.Thread.__init__(self)
    self.server = SublimeSocketServer()

    self.setupThread(transferMethod, args)


  # called by thread.start
  def run(self):
    self.server.spinupTransfer()


  def setupThread(self, transferMethod, args):
    
    if transferMethod in SublimeSocketAPISettings.TRANSFER_METHODS:
      params = sublime.load_settings("SublimeSocket.sublime-settings").get(transferMethod)
      
      self.server.setupTransfer(transferMethod, params)

    if "runTests" in args:
      testSuiteFilePath = sublime.packages_path() + "/"+SublimeSocketAPISettings.MY_PLUGIN_PATHNAME+"/"+sublime.load_settings("SublimeSocket.sublime-settings").get('testSuiteFilePath')
      params["testSuiteFilePath"] = testSuiteFilePath
      
      Openhtml.openSublimeSocketTest(params)


  def restartServer(self):
    # restart means reset @ SublimeSocketServer.
    self.server.resetServer()


  # send eventName and data to server. gen results from here for view-oriented-event-fireing.
  def toSublimeSocketServer(self, eventName, view):
    if self.server:

      if not view:
        return
        
      # avoid empty-file
      if view.is_scratch():
        # print "scratch buffer."
        return

      eventParam = self.server.api.editorAPI.generateSublimeViewInfo(
        view,
        SublimeSocketAPISettings.REACTOR_VIEWKEY_VIEWSELF,
        SublimeSocketAPISettings.REACTOR_VIEWKEY_ID,
        SublimeSocketAPISettings.REACTOR_VIEWKEY_BUFFERID,
        SublimeSocketAPISettings.REACTOR_VIEWKEY_PATH,
        SublimeSocketAPISettings.REACTOR_VIEWKEY_BASENAME,
        SublimeSocketAPISettings.REACTOR_VIEWKEY_VNAME,
        SublimeSocketAPISettings.REACTOR_VIEWKEY_SELECTED,
        SublimeSocketAPISettings.REACTOR_VIEWKEY_ISEXIST
      )
      
      emitIdentity = str(uuid.uuid4())
      eventParam[SublimeSocketAPISettings.REACTOR_VIEWKEY_EMITIDENTITY] = emitIdentity

      results = self.server.api.initResult("view:"+emitIdentity)

      self.server.api.fireReactor(SublimeSocketAPISettings.REACTORTYPE_VIEW, eventName, eventParam, results)


  def getReactorDataFromServer(self, eventName, view):
    if self.server:
      # avoid empty-file
      if view.is_scratch():
        # print "scratch buffer."
        return
        
      elif not view.file_name():
        # print "no path"
        return

      view_file_name = view.file_name()

      if view_file_name:
        return self.server.api.consumeCompletion(view_file_name, eventName)
      
  def teardownServer(self):
    # close the SublimeSocketServer and this thread.
    self.server.teardownServer()



# view listeners
class CaptureEditing(sublime_plugin.EventListener):
  def __init__(self):
    self.currentViewInfo = {}
  
  def on_modified(self, view):
    self.update(SublimeSocketAPISettings.REACTABLE_VIEW_ON_MODIFIED, view)
    self.updateViewInfo(view)

  def on_new(self, view):
    self.update(SublimeSocketAPISettings.REACTABLE_VIEW_ON_NEW, view)

  def on_clone(self, view):
    self.update(SublimeSocketAPISettings.REACTABLE_VIEW_ON_CLOSE, view)

  def on_load(self, view):
    self.update(SublimeSocketAPISettings.REACTABLE_VIEW_ON_LOAD, view)
    self.updateViewInfo(view)
    
  def on_close(self, view):
    self.update(SublimeSocketAPISettings.REACTABLE_VIEW_ON_CLOSE, view)

  def on_pre_save(self, view):
    self.update(SublimeSocketAPISettings.REACTABLE_VIEW_ON_PRE_SAVE, view)

  def on_post_save(self, view):
    self.update(SublimeSocketAPISettings.REACTABLE_VIEW_ON_POST_SAVE, view)
    
  def on_selection_modified(self, view):
    s = view.sel()
    print("view.sel()", dir(s))
    self.update(SublimeSocketAPISettings.REACTABLE_VIEW_ON_SELECTION_MODIFIED, view)

  def on_query_completions(self, view, prefix, locations):
    completions = self.getDataFromThread(SublimeSocketAPISettings.REACTABLE_VIEW_ON_QUERY_COMPLETIONS, view)
    
    if completions:
      return completions

  ## call when the event happen
  def update(self, eventName, view=None):
    global thread

    if thread and thread.is_alive():
      thread.toSublimeSocketServer(eventName, view)


  def updateViewInfo(self, view):
    if self.currentViewInfo and self.currentViewInfo["view"] == view:
        beforeSize = self.currentViewInfo["size"]
        
        self.currentViewInfo["view"] = view
        self.currentViewInfo["size"] = view.size()

        if beforeSize > self.currentViewInfo["size"]:
          self.update(SublimeSocketAPISettings.REACTABLE_VIEW_SS_V_DECREASED, view)
        
        if beforeSize < self.currentViewInfo["size"]:
          self.update(SublimeSocketAPISettings.REACTABLE_VIEW_SS_V_INCREASED, view)

    else:
      self.currentViewInfo["view"] = view
      self.currentViewInfo["size"] = view.size()


  def getDataFromThread(self, eventName, view=None):    
    global thread
    
    if thread and thread.is_alive():
      return thread.getReactorDataFromServer(eventName, view)



# view contents control
class InsertTextCommand(sublime_plugin.TextCommand):
  def run(self, edit, string=''):
    self.view.insert(edit, self.view.size(), string)


class ReduceTextCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    region = sublime.Region(self.view.size()-1, self.view.size())
    self.view.erase(edit, region)
    
class ClearSelectionCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    print("clear!")
    self.view.sel().clear()


    