# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import threading
from .SublimeWSServer import SublimeWSServer
from .OpenPreference import Openpreference

from . import SublimeSocketAPISettings
import os

import uuid


# WebSocket server's thread
thread = None

class Socketon(sublime_plugin.TextCommand):
  def run(self, edit):
    self.startServer()

  @classmethod
  def startServer(self):
    global thread

    host = sublime.load_settings("SublimeSocket.sublime-settings").get('host')
    port = sublime.load_settings("SublimeSocket.sublime-settings").get('port')


    if thread is not None and thread.is_alive():
      if (thread.isServerAlive()):
        alreadyRunningMessage = "SublimeSocket Already Running."
        sublime.status_message(alreadyRunningMessage)
        print("ss:", alreadyRunningMessage)

      else:
        thread.set(host, port)
        thread.run();

    else:
      thread = SublimeSocketThread(host, port)
      thread.start()
    
class On_then_openpref(sublime_plugin.TextCommand):
  def run(self, edit):
    Socketon.startServer()
    Openpreference.openSublimeSocketPreference()
      

class Test(sublime_plugin.TextCommand):
  def run(self, edit):
    global thread
    if thread is not None and thread.is_alive():
      
      Openpreference.openSublimeSocketTest()
    else:
      notActivatedMessage = "SublimeSocket not yet activated."
      sublime.status_message(notActivatedMessage)
      print("ss:", notActivatedMessage)

class On_then_test(sublime_plugin.TextCommand):
   def run(self, edit):
    Socketon.startServer()
    Openpreference.openSublimeSocketTest()

class Statuscheck(sublime_plugin.TextCommand):
  def run(self, edit):
    global thread
    if thread is not None and thread.is_alive():
      thread.currentConnections()
    else:
      notActivatedMessage = "SublimeSocket not yet activated."
      sublime.status_message(notActivatedMessage)
      print("ss:", notActivatedMessage)

class Socketoff(sublime_plugin.TextCommand):
  def run(self, edit):
    global thread
    if thread is not None and thread.is_alive():
      if (thread.isServerAlive()):
        thread.tearDownServer()

    else:
      notActivatedMessage = "SublimeSocket not yet activated."
      sublime.status_message(notActivatedMessage)
      print("ss:", notActivatedMessage)
      
# threading
class SublimeSocketThread(threading.Thread):
  def __init__(self, host, port):
    threading.Thread.__init__(self)
    self.set(host, port)

  # call through thread-initialize
  def run(self):
    result = self._server.start(self._host, self._port)
    
    if result is 0:
      pass
    else:
      self.tearDownServer()


  def set(self, host, port):
    self._host = host
    self._port = port

    self._server = SublimeWSServer()

  # send eventName and data to server. gen results from here for view-oriented-event-fireing.
  def toServer(self, eventName, view):
    if self._server is None:
      pass
    else:

      if not view:
        return
        
      # avoid empty-file
      if view.is_scratch():
        # print "scratch buffer."
        return

      view_file_name = view.file_name()

      if view_file_name:
        eventParam = self._server.getSublimeViewInfo(
          view,
          SublimeSocketAPISettings.REACTOR_VIEWKEY_VIEWSELF,
          SublimeSocketAPISettings.REACTOR_VIEWKEY_ID,
          SublimeSocketAPISettings.REACTOR_VIEWKEY_BUFFERID,
          SublimeSocketAPISettings.REACTOR_VIEWKEY_PATH,
          SublimeSocketAPISettings.REACTOR_VIEWKEY_BASENAME,
          SublimeSocketAPISettings.REACTOR_VIEWKEY_VNAME,
          SublimeSocketAPISettings.REACTOR_VIEWKEY_SELECTED
        )

        results = self._server.api.initResult("view:"+str(uuid.uuid4()))

        self._server.fireKVStoredItem(SublimeSocketAPISettings.REACTORTYPE_VIEW, eventName, eventParam, results)


  def getReactorDataFromServer(self, eventName, view):
    if self._server is None:
      pass
    else:
      # avoid empty-file
      if view.is_scratch():
        # print "scratch buffer."
        return
        
      elif not view.file_name():
        # print "no path"
        return

      view_file_name = view.file_name()

      if view_file_name:
        eventParam = self._server.getSublimeViewInfo(
          view,
          SublimeSocketAPISettings.REACTOR_VIEWKEY_VIEWSELF,
          SublimeSocketAPISettings.REACTOR_VIEWKEY_ID,
          SublimeSocketAPISettings.REACTOR_VIEWKEY_BUFFERID,
          SublimeSocketAPISettings.REACTOR_VIEWKEY_PATH,
          SublimeSocketAPISettings.REACTOR_VIEWKEY_BASENAME,
          SublimeSocketAPISettings.REACTOR_VIEWKEY_VNAME,
          SublimeSocketAPISettings.REACTOR_VIEWKEY_SELECTED
        )

        return self._server.consumeCompletion(view_file_name, eventName)
      
  def currentConnections(self):
    self._server.showCurrentStatusAndConnections()
  
  def tearDownServer(self):
    self._server.tearDown()
    self._server = None

  def isServerAlive(self):
    if not self._server:
      return False
    return True

# event listeners
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
    self.update(SublimeSocketAPISettings.REACTABLE_VIEW_ON_SELECTION_MODIFIED, view)
    # self.updateViewInfo(view)

  def on_query_completions(self, view, prefix, locations):
    ret = self.get(SublimeSocketAPISettings.REACTABLE_VIEW_ON_QUERY_COMPLETIONS, view)
    
    if ret:
      return ret

  ## call when the event happen
  def update(self, eventName, view=None):
    print("eventName!", eventName)
    global thread

    if thread is not None and thread.is_alive():
      thread.toServer(eventName, view)


  def updateViewInfo(self, view):
    print("updateViewInfo")
    if self.currentViewInfo and self.currentViewInfo["view"] == view:
        print("updateViewInfo currentあり", view.size())
        beforeSize = self.currentViewInfo["size"]
        
        self.currentViewInfo["view"] = view
        self.currentViewInfo["size"] = view.size()

        if beforeSize > self.currentViewInfo["size"]:
          print("down", view.file_name())
          self.update(SublimeSocketAPISettings.REACTABLE_VIEW_SS_V_DECREASED, view)
        
        if beforeSize < self.currentViewInfo["size"]:
          print("up", view.file_name())
          self.update(SublimeSocketAPISettings.REACTABLE_VIEW_SS_V_INCREASED, view)
          
    else:
      self.currentViewInfo["view"] = view
      self.currentViewInfo["size"] = view.size()
      print("updateViewInfo currentなし", view.size())


  def get(self, eventName, view=None):    
    global thread

    if thread is not None and thread.is_alive():
      return thread.getReactorDataFromServer(eventName, view)
