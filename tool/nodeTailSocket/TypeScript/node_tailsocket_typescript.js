// for TypeScript ver 1.1.0

// process.argv.forEach(function (val, index, array) {
//   console.log(index + ': ' + val);
// });


// requires ws, nodetail and tsc
var WebSocket = require('ws');
var Tail = require('tail').Tail;


var assert = require('assert');
var fs = require('fs'); 
var ws = new WebSocket('ws://127.0.0.1:8823/');


var projectPathWithNodeTailSocketJSPath = process.argv[1];// path of SOMEWHERE/node_tailsocket_typescript.js



var projectPath = "";

if (3 <= process.argv.length) {
    projectPath = process.argv[2];
} else {
    // assume that project's path is where "node_tailsocket_typescript.js" located. 
    // get last component path.
    var segements = projectPathWithNodeTailSocketJSPath.split("/");
    segements.splice(segements.length - 1, segements.length - 1);
    projectPath = segements.join("/");
}


console.log("nodeTailSocket: projectPath is:"+projectPath);


// path of compiler shell.
var tscwithenvPath = projectPath + "/tscwithenv.sh";
fs.exists(tscwithenvPath, function(exists) {
    assert(exists, "nodeTailSocket: " + tscwithenvPath + " is not exist. please put it.");
});


// generate log file.
var logPath = projectPath + "/tscompile.log";
fs.openSync(logPath, 'w');




console.log("connecting to SublimeSocket...");


ws.on('open', function() {
    console.log("connected to SublimeSocket.");
    
    var inputIdentityJSON = 
    {
        "to" : "nodetail"
    }
    var compilationFilterJSON = 
    {
        "name": "typescript",
        "filters": [
            {
                "(.*?)[(]([0-9].*?)[,].*: error .*: (.*)": {
                    "injects": {
                        "groups[0]": "name",
                        "groups[1]": "line",
                        "groups[2]": "message"
                    },
                    "selectors": [
                        {
                            "showStatusMessage<-message": {
                                
                            }
                        },
                        {
                            "showAtLog<-message": {

                            }
                        },
                        {
                            "appendRegion<-name, line, message": {
                                "condition": "keyword"
                            }
                        }
                    ]
                }
            },
            {
                "(.*)": {
                    "injects": {
                        "groups[0]": "message"
                    },
                    "selectors": [
                        {
                            "showAtLog<-message": {}
                        }
                    ]
                }
            },
            {
                 "^typescript compile succeeded.": {
                    "selectors": [
                        {
                            "showStatusMessage": {
                                "message": "typescript compile succeeded."
                            }
                        }
                    ]
                }
            },
            {
                 "^typescript compile failure.": {
                    "selectors": [
                        {
                            "showStatusMessage": {
                                "message": "typescript compile failure."
                            }
                        }
                    ]
                }
            }
        ]
    };

    var quickfixFilterJSON = {
        "name": "quickfix",
        "filters": [
            {
                // open it.
                "^open:(.*) :.*": {
                    "injects": {
                        "groups[0]": "path"
                    },
                    "selectors": [
                        {
                            "openFile<-path": {}
                        }
                    ]
                }
            },
            {
                "(.*)": {
                    "injects": {
                        "groups[0]": "message"
                    },
                    "selectors": [
                        {
                            "showAtLog<-message": {}
                        }
                    ]
                }
            }
        ]
    }

    var cursorModifyReactorJSON = {
        "react": "on_selection_modified",
        "delay": 100,
        "reactors": [
            {
                "selectedRegions<-name, selecteds": {
                    "selectors":[
                        {
                            "generate filtring source for quickfix/transform<-path, crossed, messages, to, line": {
                                "code": "import os\nname = os.path.basename(inputs[\"path\"])\nonselected = []\nmessages = inputs[\"messages\"]\nto = inputs[\"to\"]\nline = inputs[\"line\"]\nfor message in messages:\n\tselector = []\n\tfilteringContents = {\"name\":\"quickfix\", \"source\":message+\" @to \"+str(to)+\"  @line \"+str(line)+\" @on \"+name}\n\tfilteringAPI = {\"filtering\":filteringContents}\n\tselector.append(filteringAPI)\n\ttooltipItem = {}\n\ttooltipItem[message] = selector\n\tonselected.append(tooltipItem)\noutput({\"name\":name, \"onselected\":onselected, \"message\": messages[0]})\n",
                                "selectors": [
                                    {
                                        "clearSelection<-name": {

                                        }
                                    },
                                    {
                                        "afterAsync<-name, onselected": {
                                            "identity": "waitForClearSelection",
                                            "ms": 100,
                                            "selectors": [
                                                {
                                                    "showToolTip<-name, onselected": {
                                                        "oncancelled": [
                                                        ]
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        ]
    };

    var saveReactorJSON = {
        "react": "on_post_save",
        "delay": 100,
        "reactors": [
            {
                "eraseAllRegions":{
                    "selectors": [
                        {
                            "showAtLog<-deletes": {
                                "format": "the [deletes]"
                            }
                        }
                    ]
                }
            },
            {
                "afterAsync": {
                    "identity": "typescript-compilation",
                    "ms": 1,
                    "selectors": [
                        {
                            "showStatusMessage": {
                                "message": "typescript compiling..."
                            }
                        },
                        {
                            "showAtLog": {
                                "message": "typescript compiling..."
                            }
                        },
                        {
                            "runShell": {
                                "main": "/bin/sh",
                                "":[
                                    tscwithenvPath, projectPath
                                ]
                                // , "debug": true
                            }
                        }
                    ]
                }
            }
            
        ] 
    };

    var showUnopenedFile = {
        "react": "ss_f_noViewFound",
        "injects": {
            "name": "targetViewName",
            "message": "reason"
        },
        "reactors": [
            {
                "appendRegion<-targetViewName, reason": {
                    "format": "open:[targetViewName] :[reason]",
                    "name": "ss_viewkey_current",
                    "line": 1,
                    "condition": "constant.language"
                }
            }
        ]
    }
    
    var setUpDone = {
        "message": "SublimeSocket : typescript-compilation sequence ready!"
    };

    ws.send("ss@changeIdentity:"+JSON.stringify(inputIdentityJSON)
        +"->defineFilter:"+JSON.stringify(compilationFilterJSON)
        +"->defineFilter:"+JSON.stringify(quickfixFilterJSON)
        +"->setViewReactor:"+JSON.stringify(cursorModifyReactorJSON)
        +"->setViewReactor:"+JSON.stringify(saveReactorJSON)
        +"->setViewReactor:"+JSON.stringify(showUnopenedFile)
        +"->showAtLog:"+JSON.stringify(setUpDone)
        +"->showStatusMessage:"+JSON.stringify(setUpDone)
    );

    tail = new Tail(logPath);
    tail.on("line", function(message) {
        console.log("tsc: "+message);

        var tailedLogMessage = {
            "name": "typescript",
            "source": message
            // , "debug": true
        };
        
        ws.send("ss@filtering:" + JSON.stringify(tailedLogMessage));
    });
});

ws.on('message', function(data, flags) {
    // do nothing yet.
});
