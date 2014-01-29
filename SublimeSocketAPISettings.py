import os



#SublimeSocket API 


SS_HOST_REPLACE					= "SUBLIMESOCKET_HOST"
SS_PORT_REPLACE					= "SUBLIMESOCKET_PORT"
SS_IDENTITY_REPLACE				= "SUBLIMESOCKET_PAGEIDENTITY"
SS_VERSION_REPLACE				= "SUBLIMESOCKET_VERSION"
SS_TESTSUITE_FILEPATH_REPLACE		= "SUBLIMESOCKET_TESTSUITE_FILEPATH"


HTML_REPLACEABLE_KEYS = [SS_HOST_REPLACE, SS_PORT_REPLACE, SS_IDENTITY_REPLACE, SS_VERSION_REPLACE, SS_TESTSUITE_FILEPATH_REPLACE]

# get folder name of this plugin.
MY_PLUGIN_PATHNAME = os.path.split(os.path.dirname(os.path.realpath(__file__)))[1]


WEBSOCKET_SERVER = "WebSocketServer"
TRANSFER_METHODS = [WEBSOCKET_SERVER]

# KVS

DICT_VIEWS				= "DICT_VIEWS"
VIEW_SELF				= "view"
VIEW_PATH				= "path"
VIEW_ID					= "viewId"
VIEW_BUFFERID			= "bufferId"
VIEW_BASENAME			= "basename"
VIEW_VNAME				= "vname"
VIEW_SELECTED			= "selected"
VIEW_ISEXIST			= "isExist"


DICT_COMPLETIONS		= "DICT_COMPLETIONS"


DICT_FILTERS		= "DICT_FILTERS"


DICT_REACTORS		= "DICT_REACTORS"


DICT_REACTORSLOG	= "DICT_REACTORS_LOG"
REACTORSLOG_LATEST	= "latest"


DICT_REGIONS		= "DICT_REGIONS"
REGION_IDENTITY		= "identity"
REGION_ISSELECTING	= "isSelecting"
REGION_FROM			= "from"
REGION_TO			= "to"
REGION_LINE			= "line"
REGION_MESSAGES		= "messages"
REGIONDATA_MESSAGE	= "message"


# region identifier prefix
REGION_UUID_PREFIX			= "ss_"



# API

### COMMAND		=		COMMAND_NAME : JSON_EXPRESSION
### COMMANDS	=		COMMAND_NAME : JSON_EXPRESSION -> COMMAND_NAME : JSON_EXPRESSION -> ...
### COMMANDS	=		COMMAND_NAME + COMMAND_NAME : JSON_EXPRESSION -> COMMAND_NAME + COMMAND_NAME + COMMAND_NAME : JSON_EXPRESSION -> ...

API_PREFIX					= "sublimesocket"

API_PREFIX_SUB				= "ss"
API_DEFINE_DELIM			= "@"	# sublimesocket@commandA:{}->commandB:{}->commandC:[]->
API_CONCAT_DELIM			= "->"	# concat commands. every commands run in sequential.
API_COMMAND_PARAMS_DELIM	= ":"	# only first ":" will be evaluated as delimiter / each commnand.

API_COMMENT_DELIM			= "/"	# comment expression in API. ss@COMMENT/API...

API_TESTCASE_DELIM			= "test>"	# test commands delim.


COMMAND_KEYWORD_INJECT		= "<-"
COMMAND_KEYWORD_DELIM		= ","


API_VERSION		= "1.4.0"
SOCKET_VERSION	= 3	# for Sublime Text 3


# SublimeSocket internal event definition
SS_EVENT_COLLECT	= "ss_collect"
SS_EVENT_LOADING	= "ss_loading"
SS_EVENT_RENAMED	= "ss_renamed"



SS_FOUNDATION_NOVIEWFOUND	= "ss_f_noViewFound"
NOVIEWFOUND_TARGET			= "target"
NOVIEWFOUND_PATH			= "path"
NOVIEWFOUND_LINE			= "line"
NOVIEWFOUND_MESSAGE			= "message"
NOVIEWFOUND_CONDITION		= "condition"

SS_FOUNDATION_VIEWEMIT		= "ss_f_viewemit"



# view events
REACTABLE_EVENT_ON_QUERY_COMPLETIONS = "on_query_completions"


# internal APIs/
API_I_SHOWSTATUSMESSAGE		= "showStatusMessage"
SHOWSTATUSMESSAGE_MESSAGE	= "message"


# /internal APIs



# public APIs
API_VERSIONVERIFY			= "versionVerify"
VERSIONVERIFY_SOCKETVERSION	= "socketVersion"
VERSIONVERIFY_APIVERSION	= "apiVersion"
VERSIONVERIFY_DRYRUN		= "dryrun"


VERIFICATION_CODE_VERIFIED_CLIENT_UPDATE			= 2
VERIFICATION_CODE_VERIFIED							= 1
VERIFICATION_CODE_REFUSED_DIFFERENT_SUBLIMESOCKET	= 0
VERIFICATION_CODE_REFUSED_SUBLIMESOCKET_UPDATE		= -1
VERIFICATION_CODE_REFUSED_CLIENT_UPDATE				= -2


API_RUNTESTS		= "runTests"
RUNTESTS_PATH		= "path"


API_SETTESTBEFOREAFTER	= "setTestBeforeAfter"
SETTESTBEFOREAFTER_BEFORESELECTORS = "beforeselectors"
SETTESTBEFOREAFTER_AFTERSELECTORS = "afterselectors"
SETTESTBEFOREAFTER_SELECTORS = "selectors"


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


API_COUNTUP		= "countUp"
COUNTUP_LABEL	= "label"
COUNTUP_DEFAULT	= "default"


API_RESETCOUNTS	= "resetCounts"


API_RUNSETTING		= "runSetting"
RUNSETTING_FILEPATH	= "path"
RUNSETTING_PREFIX_SUBLIMESOCKET_PATH = "SUBLIMESOCKET_PATH:"

API_INPUTIDENTITY	= "inputIdentity"
IDENTITY_ID			= "id"

API_TEARDOWN		=	"tearDown"

API_CREATEBUFFER	= "createBuffer"
CREATEBUFFER_NAME	= "name"
CREATEBUFFER_CONTENTS = "contents"


API_OPENFILE		= "openFile"
OPENFILE_PATH		= "path"

API_CLOSEFILE		= "closeFile"
CLOSEFILE_NAME		= "name"

API_CLOSEALLBUFFER	= "closeAllBuffer"

API_SETEVENTREACTOR	= "setEventReactor"
API_SETVIEWREACTOR	= "setViewReactor"

REACTOR_TARGET		= "target"
REACTOR_REACT		= "react"
REACTOR_SELECTORS	= "selectors"
REACTOR_DELAY		= "delay"
REACTOR_INJECT		= "inject"

REACTOR_VIEWKEY_VIEWSELF	= "view"
REACTOR_VIEWKEY_ID			= "viewId"
REACTOR_VIEWKEY_BUFFERID	= "bufferId"
REACTOR_VIEWKEY_PATH		= "path"
REACTOR_VIEWKEY_BASENAME	= "basename"
REACTOR_VIEWKEY_VNAME		= "vname"
REACTOR_VIEWKEY_SELECTED	= "selected"
REACTOR_VIEWKEY_ISEXIST		= "isExist"
REACTOR_VIEWKEY_EMITIDENTITY	= "identity"
REACTOR_VIEWKEY_INJECTIONKEYS = [REACTOR_VIEWKEY_EMITIDENTITY, REACTOR_VIEWKEY_VIEWSELF, REACTOR_VIEWKEY_SELECTED, REACTOR_VIEWKEY_PATH, REACTOR_VIEWKEY_ISEXIST]


REACTORTYPE_EVENT	= "event"
REACTORTYPE_VIEW	= "view"


API_RESETREACTORS	= "resetReactors"


API_VIEWEMIT		= "viewEmit"
VIEWEMIT_NAME		= "name"
VIEWEMIT_VIEW		= "view"
VIEWEMIT_IDENTITY	= "identity"
VIEWEMIT_DELAY		= "delay"
VIEWEMIT_SELECTORS	= "selectors"

VIEWEMIT_VIEWSELF	= "view"
VIEWEMIT_BODY		= "body"
VIEWEMIT_PATH		= "path"
VIEWEMIT_ROWCOL		= "rowcol"

VIEWEMIT_INJECT		= "inject"
VIEWEMIT_INJECTIONKEYS = [VIEWEMIT_VIEWSELF, VIEWEMIT_BODY, VIEWEMIT_PATH, VIEWEMIT_ROWCOL, VIEWEMIT_IDENTITY]



API_MODIFYVIEW		= "modifyView"
MODIFYVIEW_VIEW		= "view"
MODIFYVIEW_NAME		= "name"
MODIFYVIEW_ADD		= "add"
MODIFYVIEW_REDUCE	= "reduce"

API_SETSELECTION	= "setSelection"
SETSELECTION_VIEW	= "view"
SETSELECTION_NAME	= "name"
SETSELECTION_FROM	= "from"
SETSELECTION_TO		= "to"
SS_VIEW_ON_SELECTION_MODIFIED_BY_SETSELECTION = "ss_on_selection_modified_by_setselection"

API_CLEARSELECTION	= "clearSelection"
CLEARSELECTION_VIEW	= "view"
CLEARSELECTION_NAME	= "name"

REACTIVE_PREFIX_USERDEFINED_EVENT	= "event_"
REACTIVE_FOUNDATION_EVENT = [SS_FOUNDATION_NOVIEWFOUND]
REACTIVE_CURRENT_COMPLETINGS = "currentcompletings"

API_DEFINEFILTER				= "defineFilter"
DEFINEFILTER_PATTERNS			= "patterns"
DEFINEFILTER_NAME 				= "name"
DEFINEFILTER_SELECTORS			= "selectors"
DEFINEFILTER_DOTALL				= "dotall"
DEFINEFILTER_COMMENT			= "comments"
		
API_FILTERING					= "filtering"
FILTERING_NAME					= "name"
FILTERING_SOURCE				= "source"
FILTERING_DEBUG					= "debug"

API_SELECTEDREGIONS				= "selectedRegions"
API_SELECTEDREGIONSFOREACH		= "selectedRegionsForeach"
SELECTEDREGIONS_VIEW			= "view"
SELECTEDREGIONS_PATH			= "path"
SELECTEDREGIONS_TARGET			= "target"
SELECTEDREGIONS_SELECTED		= "selected"
SELECTEDREGIONS_SELECTORS		= "selectors"
SELECTEDREGIONS_ONLYONE			= "onlyone"
SELECTEDREGIONS_REGIONDATAS		= "regionDatas"
SELECTEDREGIONS_INJECT			= "inject"
SELECTEDREGIONS_INJECTIONKEYS 	= [SELECTEDREGIONS_REGIONDATAS, SELECTEDREGIONS_VIEW, SELECTEDREGIONS_PATH, SELECTEDREGIONS_TARGET, SELECTEDREGIONS_SELECTED]


API_COLLECTVIEWS				= "collectViews"

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


API_BROADCASTMESSAGE	= "broadcastMessage"
API_MONOCASTMESSAGE		= "monocastMessage"
OUTPUT_TARGET			= "target"
OUTPUT_FORMAT			= "format"
OUTPUT_MESSAGE			= "message"

API_SHOWATLOG			= "showAtLog"
LOG_FORMAT				= "format"
LOG_MESSAGE				= "message"
LOG_prefix				= "ss:"

API_SHOWDIALOG			= "showDialog"
SHOWDIALOG_FORMAT		= "format"
SHOWDIALOG_MESSAGE		= "message"

API_SHOWTOOLTIP				= "showToolTip"
SHOWTOOLTIP_VIEW			= "view"
SHOWTOOLTIP_NAME			= "name"
SHOWTOOLTIP_ONCANCELLED		= "oncancelled"
SHOWTOOLTIP_ONSELECTED		= "onselected"
SHOWTOOLTIP_FINALLY			= "finally"
SHOWTOOLTIP_INJECT			= "inject"
SHOWTOOLTIP_INJECTIONKEYS	= [SHOWTOOLTIP_VIEW]

SUBAPI_TRANSFORMTOTOOLTIP	= "transformToToolTip"


API_APPENDREGION		= "appendRegion"
APPENDREGION_NAME		= "name"
APPENDREGION_VIEW		= "view"
APPENDREGION_LINE		= "line"
APPENDREGION_MESSAGE	= "message"
APPENDREGION_CONDITION 	= "condition"

API_ERASEALLREGION		= "eraseAllRegion"
ERASEALLREGION_NAME		= "name"

API_RUNWITHBUFFER		= "runWithBuffer"
RUNWITHBUFFER_VIEW		= "view"

API_NOTIFY				= "notify"
NOTIFY_TITLE			= "title"
NOTIFY_MESSAGE			= "message"
NOTIFY_DEBUG			= "debug"

API_GETALLFILEPATH		= "getAllFilePath"
GETALLFILEPATH_PATHS	= "paths"
GETALLFILEPATH_ANCHOR	= "anchor"
GETALLFILEPATH_LIMIT	= "limit"
GETALLFILEPATH_HEADER	= "header"
GETALLFILEPATH_FOOTER	= "footer"
GETALLFILEPATH_DELIM	= "delim"

API_READFILEDATA		= "readFileData"
READFILEDATA_PATH		= "path"
READFILEDATA_DATA		= "data"

API_EVENTEMIT			= "eventEmit"
EVENTEMIT_TARGET		= "target"
EVENTEMIT_EVENT			= "event"


API_CANCELCOMPLETION	= "cancelCompletion"
CANCELCOMPLETION_VIEW	= "view"
CANCELCOMPLETION_NAME	= "name"


API_RUNCOMPLETION		= "runCompletion"
RUNCOMPLETION_VIEW		= "view"
RUNCOMPLETION_NAME		= "name"
RUNCOMPLETION_COMPLETIONS	= "completion"
RUNCOMPLETION_FORMATHEAD	= "formathead"
RUNCOMPLETION_FORMATTAIL	= "formattail"
RUNCOMPLETION_ID			= "id"


API_SETSUBLIMESOCKETWINDOWBASEPATH = "setSublimeSocketWindowBasePath"



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


VIEW_EVENTS_RENEW		= [REACTABLE_VIEW_ON_NEW, REACTABLE_VIEW_ON_CLONE, REACTABLE_VIEW_ON_LOAD, SS_EVENT_COLLECT, SS_EVENT_LOADING, SS_EVENT_RENAMED] #list of acceptable-view renew event names.
VIEW_EVENTS_DEL			= [REACTABLE_VIEW_ON_CLOSE] #list of acceptable-view del event names.
VIEW_EVENTS_REACTIVE	= [REACTABLE_VIEW_ON_QUERY_COMPLETIONS, REACTABLE_VIEW_SS_V_DECREASED, REACTABLE_VIEW_SS_V_INCREASED]




