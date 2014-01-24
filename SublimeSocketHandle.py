# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import threading

from .OpenPreference import Openpreference
from .SublimeSocketServer import SublimeSocketServer
from . import SublimeSocketAPISettings
import os

import uuid


# SublimeSocket server's thread
thread = None

class Socketon(sublime_plugin.TextCommand):
  def run(self, edit):
    print("未調整、デフォルトをセットしないと。")
    self.startServer("", [])


  @classmethod
  def startServer(self, transferMethod, args):
    global thread

    if thread and thread.is_alive():
      if (thread.isServerAlive()):
        alreadyRunningMessage = "SublimeSocket Already Running."
        sublime.status_message(alreadyRunningMessage)
        print("ss:", alreadyRunningMessage)

    else:
      thread = SublimeSocketThread(transferMethod, args)
      thread.start()

      print("argsに応じてここでもなにかする、というコードを書く事になる。二重になっちゃうのがやだな、、考えよう。")
      if "WebSocketServer" in transferMethod:
        host = sublime.load_settings("SublimeSocket.sublime-settings").get("WebSocketServer").get("host")
        port = sublime.load_settings("SublimeSocket.sublime-settings").get("WebSocketServer").get("port")

        if "runTests" in args:
          Openpreference.openSublimeSocketTest(host, port)

    
    
class On_then_openpref(sublime_plugin.TextCommand):
  def run(self, edit):
    Socketon.startServer()
    Openpreference.openSublimeSocketPreference()
      

class Test(sublime_plugin.TextCommand):
  def run(self, edit):
    global thread
    if thread and thread.is_alive():
      print("provisionみたいに、特定のものを走らせる、みたいな仕掛けがいいなあ。と思うけど、ちょっと脳が回ってないので後で考える。")
      Openpreference.openSublimeSocketTest()
    else:
      notActivatedMessage = "SublimeSocket not yet activated."
      sublime.status_message(notActivatedMessage)
      print("ss:", notActivatedMessage)


class On_then_test(sublime_plugin.TextCommand):
   def run(self, edit):
    Socketon.startServer("WebSocketServer", ["runTests"])


class Socketoff(sublime_plugin.TextCommand):
  def run(self, edit):
    global thread

    if thread and thread.is_alive():
      if (thread.isServerAlive()):
        thread.tearDownServer()

    else:
      notActivatedMessage = "SublimeSocket not yet activated."
      sublime.status_message(notActivatedMessage)
      print("ss:", notActivatedMessage)
      





# threading
class SublimeSocketThread(threading.Thread):
  def __init__(self, transferMethod, args):
    threading.Thread.__init__(self)
    self.server = None
    self.transferMethod = transferMethod
    self.args = args

  # call through thread-initialize
  def run(self):
    self.server = SublimeSocketServer(self.transferMethod, self.args)
    


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

      self.server.fireKVStoredItem(SublimeSocketAPISettings.REACTORTYPE_VIEW, eventName, eventParam, results)


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
        return self.server.consumeCompletion(view_file_name, eventName)
      
  def tearDownServer(self):
    self.server.transferTearDown()



  def isServerAlive(self):
    if self.server:
      return True
    return False



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
    self.update(SublimeSocketAPISettings.REACTABLE_VIEW_ON_SELECTION_MODIFIED, view)
    # self.updateViewInfo(view)

  def on_query_completions(self, view, prefix, locations):
    ret = self.get(SublimeSocketAPISettings.REACTABLE_VIEW_ON_QUERY_COMPLETIONS, view)
    
    if ret:
      return ret

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


  def get(self, eventName, view=None):    
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
    
