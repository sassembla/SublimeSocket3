# -*- coding: utf-8 -*-
import sublime, sublime_plugin
import threading
import uuid
import os

from .SublimeSocketServer import SublimeSocketServer
from . import SublimeSocketAPISettings

from .PythonSwitch import PythonSwitch


from .OpenHTML import Openhtml
# one history of tailMachine

# SublimeSocket server's thread
thread = None


tailPath = ""
tailReactor = ""

# one history of runSushiJSON
runPath = ""



class Socket_start_tailmachine(sublime_plugin.TextCommand):
    def run(self, edit):
        global tailPath

        caption = "input tail-target path:"

        defaultPath = sublime.load_settings("SublimeSocket.sublime-settings").get("defaultRunSushiJSONPath")

        if tailPath:
            initial_text = tailPath

        else:
            initial_text = defaultPath


        def getMessageAndStatus(pathCandidate):
            status = -1

            if os.path.isdir(pathCandidate):
                message = "tailMachine:" + pathCandidate + " is folder."

            else:
                if os.path.exists(pathCandidate):
                    message = "tailMachine:" + pathCandidate + " is exists."
                    status = 1                    
                else:
                    message = "tailMachine:" + pathCandidate + " is not exists."

            return (message, status)


        def on_done(path):
            global tailPath


            _, status = getMessageAndStatus(path)

            if status == 1:
                caption = "input tail-reactor path or SushiJSON-String:"

                def on_done_setReactor(reactorCandicate):
                    global tailPath
                    global tailReactor

                    tailPath = path
                    tailReactor = reactorCandicate

                    # do not check if file or string here.
                    _, result = getMessageAndStatus(reactorCandicate)

                    self.view.run_command("socket_on", {"params":{"type": SublimeSocketAPISettings.TAIL_MACHINE, "result": result, "tailPath":tailPath, "reactors":reactorCandicate, "continuation": True}})
            

                def on_change_setReactor(reactorCandicate):
                    # do nothing.
                    pass

                def on_cancel_setReactor():
                    # do nothing.
                    pass

                sublime.active_window().show_input_panel(caption, "", 
                    on_done_setReactor,
                    on_change_setReactor, 
                    on_cancel_setReactor)

            else:
                result = "tailMachine:cannot run:"+path
                sublime.status_message(result)
                print(SublimeSocketAPISettings.LOG_prefix, result)

        
        def on_change(pathCandidate):
            message, _ = getMessageAndStatus(pathCandidate)

            sublime.status_message(message)
            print(SublimeSocketAPISettings.LOG_prefix, message)

        def on_cancel():
            pass
            
        sublime.active_window().show_input_panel(caption, initial_text, on_done, on_change, on_cancel)



class Socket_start_tailmachine_repeat(sublime_plugin.TextCommand):
    def run(self, edit):
        global tailPath
        global tailReactor

        currentTailPath = tailPath
        currentTailReactor = tailReactor

        if tailPath and tailReactor:
            def getMessageAndStatus(pathCandidate):
                status = -1

                if os.path.isdir(pathCandidate):
                    pass
                else:
                    if os.path.exists(pathCandidate):
                        status = 1                    
                    else:
                        pass

                return status

            # do not check if file or string here.
            result = getMessageAndStatus(currentTailReactor)
            self.view.run_command("socket_on", {"params":{"type": SublimeSocketAPISettings.TAIL_MACHINE, "result": result, "tailPath":currentTailPath, "reactors":currentTailReactor}})
            



class Socket_run_sushijson(sublime_plugin.TextCommand):
    def run(self, edit):
        global runPath

        caption = "input the path of SushiJSON file:"

        defaultPath = sublime.load_settings("SublimeSocket.sublime-settings").get("defaultRunSushiJSONPath")

        if runPath:
            initial_text = runPath

        else:
            initial_text = defaultPath


        def getMessageAndStatus(pathCandidate):
            status = -1

            if os.path.isdir(pathCandidate):
                message = "runSushiJSON:" + pathCandidate + " is folder."

            else:
                if os.path.exists(pathCandidate):
                    message = "runSushiJSON:" + pathCandidate + " is exists."
                    status = 1                    
                else:
                    message = "runSushiJSON:" + pathCandidate + " is not exists."

            return (message, status)


        def on_done(path):
            global runPath
            _, status = getMessageAndStatus(path)

            if status == 1:
                runPath = path
                self.view.run_command("socket_on", {SublimeSocketAPISettings.ADDTRANSFER_PARAMS:{
                    SublimeSocketAPISettings.ADDTRANSFER_PROTOCOL: SublimeSocketAPISettings.PROTOCOL_RUNSUSHIJSON_SERVER,
                    SublimeSocketAPISettings.ADDTRANSFER_TRANSFERIDENTITY: "RUNSUSHIJSON_HANDLED_DEFAULT_TRANSFER",
                    SublimeSocketAPISettings.ADDTRANSFER_CONNECTIONIDENTITY: "RUNSUSHIJSON_HANDLED_DEFAULT_CONNECTION",
                    "path": path
                    }})

            else:
                result = "runSushiJSON:cannot run:" + path
                sublime.status_message(result)
                print(SublimeSocketAPISettings.LOG_prefix, result)

        
        def on_change(pathCandidate):
            message, _ = getMessageAndStatus(pathCandidate)

            sublime.status_message(message)
            print(SublimeSocketAPISettings.LOG_prefix, message)

        def on_cancel():
            pass
            
        sublime.active_window().show_input_panel(caption, initial_text, on_done, on_change, on_cancel)





# states are below.
# not active -> active == serving <-> transfering

#                     serving:on
#                     serving:off
#                     serving:restart
# 
#                           transfer:setup
#                           transfer:spinup
# 
#                           transfer:restart
#                           transfer:teardown
# 
#                           transfers:closeall

class Socket_on(sublime_plugin.TextCommand):
    def run(self, edit, params=None):
        if params:
            assert SublimeSocketAPISettings.ADDTRANSFER_PROTOCOL in params, "SocketOn require 'protocol' params."
        else:
            transferProtocol = sublime.load_settings("SublimeSocket.sublime-settings").get("defaultTransferProtocol")
            params = sublime.load_settings("SublimeSocket.sublime-settings").get(transferProtocol)
            params[SublimeSocketAPISettings.ADDTRANSFER_PROTOCOL] = transferProtocol

        self.startServer(params)


    @classmethod
    def restartServer(self):
        global thread
        if thread and thread.is_alive():
            thread.restartServer()

        else:
            notActivatedMessage = "SublimeSocket not yet activated."
            sublime.status_message(notActivatedMessage)
            print(SublimeSocketAPISettings.LOG_prefix, notActivatedMessage)


    @classmethod
    def startServer(self, args):
        global thread
        
        if thread and thread.is_alive():
            thread.setupThread(args)

        else:
            thread = SublimeSocketThread(args)
            thread.start()


class Socket_on_then_test(sublime_plugin.TextCommand):
    def run(self, edit):
        transferProtocol = sublime.load_settings("SublimeSocket.sublime-settings").get("defaultTransferProtocol")
        baseArgs = sublime.load_settings("SublimeSocket.sublime-settings").get(transferProtocol)
            
        params = baseArgs
        params[SublimeSocketAPISettings.ADDTRANSFER_PROTOCOL] = transferProtocol
        params["runTests"] = True

        def start():
            self.view.run_command("socket_on", {"params":params})

        global thread
        
        if thread and thread.is_alive():            
            # run after teardowned.
            self.view.run_command("socket_off")

            start()
        else:
            start()
        

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
            print(SublimeSocketAPISettings.LOG_prefix, message)
            

class Transfer_info(sublime_plugin.TextCommand):
    def run(self, edit):
        global thread

        if thread and thread.is_alive():
            message = thread.server.showTransferInfo()
            sublime.status_message(message)
            print(SublimeSocketAPISettings.LOG_prefix, message)

        else:
            message = "SublimeSocket not yet activated."
            sublime.status_message(message)
            print(SublimeSocketAPISettings.LOG_prefix, message)





# threading
class SublimeSocketThread(threading.Thread):
    def __init__(self, args):
        threading.Thread.__init__(self)
        self.server = SublimeSocketServer()
        
        # setup and get identity for transfer.
        self.setupThread(args)



    def setupThread(self, params):
        # get transferIdentity for prepare action.
        transferIdentity = self.server.setupTransfer(params)
        if "runTests" in params:
            Openhtml.openSublimeSocketTest(params)
            
            testSuiteFilePath = sublime.packages_path() + "/"+SublimeSocketAPISettings.MY_PLUGIN_PATHNAME+"/"+sublime.load_settings("SublimeSocket.sublime-settings").get('testSuiteFilePath')

            
            def runTests():
                self.server.api.runTests({SublimeSocketAPISettings.RUNTESTS_PATH:testSuiteFilePath}, transferIdentity, "sublimesockettest")
            
            self.server.appendOnConnectedTriggers(transferIdentity, [runTests])
        
    # called by thread.start
    def run(self):
        self.server.spinupLatestTransfer()
        

    def restartServer(self):
        # restart means reset @ SublimeSocketServer.
        self.server.resetServer()



    def showKVS(self):
        self.server.showAllKeysAndValues()

    def flushKVS(self):
        self.server.clearAllKeysAndValues()


  # send eventName and data to server. gen results from here for view-oriented-event-fireing.
    def viewEmitViaSublime(self, eventName, view):
        if self.server:

            if not view:
                return
                
            # avoid empty-file
            if view.is_scratch():
                # print "scratch buffer."
                return

            eventParam = self.server.api.editorAPI.generateViewInfo(
                view, None, None,
                SublimeSocketAPISettings.REACTOR_VIEWKEY_VIEWSELF,
                SublimeSocketAPISettings.REACTOR_VIEWKEY_PATH,
                SublimeSocketAPISettings.REACTOR_VIEWKEY_NAME,
                SublimeSocketAPISettings.REACTOR_VIEWKEY_SELECTEDS,
                SublimeSocketAPISettings.REACTOR_VIEWKEY_ISEXIST
            )
            
            emitIdentity = str(uuid.uuid4())
            eventParam[SublimeSocketAPISettings.REACTOR_VIEWKEY_EMITIDENTITY] = emitIdentity

            self.server.api.fireReactor(SublimeSocketAPISettings.REACTORTYPE_VIEW, eventName, eventParam)


    def getReactorDataFromServer(self, eventName, view):
        if self.server:

            # avoid empty-file
            if view.is_scratch():
                return
                
            elif not view.file_name():
                return

            view_file_name = view.file_name()

            if view_file_name:
                return self.server.api.consumeCompletion(view_file_name, eventName)
            
    def teardownServer(self):
        # close the SublimeSocketServer and this thread.
        self.server.teardownServer()




# kvs control

class Kvs_show(sublime_plugin.TextCommand):
    def run(self, edit):
        global thread

        if thread and thread.is_alive():
            thread.showKVS()
        else:
            message = "SublimeSocket not yet activated."
            sublime.status_message(message)
            print(SublimeSocketAPISettings.LOG_prefix, message)


class Kvs_flush(sublime_plugin.TextCommand):
    def run(self, edit):
        global thread

        if thread and thread.is_alive():
            thread.flushKVS()
        else:
            message = "SublimeSocket not yet activated."
            sublime.status_message(message)
            print(SublimeSocketAPISettings.LOG_prefix, message)


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

    def on_query_completions(self, view, prefix, locations):
        completions = self.getDataFromThread(SublimeSocketAPISettings.REACTABLE_VIEW_ON_QUERY_COMPLETIONS, view)
        if completions:
            # add prefix for prevent force-input.
            completions.append((prefix, prefix))
            return completions

    ## call when the event happen
    def update(self, eventName, view=None):
        global thread

        
        if thread and thread.is_alive():
            thread.viewEmitViaSublime(eventName, view)



    def updateViewInfo(self, view):
        if self.currentViewInfo and self.currentViewInfo["view"] == view.file_name():
            beforeSize = self.currentViewInfo["size"]
            
            self.currentViewInfo["view"] = view.file_name()
            self.currentViewInfo["size"] = view.size()

            if beforeSize > self.currentViewInfo["size"]:
                self.update(SublimeSocketAPISettings.REACTABLE_VIEW_SS_V_DECREASED, view)
            
            if beforeSize < self.currentViewInfo["size"]:
                self.update(SublimeSocketAPISettings.REACTABLE_VIEW_SS_V_INCREASED, view)
                    
        else:
            self.currentViewInfo["view"] = view.file_name()
            self.currentViewInfo["size"] = view.size()


    def getDataFromThread(self, eventName, view=None):    
        global thread
        
        if thread and thread.is_alive():
                return thread.getReactorDataFromServer(eventName, view)



# view contents control
class InsertTextCommand(sublime_plugin.TextCommand):
    def run(self, edit, string='', fromParam=0):
        
        fromParam = int(fromParam)
        if fromParam == -1:
            self.view.insert(edit, self.view.size(), string)
        else:
            self.view.insert(edit, fromParam, string)

class ReduceTextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        region = sublime.Region(self.view.size()-1, self.view.size())
        self.view.erase(edit, region)
    
class ClearSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.sel().clear()
    
    
