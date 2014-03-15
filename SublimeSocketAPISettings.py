import os



# SublimeSocket API 

SS_HOST_REPLACE				= "SUBLIMESOCKET_HOST"
SS_PORT_REPLACE				= "SUBLIMESOCKET_PORT"
SS_VERSION_REPLACE			= "SUBLIMESOCKET_VERSION"
	
	
HTML_REPLACEABLE_KEYS		= [SS_HOST_REPLACE, SS_PORT_REPLACE, SS_VERSION_REPLACE]

# get folder name of this plugin.
MY_PLUGIN_PATHNAME			= os.path.split(os.path.dirname(os.path.realpath(__file__)))[1]
	
RUNSUSHIJSON_SERVER			= "RunSushiJSONServer"
WEBSOCKET_SERVER			= "WebSocketServer"
TAIL_MACHINE				= "TailMachine"
TRANSFER_METHODS			= [RUNSUSHIJSON_SERVER, WEBSOCKET_SERVER, TAIL_MACHINE]
	
# KVS	
	
DICT_VIEWS					= "DICT_VIEWS"
VIEW_SELF					= "view"
VIEW_PATH					= "path"
VIEW_NAME					= "name"
VIEW_SELECTEDS				= "selecteds"
VIEW_ISEXIST				= "isExist"
	
	
DICT_COMPLETIONS			= "DICT_COMPLETIONS"
DICT_FILTERS				= "DICT_FILTERS"
DICT_REACTORS				= "DICT_REACTORS"
DICT_REACTORSLOG			= "DICT_REACTORS_LOG"
REACTORSLOG_LATEST			= "latest"

DICT_REGIONS				= "DICT_REGIONS"
REGION_IDENTITY				= "identity"
REGION_ISSELECTING			= "isSelecting"
REGION_FROM					= "from"
REGION_TO					= "to"
REGION_LINE					= "line"
REGION_MESSAGES				= "messages"
REGIONDATA_MESSAGE			= "message"


# region identifier prefix
REGION_UUID_PREFIX			= "ss_"



# API

SSAPI_PREFIX				= "sublimesocket"

SSAPI_PREFIX_SUB			= "ss"
SSAPI_DEFINE_DELIM			= "@"	# sublimesocket@commandA:{}->commandB:{}->commandC:[]->


SSAPI_VERSION				= "1.4.1"
SSSOCKET_VERSION			= 3	# for Sublime Text 3



# SublimeSocket internal event definition
SS_EVENT_COLLECT			= "ss_collect"
SS_EVENT_LOADING			= "ss_loading"
SS_EVENT_RENAMED			= "ss_renamed"



SS_FOUNDATION_NOVIEWFOUND	= "ss_f_noViewFound"
NOVIEWFOUND_NAME			= "name"
NOVIEWFOUND_MESSAGE			= "message"
NOVIEWFOUND_INJECTIONS		= [NOVIEWFOUND_NAME, NOVIEWFOUND_MESSAGE]

SS_FOUNDATION_VIEWEMIT		= "ss_f_viewemit"

SS_VIEWKEY_CURRENTVIEW		= "ss_viewkey_current"


# internal APIs/

INTERNAL_API_RUNTESTS		= "runTests"
RUNTESTS_PATH				= "path"

# /internal APIs


"""
@apiGroup connectedCall
@api {SushiJSON} connectedCall:{} raise SublimeSocketServer's connected event.
"""
# public APIs
API_CONNECTEDCALL 			= "connectedCall"
# no injection, no key, no value.

"""
@apiGroup versionVerify
@api {SushiJSON} versionVerify:{JSON} check SublimeSocket version from client.
@apiExample [example]
versionVerify: {
    "socketVersion": 3,
    "apiVersion": "1.-1.0",
    "injects": {
        "code": "code",
        "message": "theMessage"
    },
    "selectors": [
        {
            "showAtLog<-code, theMessage": {
                "format": "[code] [theMessage]"
            }
        }
    ]
}
@apiParam {String} socketVersion the version of expected SublimeSocket version.(2 or 3)
@apiParam {String} apiVersion the version of expected SublimeSocket API version.(a.b.c)

@apiSuccess {Int} code_2 (2) VERIFICATION_CODE_VERIFIED_CLIENT_UPDATE
@apiSuccess {Int} code_1 (1) VERIFICATION_CODE_VERIFIED		
@apiSuccess {Int} code_0 (0) VERIFICATION_CODE_REFUSED_DIFFERENT_SUBLIMESOCKET
@apiSuccess {Int} code_-1 (-1) VERIFICATION_CODE_REFUSED_SUBLIMESOCKET_UPDATE
@apiSuccess {Int} code_-2 (-2) VERIFICATION_CODE_REFUSED_CLIENT_UPDATE
@apiSuccess {String} message result message of verification.
"""
API_VERSIONVERIFY			= "versionVerify"
VERSIONVERIFY_SOCKETVERSION	= "socketVersion"
VERSIONVERIFY_APIVERSION	= "apiVersion"
VERSIONVERIFY_CODE			= "code"
VERSIONVERIFY_MESSAGE		= "message"
VERSIONVERIFY_DRYRUN		= "dryrun"
VERSIONVERIFY_INJECTIONS = [VERSIONVERIFY_CODE, VERSIONVERIFY_MESSAGE]

VERIFICATION_CODE_VERIFIED_CLIENT_UPDATE			= 2
VERIFICATION_CODE_VERIFIED							= 1
VERIFICATION_CODE_REFUSED_DIFFERENT_SUBLIMESOCKET	= 0
VERIFICATION_CODE_REFUSED_SUBLIMESOCKET_UPDATE		= -1
VERIFICATION_CODE_REFUSED_CLIENT_UPDATE				= -2


"""
no document. this is method only for test.
"""
API_ASSERTRESULT			= "assertResult"
ASSERTRESULT_CONTEXT		= "context"
ASSERTRESULT_CONTAINS		= "contains"
ASSERTRESULT_NOTCONTAINS	= "notcontains"
ASSERTRESULT_ISEMPTY		= "isempty"
ASSERTRESULT_ISNOTEMPTY		= "isnotempty"
ASSERTRESULT_ID				= "id"
ASSERTRESULT_DESCRIPTION	= "description"
ASSERTRESULT_DEBUG			= "debug"
ASSERTRESULT_VALUE_PASS		= "Pass:"
ASSERTRESULT_VALUE_FAIL		= "Fail:"
ASSERTRESULT_RESULT			= "result"
ASSERTRESULT_PASSEDORFAILED = "passedOrFailed"


"""
@apiGroup afterAsync
@api {SushiJSON} afterAsync:{JSON} go to next API and run selectors after milliseconds
@apiExample [example]
afterAsync: {
    "identity": "testIdentity",
    "ms": 100,
    "selectors": [
        {
            "showAtLog": {
                "message": "hello after 100"
            }
        }
    ]
}

@apiParam {String} identity identifier of this async block.
@apiParam {Int} ms run selectors after this milliseconds.
@apiParam {JSON} selectors run after ms.

@apiSuccess {Everything} keys_and_values this api injects all keys and values to selectors.
"""
API_AFTERASYNC				= "afterAsync"
AFTERASYNC_IDENTITY			= "identity"
AFTERASYNC_MS				= "ms"


"""
@apiGroup wait
@api {SushiJSON} wait:{JSON} wait milliseconds and go to next.
@apiExample [example]
wait:{
    "ms": 200
}

@apiParam {Int} ms wait milliseconds.
"""
API_WAIT					= "wait"
WAIT_MS						= "ms"


"""
@apiGroup startTailing
@api {SushiJSON} startTailing:{JSON} start tailing the target file and run reactor.
@apiExample [example]
startTailing: {
    "identity": "startTailing",
    "path": "SUBLIMESOCKET_PATH:tests/testResources/runShellTarget.txt",
    "reactors": [
        {
            "showAtLog<-source": {
                "format": "tailed, [source]"
            }
        }
    ],
    "selectors": [
    ]
}

@apiParam {String} identity identifier of this tail process.(only defined. no usage yet.)
@apiParam {String} path the target file path. must be full-path.
@apiParam {JSON} reactors run when tailed-data incoming. "source" param will be injected.
@apiParam {JSON} selectors run after defined.

@apiSuccess {String} path the tail-started file path.
"""
API_STARTTAILING			= "startTailing"
STARTTAILING_IDENTITY		= "identity"
STARTTAILING_PATH			= "path"
STARTTAILING_REACTORS		= "reactors"
STARTTAILING_SOURCE			= "source"
STARTTAILING_INJECTIONS		= [STARTTAILING_PATH]


"""
@apiGroup countUp
@api {SushiJSON} countUp:{JSON} count up mechanism. if the label was already defined, countup it.
@apiExample [example]
countUp: {
    "label": "countIdentity",
    "default": 0
}

@apiParam {String} label identifier of the count machine. countup if same label is defined.
@apiParam {Int} default the first value of the count.

@apiSuccess {String} label inputted label.
@apiSuccess {Int} count the count after define/countup.
"""
API_COUNTUP					= "countUp"
COUNTUP_LABEL				= "label"
COUNTUP_DEFAULT				= "default"
COUNTUP_COUNT				= "count"
COUNTUP_INJECTIONS			= [COUNTUP_LABEL, COUNTUP_COUNT]


"""
@apiGroup resetCounts
@api {SushiJSON} resetCounts:{JSON} reset the labeled count.
@apiExample [example]
resetCounts: {
    "label": "countIdentity"
}

@apiParam {String(Optional)} label identifier of the count machine. countup if same label is defined. reset all if not specified.

@apiSuccess {Strings} resetted the list of labels which was resetted.
"""
API_RESETCOUNTS				= "resetCounts"
RESETCOUNTS_LABEL			= "label"
RESETCOUNTS_RESETTED		= "resetted"
RESETCOUNTS_INJECTIONS		= [RESETCOUNTS_RESETTED]


"""
@apiGroup runSushiJSON
@api {SushiJSON} runSushiJSON:{JSON} run SushiJSON formatted string as APISuites.
@apiExample [example]
runSushiJSON: {
    "path": "SUBLIMESOCKET_PATH:tests/testResources/sample_SushiJSON.txt",
    "selectors": [
        {
            "showAtLog<-logs": {
                "format": "runSetting logs:[logs]"
            }
        }
    ]
}

@apiParam {String(Optional)} path the path of SushiJSON descripted file.
@apiParam {String(Optional)} data the strings of SushiJSON.

@apiSuccess {Strings} logs the list of the SushiJSON's result = "showAtLog" message which was running inside path / data.
"""
API_RUNSUSHIJSON			= "runSushiJSON"
RUNSUSHIJSON_PATH			= "path"
RUNSUSHIJSON_DATA			= "data"
RUNSUSHIJSON_LOGS			= "logs"
RUNSUSHIJSON_INJECTIONS		= [RUNSUSHIJSON_LOGS]
RUNSUSHIJSON_PREFIX_SUBLIMESOCKET_PATH = "SUBLIMESOCKET_PATH:"


"""
@apiGroup runSelectorsWithInjects
@api {SushiJSON} runSelectorsWithInjects:{JSON} run "selectos" with specific injection of keys & values.
@apiExample [example]
runSelectorsWithInjects: {
	"injects": {
		"key1": "key2"
	},
    "selectors": [
        {
            "showAtLog<-key2": {
                "format": "injected [key2]"
            }
        }
    ]
}

@apiParam {JSON} injects the pair of before-after key name transform.
@apiParam {JSON} selectors which run with injects all keys & values.

@ap@apiSuccess {Everything} keys_and_values this api injects all keys and values to selectors.
"""
API_RUNSELECTORSWITHINJECTS = "runSelectorsWithInjects"
RUNSELECTORSWITHINJECTS_SELECTORS	= "selectors"
RUNSELECTORSWITHINJECTS_INJECTS		= "injects"


"""
@apiGroup changeIdentity
@api {SushiJSON} changeIdentity:{JSON} chamge identity of WebSocket client.(not useful for the other protocols.)
@apiExample [example]
changeIdentity: {
    "from": "sublimesockettest",
    "to": "test",
    "injects": {
        "from": "from",
        "to": "to"
    },
    "selectors": [
        {
            "showAtLog<-from, to": {
                "format": "[from] becomes [to]."
            }
        }
    ]
}

@apiParam {String} from specify the target of rename.
@apiParam {String} to value for rename.

@apiSuccess {String} from the identity before changed.
@apiSuccess {String} to the identity after changed.
"""
API_CHANGEIDENTITY			= "changeIdentity"
CHANGEIDENTITY_FROM			= "from"
CHANGEIDENTITY_TO			= "to"
CHANGEIDENTITY_INJECTIONS	= [CHANGEIDENTITY_FROM, CHANGEIDENTITY_TO]


"""
@apiGroup tearDown
@api {SushiJSON} tearDown:{} teardown the SublimeSocket Server itself.
@apiExample [example]
tearDown: {}
"""
API_TEARDOWN				= "tearDown"


"""
@apiGroup createBuffer
@api {SushiJSON} createBuffer:{JSON} create the named buffer.
@apiExample [example]
createBuffer: {
    "name": "test",
    "selectors": [
        {
            "showAtLog<-name": {
                "format": "[name] created."
            }
        }
    ]
}

@apiParam {String} name set the name of buffer.
@apiParam {String(Optional)} contents the contents of buffer. create, named then insert contents to the buffer.

@apiSuccess {Strings} name the name of buffer.
"""
API_CREATEBUFFER			= "createBuffer"
CREATEBUFFER_NAME			= "name"
CREATEBUFFER_CONTENTS		= "contents"
CREATEBUFFER_INJECTIONS		= [CREATEBUFFER_NAME]



"""
@apiGroup openFile
@api {SushiJSON} openFile:{JSON} open the file which is exist.
@apiExample [example]
openFile: {
    "path": "SUBLIMESOCKET_PATH:tests/testResources/sample.txt",
    "selectors": [
        {
            "showAtLog<-name": {
                "format": "opened [name]"
            }
        }
    ]
}

@apiParam {String} path open file if exist. or not, do nothing.

@apiSuccess {String} name the name = last path part of the file.
@apiSuccess {String} path the full path of the file.
"""
API_OPENFILE				= "openFile"
OPENFILE_PATH				= "path"
OPENFILE_NAME				= "name"
OPENFILE_INJECTIONS			= [OPENFILE_PATH, OPENFILE_NAME]



"""
@apiGroup closeFile
@api {SushiJSON} closeFile:{JSON} open the file which is exist.
@apiExample [example]
closeFile: {
    "name": "sample.txt"
}

@apiParam {String} name the target file's last part of file path or fullpath.

@apiSuccess {String} name the name = last path part of the closed file.
@apiSuccess {String} path the full path of the closed file.
"""
API_CLOSEFILE				= "closeFile"
CLOSEFILE_PATH				= "path"
CLOSEFILE_NAME				= "name"
CLOSEFILE_INJECTIONS		= [CLOSEFILE_PATH, CLOSEFILE_NAME]


"""
@apiGroup closeAllFiles
@api {SushiJSON} closeAllFiles:{JSON} close all files or close excepted-specific named files.
@apiExample [example]
closeAllFiles: {
    "dryrun": true,
    "selectors": [
        {
            "showAtLog<-closeds": {
                "format": "[closeds]"
            }
        }
    ]
}
@apiParam {String(Optional)} excepts the list of file names which do not want to close.
@apiParam {Bool(Optional)} dryrun the flag for debug.

@apiSuccess {Strings} closeds the list of closed file's full path.
"""
API_CLOSEALLFILES			= "closeAllFiles"
CLOSEALLFILES_EXCEPTS		= "excepts"
CLOSEFILE_DRYRUN			= "dryrun"
CLOSEALLFILES_CLOSEDS		= "closeds"
CLOSEALLFILES_INJECTIONS	= [CLOSEALLFILES_CLOSEDS]


"""
@apiGroup closeAllBuffer
@api {SushiJSON} closeAllBuffer:{JSON} close all buffers.
@apiExample [example]
closeAllBuffer: {
    "injects": {
        "closeds": "message"
    },
    "selectors": [
        {
            "showAtLog<-message": {}
        }
    ]
}

@apiSuccess {Strings} closeds the list of closed buffer's names.
"""
API_CLOSEALLBUFFER			= "closeAllBuffer"
CLOSEALLBUFFER_CLOSEDS		= "closeds"
CLOSEALLBUFFER_INJECTIONS	= [CLOSEALLBUFFER_CLOSEDS]


"""
@apiGroup setEventReactor
@api {SushiJSON} setEventReactor:{JSON} set self-defined event reactor. run when the reactive-event/foundation-event appeared.
@apiExample [example]
setEventReactor: {
    "react": "event_accept_event",// you can define it. must starts with "event_" prefix.
    "reactors": [
        {
            "showAtLog": {
                "message": "hereComes"
            }
        },
        {
            "showAtLog<-messageFromEventEmit": {
                "format": "from [messageFromEventEmit]"
            }
        }
    ]
}->eventEmit: {
    "messageFromEventEmit": "the message from eventEmit"
}

@apiExample [example of receive foundation event]
setEventReactor: {
    "react": "ss_f_noViewFound",
    "reactors": [
        {
            "showAtLog<-name": {
                "message": "no view found",
                "format": "view [name] not found."
            }
        }
    ]
}

@apiParam {String} react target event name.
@apiParam {JSON} reactors run when target-event/foundation-event appeared.
@apiParam {Int(Optional)} delay milliseconds. delay ignore running reactors, when the event appeared multitimes in this delay.

@apiSuccess {Everything} keys_and_values run when this event appeared. run with caller API's injects.
"""
API_SETEVENTREACTOR			= "setEventReactor"


"""
@apiGroup setViewReactor
@api {SushiJSON} setViewReactor:{JSON} set defined view-event reactor. run when the event appeared.
@apiExample [example]
setViewReactor: {
    "react": "on_post_save",
    "reactors": [
        {
           "showAtLog<-name": {
                "format": "name is [name]"
            }
        }
    ]
}

@apiExample [view-events]
on_new
on_clone
on_close
on_load
on_modified

on_query_completions

on_pre_save
on_post_save
on_selection_modified

ss_on_selection_modified_by_setselection
ss_v_decreased
ss_v_increased

@apiParam {String} react target event name.
@apiParam {JSON} reactors run when target-event/foundation-event appeared.
@apiParam {Int(Optional)} delay milliseconds. delay ignore running reactors, when the event appeared multitimes in this delay.

@apiSuccess {JSON} reactors reactors block.
@apiSuccess {Int} delay 0 or inputted value.

@apiExample [when reacted]
@apiSuccess {ViewInstance} view the instance of view.(not good to use. use "name", "path" to specify view.)
"view"
"path"
"name"
"selecteds"
"isExist"
"identity"
"""
API_SETVIEWREACTOR			= "setViewReactor"

# must selective
SETREACTOR_REACT			= "react"
SETREACTOR_REACTORS			= "reactors"
SETREACTOR_DELAY			= "delay"
SETREACTOR_ACCEPTS			= "accepts"
SETREACTOR_INJECTIONS		= [SETREACTOR_REACT, SETREACTOR_DELAY]

REACTOR_VIEWKEY_VIEWSELF	= "view"
REACTOR_VIEWKEY_PATH		= "path"
REACTOR_VIEWKEY_NAME		= "name"
REACTOR_VIEWKEY_VNAME		= "vname"
REACTOR_VIEWKEY_SELECTEDS	= "selecteds"
REACTOR_VIEWKEY_ISEXIST		= "isExist"
REACTOR_VIEWKEY_EMITIDENTITY= "identity"
REACTOR_VIEWKEY_INJECTIONS	= [REACTOR_VIEWKEY_EMITIDENTITY, REACTOR_VIEWKEY_VIEWSELF, REACTOR_VIEWKEY_SELECTEDS, REACTOR_VIEWKEY_PATH, REACTOR_VIEWKEY_NAME, REACTOR_VIEWKEY_ISEXIST]

REACTORTYPE_EVENT			= "event"
REACTORTYPE_VIEW			= "view"


API_RESETREACTORS			= "resetReactors"
RESETREACTORS_DELETEDS		= "deleteds"
RESETREACTORS_INJECTIONS	= [RESETREACTORS_DELETEDS]


API_VIEWEMIT				= "viewEmit"
VIEWEMIT_NAME				= "name"
VIEWEMIT_VIEW				= "view"
VIEWEMIT_DELAY				= "delay"
VIEWEMIT_VIEWSELF			= "view"
VIEWEMIT_BODY				= "body"
VIEWEMIT_PATH				= "path"
VIEWEMIT_MODIFIEDPATH		= "modifiedpath"
VIEWEMIT_ROWCOL				= "rowcol"
VIEWEMIT_INJECTIONS 		= [VIEWEMIT_BODY, VIEWEMIT_PATH, VIEWEMIT_NAME, VIEWEMIT_MODIFIEDPATH, VIEWEMIT_ROWCOL]


API_EVENTEMIT				= "eventEmit"
EVENTEMIT_EVENT				= "event"
EVENTEMIT_INJECTIONS		= [EVENTEMIT_EVENT]


REACTIVE_PREFIX_USERDEFINED_EVENT	= "event_"
REACTIVE_PREFIX_SUBLIMESOCKET_EVENT = "ss_f_"
REACTIVE_PREFIXIES					= [REACTIVE_PREFIX_USERDEFINED_EVENT, REACTIVE_PREFIX_SUBLIMESOCKET_EVENT]

REACTIVE_FOUNDATION_EVENT			= [SS_FOUNDATION_NOVIEWFOUND]
REACTIVE_CURRENT_COMPLETINGS		= "currentcompletings"




# view series

API_MODIFYVIEW				= "modifyView"
MODIFYVIEW_VIEW				= "view"
MODIFYVIEW_NAME				= "name"
MODIFYVIEW_PATH				= "path"
MODIFYVIEW_ADD				= "add"
MODIFYVIEW_TO				= "to"
MODIFYVIEW_LINE				= "line"
MODIFYVIEW_REDUCE			= "reduce"
MODIFYVIEW_INJECTIONS		= [MODIFYVIEW_PATH, MODIFYVIEW_NAME, MODIFYVIEW_LINE, MODIFYVIEW_TO]


API_SETSELECTION			= "setSelection"
SETSELECTION_VIEW			= "view"
SETSELECTION_NAME			= "name"
SETSELECTION_PATH			= "path"
SETSELECTION_SELECTIONS		= "selections"
SETSELECTION_FROM			= "from"
SETSELECTION_TO				= "to"
SETSELECTION_SELECTEDS		= "selecteds"
SETSELECTION_INJECTIONS		= [SETSELECTION_PATH, SETSELECTION_NAME, SETSELECTION_SELECTEDS]
SS_VIEW_ON_SELECTION_MODIFIED_BY_SETSELECTION = "ss_on_selection_modified_by_setselection"


API_CLEARSELECTION			= "clearSelection"
CLEARSELECTION_VIEW			= "view"
CLEARSELECTION_NAME			= "name"
CLEARSELECTION_PATH			= "path"
CLEARSELECTION_CLEARDS		= "cleards"
CLEARSELECTION_INJECTIONS	= [CLEARSELECTION_PATH, CLEARSELECTION_NAME, CLEARSELECTION_CLEARDS]


API_DEFINEFILTER				= "defineFilter"
DEFINEFILTER_FILTERS			= "filters"
DEFINEFILTER_PATTERNS			= "patterns"
DEFINEFILTER_NAME 				= "name"
DEFINEFILTER_DOTALL				= "dotall"
DEFINEFILTER_COMMENT			= "comments"
DEFINEFILTER_INJECTIONS			= [DEFINEFILTER_NAME, DEFINEFILTER_PATTERNS]


API_FILTERING					= "filtering"
FILTERING_NAME					= "name"
FILTERING_SOURCE				= "source"
FILTERING_DEBUG					= "debug"


API_SELECTEDREGIONS				= "selectedRegions"
SELECTEDREGIONS_SELECTEDS		= "selecteds"
SELECTEDREGIONS_ISEXACTLY		= "isexactly"
SELECTEDREGIONS_ISSAMELINE		= "issameline"
SELECTEDREGIONS_VIEW			= "view"
SELECTEDREGIONS_NAME			= "name"
SELECTEDREGIONS_PATH			= "path"
SELECTEDREGIONS_CROSSED			= "crossed"
SELECTEDREGIONS_ONLYONE			= "onlyone"
SELECTEDREGIONS_LINE			= "line"
SELECTEDREGIONS_FROM			= "from"
SELECTEDREGIONS_TO				= "to"
SELECTEDREGIONS_MESSAGES		= "messages"
SELECTEDREGIONS_INJECTIONS 		= [SELECTEDREGIONS_PATH, SELECTEDREGIONS_NAME, SELECTEDREGIONS_CROSSED, SELECTEDREGIONS_LINE, SELECTEDREGIONS_FROM, SELECTEDREGIONS_TO, SELECTEDREGIONS_MESSAGES]


API_COLLECTVIEWS				= "collectViews"
COLLECTVIEWS_COLLECTEDS			= "collecteds"
COLLECTVIEWS_INJECTIONS 		= [COLLECTVIEWS_COLLECTEDS]


API_APPENDREGION			= "appendRegion"
APPENDREGION_NAME			= "name"
APPENDREGION_VIEW			= "view"
APPENDREGION_PATH			= "path"
APPENDREGION_IDENTITY		= "identity"
APPENDREGION_LINE			= "line"
APPENDREGION_FROM			= "from"
APPENDREGION_TO				= "to"
APPENDREGION_MESSAGE		= "message"
APPENDREGION_CONDITION 		= "condition"
APPENDREGION_INJECTIONS		= [APPENDREGION_PATH, APPENDREGION_NAME, APPENDREGION_IDENTITY, APPENDREGION_LINE, APPENDREGION_FROM, APPENDREGION_TO, APPENDREGION_MESSAGE, APPENDREGION_CONDITION]


API_ERASEALLREGIONS			= "eraseAllRegions"
ERASEALLREGIONS_NAME		= "name"
ERASEALLREGIONS_DELETES		= "deletes"
ERASEALLREGIONS_INJECTIONS	= [ERASEALLREGIONS_DELETES]



# other series

API_RUNSHELL					= "runShell"
RUNSHELL_MAIN					= "main"
RUNSHELL_DELAY					= "delay"
RUNSHELL_DEBUG					= "debug"
RUNSHELL_LIST_IGNORES 			= [RUNSHELL_MAIN, RUNSHELL_DELAY, RUNSHELL_DEBUG]
RUNSHELL_REPLACE_SPACE			= "_"
RUNSHELL_REPLACE_RIGHTBRACE 	= ""
RUNSHELL_REPLACE_LEFTBRACE		= ""
RUNSHELL_REPLACE_SINGLEQUOTE 	= ""
RUNSHELL_REPLACE_At_s_At_s_At	= " "


API_BROADCASTMESSAGE		= "broadcastMessage"
BROADCASTMESSAGE_TARGETS	= "targets"
BROADCASTMESSAGE_FORMAT		= "format"
BROADCASTMESSAGE_MESSAGE	= "message"
BROADCASTMESSAGE_INJECTIONS	= [BROADCASTMESSAGE_TARGETS, BROADCASTMESSAGE_MESSAGE]


API_MONOCASTMESSAGE			= "monocastMessage"
MONOCASTMESSAGE_TARGET		= "target"
MONOCASTMESSAGE_FORMAT		= "format"
MONOCASTMESSAGE_MESSAGE		= "message"
MONOCASTMESSAGE_INJECTIONS	= [MONOCASTMESSAGE_TARGET, MONOCASTMESSAGE_MESSAGE]


API_SHOWSTATUSMESSAGE		= "showStatusMessage"
SHOWSTATUSMESSAGE_MESSAGE	= "message"
SHOWSTATUSMESSAGE_DEBUG		= "debug"


API_SHOWATLOG				= "showAtLog"
LOG_FORMAT					= "format"
LOG_MESSAGE					= "message"
LOG_prefix					= "ss:"


API_SHOWDIALOG				= "showDialog"
SHOWDIALOG_FORMAT			= "format"
SHOWDIALOG_MESSAGE			= "message"
SHOWDIALOG_INJECTIONS		= [SHOWDIALOG_MESSAGE]


API_SHOWTOOLTIP				= "showToolTip"
SHOWTOOLTIP_VIEW			= "view"
SHOWTOOLTIP_NAME			= "name"
SHOWTOOLTIP_PATH			= "path"
SHOWTOOLTIP_ONSELECTED		= "onselected"
SHOWTOOLTIP_ONCANCELLED		= "oncancelled"
SHOWTOOLTIP_FINALLY			= "finally"
SHOWTOOLTIP_SELECTEDTITLE	= "selectedtitle"
SHOWTOOLTIP_TITLES			= "titles"
SHOWTOOLTIP_INJECTIONS		= [SHOWTOOLTIP_PATH, SHOWTOOLTIP_NAME, SHOWTOOLTIP_TITLES, SHOWTOOLTIP_SELECTEDTITLE]


API_SCROLLTO				= "scrollTo"
SCROLLTO_VIEW				= "view"
SCROLLTO_NAME				= "name"
SCROLLTO_LINE				= "line"
SCROLLTO_COUNT				= "count"
SCROLLTO_INJECTIONS			= []


API_TRANSFORM				= "transform"
TRANSFORM_PATH				= "transformerpath"
TRANSFORM_CODE				= "code"
TRANSFORM_DEBUG				= "debug"


API_NOTIFY					= "notify"
NOTIFY_TITLE				= "title"
NOTIFY_MESSAGE				= "message"
NOTIFY_DEBUG				= "debug"
NOTIFY_INJECTIONS			= [NOTIFY_TITLE, NOTIFY_MESSAGE]


API_GETALLFILEPATH			= "getAllFilePath"
GETALLFILEPATH_ANCHOR		= "anchor"
GETALLFILEPATH_LIMIT		= "limit"
GETALLFILEPATH_BASEDIR		= "basedir"
GETALLFILEPATH_PATHS		= "paths"
GETALLFILEPATH_FULLPATHS	= "fullpaths"
GETALLFILEPATH_INJECTIONS	= [GETALLFILEPATH_BASEDIR, GETALLFILEPATH_PATHS, GETALLFILEPATH_FULLPATHS]

	
API_READFILE				= "readFile"
READFILE_ORIGINALPATH		= "originalpath"
READFILE_PATH				= "path"
READFILE_DATA				= "data"
READFILE_INJECTIONS			= [READFILE_ORIGINALPATH, READFILE_PATH, READFILE_DATA]

	
API_CANCELCOMPLETION		= "cancelCompletion"
CANCELCOMPLETION_VIEW		= "view"
CANCELCOMPLETION_NAME		= "name"
CANCELCOMPLETION_INJECTIONS = []

	
API_RUNCOMPLETION			= "runCompletion"
RUNCOMPLETION_VIEW			= "view"
RUNCOMPLETION_PATH			= "path"
RUNCOMPLETION_NAME			= "name"
RUNCOMPLETION_COMPLETIONS	= "completion"
RUNCOMPLETION_FORMATHEAD	= "formathead"
RUNCOMPLETION_FORMATTAIL	= "formattail"
RUNCOMPLETION_ID			= "id"
RUNCOMPLETION_INJECTIONS	= [RUNCOMPLETION_PATH, RUNCOMPLETION_NAME]


API_FORCELYSAVE				= "forcelySave"
FORCELYSAVE_VIEW			= "view"
FORCELYSAVE_PATH			= "path"
FORCELYSAVE_NAME			= "name"
FORCELYSAVE_INJECTIONS		= [FORCELYSAVE_PATH, FORCELYSAVE_NAME]


API_SETSUBLIMESOCKETWINDOWBASEPATH = "setSublimeSocketWindowBasePath"
SETSUBLIMESOCKETWINDOWBASEPATH_BASEPATH		= "basepath"
SETSUBLIMESOCKETWINDOWBASEPATH_BASENAME		= "basename"
SETSUBLIMESOCKETWINDOWBASEPATH_INJECTIONS	= [SETSUBLIMESOCKETWINDOWBASEPATH_BASEPATH, SETSUBLIMESOCKETWINDOWBASEPATH_BASENAME]


# definition of sublime's view events
REACTABLE_VIEW_ON_NEW				= "on_new"
REACTABLE_VIEW_ON_CLONE				= "on_clone"
REACTABLE_VIEW_ON_CLOSE				= "on_close"
REACTABLE_VIEW_ON_LOAD				= "on_load"
REACTABLE_VIEW_ON_MODIFIED			= "on_modified"
REACTABLE_VIEW_ON_QUERY_COMPLETIONS	= "on_query_completions"
REACTABLE_VIEW_ON_PRE_SAVE			= "on_pre_save"
REACTABLE_VIEW_ON_POST_SAVE			= "on_post_save"
REACTABLE_VIEW_ON_SELECTION_MODIFIED= "on_selection_modified"
REACTABLE_VIEW_SS_V_DECREASED		= "ss_v_decreased"
REACTABLE_VIEW_SS_V_INCREASED		= "ss_v_increased"


VIEW_EVENTS_RENEW			= [REACTABLE_VIEW_ON_POST_SAVE, REACTABLE_VIEW_ON_CLONE, REACTABLE_VIEW_ON_LOAD, SS_EVENT_COLLECT, SS_EVENT_LOADING, SS_EVENT_RENAMED] #list of acceptable-view renew event names.
VIEW_EVENTS_DEL				= [REACTABLE_VIEW_ON_CLOSE] #list of acceptable-view del event names.




