
#API for Input to ST2/3 through WebSocket

### COMMAND		=		COMMAND_NAME : JSON_EXPRESSION
### COMMANDS	=		COMMAND_NAME : JSON_EXPRESSION -> COMMAND_NAME : JSON_EXPRESSION -> ...
### COMMANDS	=		COMMAND_NAME + COMMAND_NAME : JSON_EXPRESSION -> COMMAND_NAME + COMMAND_NAME + COMMAND_NAME : JSON_EXPRESSION -> ...

API_PREFIX = "sublimesocket"

API_PREFIX_SUB = "ss"
API_DEFINE_DELIM = "@"					# sublimesocket@commandA:{}->commandB:{}->commandC:[]->
API_CONCAT_DELIM = "->"					# concat commands. every commands run in sequential.
API_COMMAND_PARAMS_DELIM = ":"	# only first ":" will be evaluated as delimiter / each commnand.

API_COMMENT_DELIM	= "/"					# comment expression in API. ss@COMMENT/API...

API_PARAM_START		= "("					# ss@(key|value,key2|value2)commandA:,,,
API_PARAM_END			= ")"					# replace commandA's "key" by "value" of present-results.
API_PARAM_CONCAT	= "|"
API_PARAM_DELIM		= ","


API_VERSION = "1.4.0"
SOCKET_VERSION = 3	# for Sublime Text 3


# SublimeSocket internal event definition
SS_EVENT_COLLECT	= "ss_collect"
SS_EVENT_LOADING	= "ss_loading"

SS_FOUNDATION_NOVIEWFOUND	= "ss_f_noViewFound"
NOVIEWFOUND_TARGET		= "target"
NOVIEWFOUND_VIEW			= "view"
NOVIEWFOUND_LINE			= "line"
NOVIEWFOUND_MESSAGE		= "message"
NOVIEWFOUND_CONDITION = "condition"


SS_FOUNDATION_RUNWITHBUFFER = "ss_f_runWithBuffer"
F_RUNWITHBUFFER_TARGET	= "target"
F_RUNWITHBUFFER_VIEW		= "view"
F_RUNWITHBUFFER_BODY		= "body"
F_RUNWITHBUFFER_PATH		= "path"
F_RUNWITHBUFFER_ID			= "id"
F_RUNWITHBUFFER_ROWCOL		= "rowcol"


REACTABLE_EVENT_ON_QUERY_COMPLETIONS = "on_query_completions"


# internal APIs/
API_I_SHOWSTATUSMESSAGE	= "showStatusMessage"
SHOWSTATUSMESSAGE_MESSAGE	= "message"


# /internal APIs

# region identifier prefix
REGION_UUID_PREFIX = "ss_"


# public APIs
API_VERSIONVERIFY	= "versionVerify"
VERSIONVERIFY_SOCKETVERSION	= "socketVersion"
VERSIONVERIFY_APIVERSION		= "apiVersion"
VERSIONVERIFY_DRYRUN		= "dryrun"

VERIFICATION_CODE_VERIFIED_CLIENT_UPDATE = 2
VERIFICATION_CODE_VERIFIED = 1
VERIFICATION_CODE_REFUSED_DIFFERENT_SUBLIMESOCKET = 0
VERIFICATION_CODE_REFUSED_SUBLIMESOCKET_UPDATE = -1
VERIFICATION_CODE_REFUSED_CLIENT_UPDATE = -2


API_RUNTESTS		= "runTests"
RUNTESTS_PATH		= "path"

PARSERESULT_SWITCH	= "switch"
PARSERESULT_NONE	= "none"

API_ASSERTRESULT	= "assertResult"
ASSERTRESULT_CONTEXT	= "context"
ASSERTRESULT_CONTAINS	= "contains"
ASSERTRESULT_NOTCONTAINS = "notcontains"
ASSERTRESULT_ISEMPTY	= "isempty"
ASSERTRESULT_ISNOTEMPTY	= "isnotempty"
ASSERTRESULT_ID			= "id"
ASSERTRESULT_DESCRIPTION	= "description"
ASSERTRESULT_DEBUG		= "debug"
ASSERTRESULT_VALUE_PASS	= "Pass:"
ASSERTRESULT_VALUE_FAIL	= "Fail:"

API_RESETRESULTS		= "resetResults"


API_RUNSETTING		= "runSetting"
RUNSETTING_FILEPATH	= "path"
RUNSETTING_PREFIX_SUBLIMESOCKET_PATH = "SUBLIMESOCKET_PATH:"

API_INPUTIDENTITY = "inputIdentity"
IDENTITY_ID				= "id"

API_TEARDOWN			=	"tearDown"

API_CREATEBUFFER	= "createBuffer"
CREATEBUFFER_NAME	= "name"
CREATEBUFFER_CONTENTS = "contents"

API_OPENFILE		= "openFile"
OPENFILE_NAME		= "name"

API_CLOSEFILE		= "closeFile"
CLOSEFILE_NAME		= "name"


API_SETEVENTREACTOR	= "setEventReactor"
API_SETVIEWREACTOR	= "setViewReactor"

REACTOR_TARGET		= "target"
REACTOR_REACT		= "react"
REACTOR_SELECTORS	= "selectors"
REACTOR_DELAY		= "delay"
REACTOR_REPLACEFROMTO		= "replacefromto"

REACTOR_VIEWKEY_VIEWSELF	= "view"
REACTOR_VIEWKEY_ID			= "viewId"
REACTOR_VIEWKEY_BUFFERID	= "bufferId"
REACTOR_VIEWKEY_PATH		= "path"
REACTOR_VIEWKEY_BASENAME	= "basename"
REACTOR_VIEWKEY_VNAME		= "vname"
REACTOR_VIEWKEY_SELECTED	= "selected"

REACTORTYPE_EVENT	= "event"
REACTORTYPE_VIEW	= "view"


API_RESETREACTORS		= "resetReactors"

API_SETSELECTION	= "setSelection"
SETSELECTION_PATH	= "path"
SETSELECTION_FROM	= "from"
SETSELECTION_TO		= "to"
SS_VIEW_ON_SELECTION_MODIFIED_BY_SETSELECTION = "on_selection_modified_by_setselection"


REACTIVE_PREFIX_USERDEFINED_EVENT	= "event_"
REACTIVE_REACTABLE_EVENT			= [REACTABLE_EVENT_ON_QUERY_COMPLETIONS]
REACTIVE_FOUNDATION_EVENT = [SS_FOUNDATION_NOVIEWFOUND, SS_FOUNDATION_RUNWITHBUFFER]
REACTIVE_CURRENT_COMPLETINGS = "currentcompletings"

API_KEYVALUESTORE	= "kvs"
KVS_SHOWALL				= "showAll"
KVS_SHOWVALUE			= "showValue"
KVS_REMOVEVALUE		= "removeValue"
KVS_CLEAR					= "clear"

API_DEFINEFILTER	= "defineFilter"
DEFINEFILTER_PATTERNS		= "patterns"
DEFINEFILTER_NAME = "name"


API_FILTERING			= "filtering"
FILTER_NAME				= "name"
FILTER_SOURCE			= "source"
FILTER_SELECTORS	= "selectors"
FILTER_COMMENT		= "comment"
FILTER_DOTALL		= "dotall"
FILTER_DEBUG			= "debug"

API_CONTAINSREGIONS	= "containsRegions"
CONTAINSREGIONS_VIEW	= "view"
CONTAINSREGIONS_TARGET	= "target"
CONTAINSREGIONS_SELECTED = "selected"
CONTAINSREGIONS_EMIT	= "emit"
CONTAINSREGIONS_DEBUG	= "debug"

API_COLLECTVIEWS	= "collectViews"

API_RUNSHELL			= "runShell"
RUNSHELL_MAIN			= "main"
RUNSHELL_DELAY		= "delay"
RUNSHELL_DEBUG		= "debug"
RUNSHELL_LIST_IGNORES = [RUNSHELL_MAIN, RUNSHELL_DELAY, RUNSHELL_DEBUG]
RUNSHELL_REPLACE_SPACE	= "_"
RUNSHELL_REPLACE_RIGHTBRACE = ""
RUNSHELL_REPLACE_LEFTBRACE	= ""
RUNSHELL_REPLACE_SINGLEQUOTE = ""
RUNSHELL_REPLACE_At_s_At_s_At			= " "


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

API_APPENDREGION	= "appendRegion"
APPENDREGION_PATH	= "path"
APPENDREGION_LINE	= "line"
APPENDREGION_MESSAGE	= "message"
APPENDREGION_CONDITION = "condition"

API_ERASEALLREGION	= "eraseAllRegion"
ERASEALLREGION_PATH	= "path"

API_RUNWITHBUFFER	= "runWithBuffer"
RUNWITHBUFFER_VIEW = "view"

API_NOTIFY				= "notify"
NOTIFY_TITLE			= "title"
NOTIFY_MESSAGE		= "message"
NOTIFY_DEBUG			= "debug"

API_GETALLFILEPATH	= "getAllFilePath"
GETALLFILEPATH_PATHS = "paths"
GETALLFILEPATH_ANCHOR = "anchor"
GETALLFILEPATH_HEADER	= "header"
GETALLFILEPATH_FOOTER	= "footer"

API_READFILEDATA	= "readFileData"
READFILEDATA_PATH = "path"
READFILEDATA_DATA = "data"

API_EVENTEMIT			= "eventEmit"
EVENTEMIT_TARGET	= "target"
EVENTEMIT_EVENT		= "event"

API_CANCELCOMPLETION = "cancelCompletion"
CANCELCOMPLETION_VIEW = "view"
CANCELCOMPLETION_TRIGGER = "trigger"
CANCELCOMPLETION_TRIGGER_BASEREDUCED = "trigger_basereduced"
CANCELCOMPLETION_TRIGGERS = [CANCELCOMPLETION_TRIGGER_BASEREDUCED]

API_PREPARECOMPLETION = "prepareCompletion"
PREPARECOMPLETION_ID	= "id"

API_RUNCOMPLETION	= "runCompletion"
RUNCOMPLETION_VIEW	= "view"
RUNCOMPLETION_COMPLETIONS = "completion"
RUNCOMPLETION_FORMATHEAD = "formathead"
RUNCOMPLETION_FORMATTAIL = "formattail"
RUNCOMPLETION_ID	= "id"
RUNCOMPLETION_LOCKCOUNT = "lockcount"


API_OPENPAGE			= "openPage"
OPENPAGE_IDENTITY = "identity"

API_SETSUBLIMESOCKETWINDOWBASEPATH = "setSublimeSocketWindowBasePath"


#Dictionaries for collection of "Views", "filters", "events"
DICT_VIEWS				= "DICT_VIEWS"

VIEW_SELF				= "view"
VIEW_PATH				= "path"
VIEW_ID					= "viewId"
VIEW_BUFFERID			= "bufferId"
VIEW_BASENAME			= "basename"
VIEW_VNAME				= "vname"
VIEW_SELECTED			= "selected"

VIEW_EVENTS_RENEW	= ["on_new", "on_clone", "on_load", "on_modified", SS_EVENT_COLLECT, SS_EVENT_LOADING] #list of acceptable-view renew event names.
VIEW_EVENTS_DEL		= ["on_close"] #list of acceptable-view del event names.

DICT_FILTERS			= "DICT_FILTERS"

DICT_REACTORS			= "DICT_REACTORS"


SUBDICT_REGIONS		= "SUBDICT_REGIONS"
REGION_IDENTITY		= "identity"
REGION_SELF				= "region"
REGION_EVENT			= "event"
REGION_MESSAGE		= "message"
REGION_LINE				= "line"

SUBARRAY_DELETED_REGIONS		= "SUBARRAY_DELETED_REGIONS"


