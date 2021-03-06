define({ api: [
  {
    "group": "addTransfer",
    "type": "SushiJSON",
    "url": "addTransfer:{JSON}",
    "title": "add transfer with protocol. root > transferIdentity(protocol) > connectionIdentity.",
    "examples": [
      {
        "title": "[example]",
        "content": "addTransfer: {\n  \"transferIdentity\": \"testAdditionalSushiJSONServer\",\n  \"connectionIdentity\": \"testAdditionalSushiJSONConnection\",\n  \"protocol\": \"RunSushiJSONServer\",\n  \"params\": {\n      \"path\": \"SUBLIMESOCKET_PATH:tests/testResources/sample_SushiJSON.txt\"\n  },\n  \"selectors\": [\n      {\n          \"showAtLog<-transferIdentity\": {\n              \"format\": \"transfer [transferIdentity] added.\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "transferIdentity",
            "optional": false,
            "description": "the transfer's identity of the new transfer's first connection."
          },
          {
            "group": "Parameter",
            "type": "String",
            "field": "connectionIdentity",
            "optional": false,
            "description": "the connection's identity of the new transfer's first connection."
          },
          {
            "group": "Parameter",
            "type": "String",
            "field": "protocol",
            "optional": false,
            "description": "the protocol of the new transfer."
          },
          {
            "group": "Parameter",
            "type": "JSON",
            "field": "params",
            "optional": false,
            "description": "the parameters for setup of the new transfer."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "afterAsync",
    "type": "SushiJSON",
    "url": "afterAsync:{JSON}",
    "title": "go to next API and run selectors after milliseconds",
    "examples": [
      {
        "title": "[example]",
        "content": "afterAsync: {\n  \"identity\": \"testIdentity\",\n  \"ms\": 100,\n  \"selectors\": [\n      {\n          \"showAtLog\": {\n              \"message\": \"hello after 100\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "identity",
            "optional": false,
            "description": "identifier of this async block."
          },
          {
            "group": "Parameter",
            "type": "Int",
            "field": "ms",
            "optional": false,
            "description": "run selectors after this milliseconds."
          },
          {
            "group": "Parameter",
            "type": "Selectors",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "Everything",
            "field": "keys_and_values",
            "optional": false,
            "description": "this api injects all keys and values to selectors."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "appendRegion",
    "type": "SushiJSON",
    "url": "appendRegion:{JSON}",
    "title": "append region and input parameter to the file",
    "examples": [
      {
        "title": "[example]",
        "content": "appendRegion: {\n  \"name\": \"target.txt\",\n  \"line\": \"1\",\n  \"message\": \"test\",\n  \"condition\": \"keyword\"\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "the target file's last part of file path or fullpath or parts."
          },
          {
            "group": "Parameter",
            "type": "String",
            "field": "message",
            "optional": false,
            "description": "message contents. will raise event."
          },
          {
            "group": "Parameter",
            "type": "String",
            "field": "condition",
            "optional": false,
            "description": "set the color of region. \"keyword\", \"string\", and more. depends on Sublime Text's theme."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String",
            "field": "path",
            "optional": false,
            "description": "the full path of the file."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "the name of the file."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "identity",
            "optional": false,
            "description": "automatically defined identity."
          },
          {
            "group": "Injects",
            "type": "Int",
            "field": "line",
            "optional": false,
            "description": "the line count where the region located."
          },
          {
            "group": "Injects",
            "type": "Int",
            "field": "from",
            "optional": false,
            "description": "start point of region."
          },
          {
            "group": "Injects",
            "type": "Int",
            "field": "to",
            "optional": false,
            "description": "end point of region."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "message",
            "optional": false,
            "description": "the message parameter of the region."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "condition",
            "optional": false,
            "description": "the condition parameter of the region."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "broadcastMessage",
    "type": "SushiJSON",
    "url": "broadcastMessage:{JSON}",
    "title": "broadcast message to transfers.",
    "examples": [
      {
        "title": "[example]",
        "content": "broadcastMessage: {\n  \"message\": \"broadcasting\",\n  \"selectors\": [\n      {\n          \"showAtLog<-targets, message\": {\n              \"format\": \"[targets], [message]\"\n          }\n      }\n  ]\n}\nor\n\"broadcastMessage<-head, body, tail\": {\n  \"format\": \"broadcasting [head] [body] [tail]\"\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "message",
            "optional": false,
            "description": "contents."
          },
          {
            "group": "Parameter",
            "type": "String(Optional)",
            "field": "format",
            "optional": false,
            "description": "construct string with bracket([, and ]) injected value."
          },
          {
            "group": "Parameter",
            "type": "String[](Optional)",
            "field": "targets",
            "optional": false,
            "description": "specify targets for broadcasting by identity of transfers."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String[]",
            "field": "transferIdentities",
            "optional": false,
            "description": "broadcasted identities of transfer."
          },
          {
            "group": "Injects",
            "type": "String[]",
            "field": "targets",
            "optional": false,
            "description": "setuped targets of transfer."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "message",
            "optional": false,
            "description": "broadcasted message."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "cancelCompletion",
    "type": "SushiJSON",
    "url": "cancelCompletion:{JSON}",
    "title": "close completion window and delete completion candidate data.",
    "examples": [
      {
        "title": "[example]",
        "content": "cancelCompletion: {\n  \"name\": \"sample.txt\",\n  \"injects\": {\n      \"name\": \"name\"\n  },\n  \"selectors\": [\n      {\n          \"showAtLog<-name\": {\n              \"format\": \"completion cancelled at [name]\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "the target file's last part of file path or fullpath or parts."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "changeIdentity",
    "type": "SushiJSON",
    "url": "changeIdentity:{JSON}",
    "title": "chamge identity of specified transfer's connection.",
    "examples": [
      {
        "title": "[example]",
        "content": "changeIdentity: {\n  \"from\": \"sublimesockettest\",\n  \"to\": \"test\",\n  \"injects\": {\n      \"from\": \"from\",\n      \"to\": \"to\"\n  },\n  \"selectors\": [\n      {\n          \"showAtLog<-from, to\": {\n              \"format\": \"[from] becomes [to].\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String(Optional)",
            "field": "from",
            "optional": false,
            "description": "specify the target connection's identity which will be renamed. if not, requested connection's identitiy will be used."
          },
          {
            "group": "Parameter",
            "type": "String",
            "field": "to",
            "optional": false,
            "description": "value for rename."
          },
          {
            "group": "Parameter",
            "type": "String(Optional)",
            "field": "transfer",
            "optional": false,
            "description": "'s identity which has connection of the target. if not, requested transfer's identitiy will be used."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String",
            "field": "from",
            "optional": false,
            "description": "the identity before changed."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "to",
            "optional": false,
            "description": "the identity after changed."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "clearSelection",
    "type": "SushiJSON",
    "url": "clearSelection:{JSON}",
    "title": "clear the selection of file",
    "examples": [
      {
        "title": "[example]",
        "content": "clearSelection: {\n  \"name\": \"clearSelection.txt\",\n  \"selectors\": [\n      {\n          \"showAtLog<-name, cleards\": {\n              \"format\": \"[name] + [cleards].\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "the target file's last part of file path or fullpath or parts."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String",
            "field": "path",
            "optional": false,
            "description": "target file's path."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "target file's name."
          },
          {
            "group": "Injects",
            "type": "Array",
            "field": "cleards",
            "optional": false,
            "description": "the list of cleared [from] and [to]."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "closeAllBuffer",
    "type": "SushiJSON",
    "url": "closeAllBuffer:{JSON}",
    "title": "close all buffers.",
    "examples": [
      {
        "title": "[example]",
        "content": "closeAllBuffer: {\n  \"injects\": {\n      \"closeds\": \"message\"\n  },\n  \"selectors\": [\n      {\n          \"showAtLog<-message\": {}\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String[]",
            "field": "closeds",
            "optional": false,
            "description": "the list of closed buffer's names."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "closeAllFiles",
    "type": "SushiJSON",
    "url": "closeAllFiles:{JSON}",
    "title": "close all files or close excepted-specific named files.",
    "examples": [
      {
        "title": "[example]",
        "content": "closeAllFiles: {\n  \"dryrun\": true,\n  \"selectors\": [\n      {\n          \"showAtLog<-closeds\": {\n              \"format\": \"[closeds]\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String(Optional)",
            "field": "excepts",
            "optional": false,
            "description": "the list of file names which do not want to close."
          },
          {
            "group": "Parameter",
            "type": "Bool(Optional)",
            "field": "dryrun",
            "optional": false,
            "description": "the flag for debug."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "Strings",
            "field": "closeds",
            "optional": false,
            "description": "the list of closed file's full path."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "closeFile",
    "type": "SushiJSON",
    "url": "closeFile:{JSON}",
    "title": "close the file which is exist.",
    "examples": [
      {
        "title": "[example]",
        "content": "closeFile: {\n  \"name\": \"sample.txt\"\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "the target file's last part of file path or fullpath or parts."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "the name = last path part of the closed file."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "path",
            "optional": false,
            "description": "the full path of the closed file."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "collectViews",
    "type": "SushiJSON",
    "url": "collectViews:{JSON}",
    "title": "collect all window's all opened file's path",
    "examples": [
      {
        "title": "[example]",
        "content": "collectViews: {\n  \"selectors\": [\n      {\n          \"showAtLog<-collecteds\": {\n              \"format\": \"[collecteds]\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "Array",
            "field": "collecteds",
            "optional": false,
            "description": "all opened file's paths."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "connectedCall",
    "type": "SushiJSON",
    "url": "connectedCall:{}",
    "title": "raise SublimeSocketServer's connected event.",
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "countUp",
    "type": "SushiJSON",
    "url": "countUp:{JSON}",
    "title": "count up mechanism. if the label was already defined, countup it.",
    "examples": [
      {
        "title": "[example]",
        "content": "countUp: {\n  \"label\": \"countIdentity\",\n  \"default\": 0\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "label",
            "optional": false,
            "description": "identifier of the count machine. countup if same label is defined."
          },
          {
            "group": "Parameter",
            "type": "Int",
            "field": "default",
            "optional": false,
            "description": "the first value of the count."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String",
            "field": "label",
            "optional": false,
            "description": "inputted label."
          },
          {
            "group": "Injects",
            "type": "Int",
            "field": "count",
            "optional": false,
            "description": "the count after define/countup."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "createBuffer",
    "type": "SushiJSON",
    "url": "createBuffer:{JSON}",
    "title": "create the named buffer.",
    "examples": [
      {
        "title": "[example]",
        "content": "createBuffer: {\n  \"name\": \"test\",\n  \"selectors\": [\n      {\n          \"showAtLog<-name\": {\n              \"format\": \"[name] created.\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "set the name of buffer."
          },
          {
            "group": "Parameter",
            "type": "String(Optional)",
            "field": "contents",
            "optional": false,
            "description": "the contents of buffer. create, named then insert contents to the buffer."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "Strings",
            "field": "name",
            "optional": false,
            "description": "the name of buffer."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "defineFilter",
    "type": "SushiJSON",
    "url": "defineFilter:{JSON}",
    "title": "define regexp filter & selector, use with filtering API",
    "examples": [
      {
        "title": "[example]",
        "content": "defineFilter: {\n  \"name\": \"test\",\n  \"filters\": [\n      {\n          \"(.*)1 (.*)2 ([0-9].*?)a3 (.*)4\": {\n              \"injects\": {\n                  \"groups[3]\": \"name\",\n                  \"groups[1]\": \"add\",\n                  \"groups[2]\": \"to\"\n              },\n              \"selectors\": [\n                  {\n                      \"showAtLog<-name, add, to\": {\n                          \"format\": \"[name], [add], [to]\"\n                      }\n                  }\n              ],\n              \"dotall\": false\n          }\n      },\n      {\n          \"(.*)\": {\n              \"selectors\": [\n                  {\n                      \"showAtLog<-groups[0]\": {\n                          \"format\": \"[groups[0]]\"\n                      }\n                  }\n              ]\n          }\n      }\n  ],\n  \"selectors\": [\n      {\n          \"showAtLog<-name, patterns\": {\n              \"format\": \"[name], [patterns]\"\n          }\n      }\n  ]\n}->filtering: {\n  \"name\": \"test\",\n  \"source\": \"the1 test2 4a3 nestedFilterCase.txt4\"\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "the name of filter."
          },
          {
            "group": "Parameter",
            "type": "SelectorsWithKey",
            "field": "regexp",
            "optional": false,
            "description": "regular expression for filtering with selectors. Matched parameters will injects as [groups[INDEX]](partial) and [group](whole). Matched parameters are automatically injected to selectors."
          },
          {
            "group": "Parameter",
            "type": "String(Optional)",
            "field": "comments",
            "optional": false,
            "description": "comment for the filter. show if filtering contains debug: true."
          },
          {
            "group": "Parameter",
            "type": "Bool(Optional)",
            "field": "dotall",
            "optional": false,
            "description": "use dotall option of regexp. By default false."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "filter's path."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "patterns",
            "optional": false,
            "description": "defined regexp patterns."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "eraseAllRegions",
    "type": "SushiJSON",
    "url": "eraseAllRegions:{JSON}",
    "title": "erase all regions(sometimes this API fails...)",
    "examples": [
      {
        "title": "[example]",
        "content": "eraseAllRegions: {\n  \"injects\": {\n      \"deletes\": \"message\"\n  },\n  \"selectors\": [\n      {\n          \"showAtLog<-message\": {}\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "the target file's last part of file path or fullpath or parts."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "Array",
            "field": "deletes",
            "optional": false,
            "description": "deleted regions's [from] and [to] pairs."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "eventEmit",
    "type": "SushiJSON",
    "url": "eventEmit:{JSON}",
    "title": "emit specific event",
    "examples": [
      {
        "title": "[example]",
        "content": "eventEmit: {\n  \"event\": \"event_eventWithIdentity\",\n  \"sample-key\": \"sample-value\"\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "event",
            "optional": false,
            "description": "event name. shoud start with [event_]."
          },
          {
            "group": "Parameter",
            "type": "*(Optional)",
            "field": "*",
            "optional": false,
            "description": "This API is vector of any key-param value. Can emit event with any keys and values of injected."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String",
            "field": "event",
            "optional": false,
            "description": "emitted event name."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "filtering",
    "type": "SushiJSON",
    "url": "filtering:{JSON}",
    "title": "input source string to specific filter, use with defineFilter API",
    "examples": [
      {
        "title": "[example]",
        "content": "filtering: {\n  \"name\": \"test\",\n  \"source\": \"the1 test2 4a3 nestedFilterCase.txt4\",\n  \"debug\": true\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "the target filter's name."
          },
          {
            "group": "Parameter",
            "type": "String",
            "field": "source",
            "optional": false,
            "description": "the input for regexp filtering."
          },
          {
            "group": "Parameter",
            "type": "Bool(Optional)",
            "field": "debug",
            "optional": false,
            "description": "show debug info. By default false."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "forcelySave",
    "type": "SushiJSON",
    "url": "forcelySave:{JSON}",
    "title": "forcely save file.",
    "examples": [
      {
        "title": "[example]",
        "content": "forcelySave: {\n  \"name\": \"sample.txt\",\n  \"injects\": {\n      \"name\": \"message\"\n  },\n  \"selectors\": [\n      {\n          \"showAtLog<-message\": {\n    \n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "the target file's last part of file path or fullpath or parts."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String",
            "field": "path",
            "optional": false,
            "description": "file's path."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "file's name."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "getAllFilePath",
    "type": "SushiJSON",
    "url": "getAllFilePath:{JSON}",
    "title": "get all file's paths with direction.",
    "examples": [
      {
        "title": "[example]",
        "content": "getAllFilePath: {\n  \"anchor\": \"tests.html\",\n  \"limit\": 1,\n  \"selectors\": [\n      {\n          \"showAtLog<-paths, fullpaths, basedir\": {\n              \"format\": \"the [basedir] + [paths] + [fullpaths]\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "anchor",
            "optional": false,
            "description": "the target file's name(part or whole path). seek the current folder with limit of seek depth. go above folder and search the file. then get all file's path under anchor path."
          },
          {
            "group": "Parameter",
            "type": "Int",
            "field": "limit",
            "optional": false,
            "description": "limit depth of seek."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String",
            "field": "basedir",
            "optional": false,
            "description": "found anchor file's path."
          },
          {
            "group": "Injects",
            "type": "String[]",
            "field": "paths",
            "optional": false,
            "description": "found file's paths."
          },
          {
            "group": "Injects",
            "type": "String[]",
            "field": "fullpaths",
            "optional": false,
            "description": "found file's full-paths."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "inputToTransfer",
    "type": "SushiJSON",
    "url": "inputToTransfer:{JSON}",
    "title": "input data to transfer. Behaviour is depends on protocol.",
    "examples": [
      {
        "title": "[example]",
        "content": "now loading...\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "transferIdentity",
            "optional": false,
            "description": "the target transfer's identity. Raise error if not exist."
          },
          {
            "group": "Parameter",
            "type": "JSON",
            "field": "params",
            "optional": false,
            "description": "the parameters for input of the transfer."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "modifyView",
    "type": "SushiJSON",
    "url": "modifyView:{JSON}",
    "title": "modify specific view",
    "examples": [
      {
        "title": "[example]",
        "content": "modifyView: {\n  \"name\": \"sample.txt\",\n  \"add\": \"1\"\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "the target file's last part of file path or fullpath or parts."
          },
          {
            "group": "Parameter",
            "type": "String(Optional)",
            "field": "add",
            "optional": false,
            "description": "add string value. if position is not specified, add the end of file."
          },
          {
            "group": "Parameter",
            "type": "String(Optional)",
            "field": "to",
            "optional": false,
            "description": "the point to insert."
          },
          {
            "group": "Parameter",
            "type": "String(Optional)",
            "field": "line",
            "optional": false,
            "description": "the line to insert."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String",
            "field": "path",
            "optional": false,
            "description": "modified file's path."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "modified file's name."
          },
          {
            "group": "Injects",
            "type": "Int",
            "field": "line",
            "optional": false,
            "description": "modified file's specified line."
          },
          {
            "group": "Injects",
            "type": "Int",
            "field": "to",
            "optional": false,
            "description": "modified file's specified point."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "monocastMessage",
    "type": "SushiJSON",
    "url": "monocastMessage:{JSON}",
    "title": "monocast message to transfer.",
    "examples": [
      {
        "title": "[example]",
        "content": "monocastMessage: {\n  \"target\": \"noTarget\",\n  \"message\": \"the message for you!\",\n  \"injects\": {\n      \"message\": \"body\"\n  },\n  \"selectors\": [\n      {\n          \"showAtLog<-target, body\": {\n              \"format\": \"[target], [body]\"\n          }\n      }\n  ]\n}\nor\n\"monocastMessage<-head, body, tail\": {\n  \"target\": \"noTarget\",\n  \"format\": \"the message for you! [head] [body] [tail]\"\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "message",
            "optional": false,
            "description": "contents."
          },
          {
            "group": "Parameter",
            "type": "String(Optional)",
            "field": "format",
            "optional": false,
            "description": "construct string with bracket([, and ]) injected value."
          },
          {
            "group": "Parameter",
            "type": "String",
            "field": "target",
            "optional": false,
            "description": "specify target for monocasting by identity of transfer."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String",
            "field": "transferIdentity",
            "optional": false,
            "description": "monocasted identitiy of the transfer."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "target",
            "optional": false,
            "description": "setuped targets of transfer."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "message",
            "optional": false,
            "description": "monocasted message."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "notify(deprecated)",
    "type": "SushiJSON",
    "url": "notify:{JSON}",
    "title": "show notification.",
    "examples": [
      {
        "title": "[example]",
        "content": "notify: {\n  \"title\": \"test_notify\",\n  \"message\": \"notice!\",\n  \"selectors\": [\n      {\n          \"showAtLog<-title, message\": {\n              \"format\": \"[title], [message]\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "openFile",
    "type": "SushiJSON",
    "url": "openFile:{JSON}",
    "title": "open the file which is exist.",
    "examples": [
      {
        "title": "[example]",
        "content": "openFile: {\n  \"path\": \"SUBLIMESOCKET_PATH:tests/testResources/sample.txt\",\n  \"selectors\": [\n      {\n          \"showAtLog<-name\": {\n              \"format\": \"opened [name]\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "path",
            "optional": false,
            "description": "open file if exist. or not, do nothing."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "the name = last path part of the file."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "path",
            "optional": false,
            "description": "the full path of the file."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "readFile",
    "type": "SushiJSON",
    "url": "readFile:{JSON}",
    "title": "read file's contents.",
    "examples": [
      {
        "title": "[example]",
        "content": "readFile: {\n  \"path\": \"~/tests/sample.txt\",\n  \"injects\": {\n      \"data\": \"data\"\n  }, \n  \"selectors\": [\n      {\n          \"showAtLog<-path, data\": {\n              \"format\": \"[path], [data]\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "path",
            "optional": false,
            "description": "the target file's full path."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String",
            "field": "path",
            "optional": false,
            "description": "file's path."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "data",
            "optional": false,
            "description": "whole contents of file."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "removeTransfer",
    "type": "SushiJSON",
    "url": "removeTransfer:{JSON}",
    "title": "remove transfer with transferIdentity.",
    "examples": [
      {
        "title": "[example]",
        "content": "now loading...\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "transferIdentity",
            "optional": false,
            "description": "the transfer's identity for remove."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "resetCounts",
    "type": "SushiJSON",
    "url": "resetCounts:{JSON}",
    "title": "reset the labeled count.",
    "examples": [
      {
        "title": "[example]",
        "content": "resetCounts: {\n  \"label\": \"countIdentity\"\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String(Optional)",
            "field": "label",
            "optional": false,
            "description": "identifier of the count machine. countup if same label is defined. reset all if not specified."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "Strings",
            "field": "resetted",
            "optional": false,
            "description": "the list of labels which was resetted."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "resetReactors",
    "type": "SushiJSON",
    "url": "resetReactors:{JSON}",
    "title": "reset all reactors.",
    "examples": [
      {
        "title": "[example]",
        "content": "resetReactors: {\n              \n}\n"
      }
    ],
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "Strings[]",
            "field": "deleteds",
            "optional": false,
            "description": "deleted reactor's names."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "resetReactors",
    "type": "SushiJSON",
    "url": "resetReactors:{JSON}",
    "title": "reset all reactors.",
    "examples": [
      {
        "title": "[example]",
        "content": "resetReactors: {\n              \n}\n"
      }
    ],
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "Strings[]",
            "field": "deleteds",
            "optional": false,
            "description": "deleted reactor's names."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "runCompletion",
    "type": "SushiJSON",
    "url": "runCompletion:{JSON}",
    "title": "show completion candidate datas.",
    "examples": [
      {
        "title": "[example]",
        "content": "runCompletion: {\n  \"name\": \"completionTestView.txt\",\n  \"completion\": [\n      {\n          \"HEAD\": \"DrawLine\",\n          \"paramsTargetFmt\": \"(${1:start}, ${2:end}, ${3:color}, ${4:duration}, ${5:depthTest})\",\n          \"return\": \"Void\",\n          \"paramsTypeDef\": \"(Vector3,Vector3,Color,Single,Boolean)\",\n          \"head\": \"DrawLine\"\n      }\n  ],\n  \"formathead\": \"HEADparamsTypeDef\\treturn\",\n  \"formattail\": \"headparamsTargetFmt$0\",\n  \"selectors\": [\n      {\n          \"showAtLog<-name\": {\n              \"format\": \"[name]\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "the target file's last part of file path or fullpath or parts."
          },
          {
            "group": "Parameter",
            "type": "String",
            "field": "completion",
            "optional": false,
            "description": "parts of completion string sources. Will become completion string."
          },
          {
            "group": "Parameter",
            "type": "String",
            "field": "formathead",
            "optional": false,
            "description": "header part of completion string. constructed bt the contents of completion's key-value."
          },
          {
            "group": "Parameter",
            "type": "String",
            "field": "formattail",
            "optional": false,
            "description": "footer part of completion string. constructed bt the contents of completion's key-value."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String",
            "field": "path",
            "optional": false,
            "description": "file's path."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "file's name."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "runSelectorsWithInjects",
    "type": "SushiJSON",
    "url": "runSelectorsWithInjects:{JSON}",
    "title": "run \"selectos\" with specific injection of keys & values.",
    "examples": [
      {
        "title": "[example]",
        "content": "runSelectorsWithInjects: {\n\"injects\": {\n\"key1\": \"key2\"\n},\n  \"selectors\": [\n      {\n          \"showAtLog<-key2\": {\n              \"format\": \"injected [key2]\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "JSON",
            "field": "injects",
            "optional": false,
            "description": "the pair of before-after key name transform."
          },
          {
            "group": "Parameter",
            "type": "Selectors",
            "field": "selectors",
            "optional": false,
            "description": "the selectors which run with injects all keys & values."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "runShell",
    "type": "SushiJSON",
    "url": "runShell:{JSON}",
    "title": "run shell(Mac only)",
    "examples": [
      {
        "title": "[example]",
        "content": "runShell: {\n  \"main\": \"pwd\",\n  \"debug\": true\n}\nor\nrunShell: {\n  \"main\": \"ls\",\n  \"\": [\"-l\"]\n}\nor\nrunShell: {\n  \"main\": \"find\",\n  \"\": \"/target/folder\",\n  \"-name\": \"targetName\"\n}\nor\n\"runShell<-main, sub, option\": {\n  \"format\": \"[main] [sub] -o [option]\"\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String(Reserved)",
            "field": "main",
            "optional": false,
            "description": "the head of command line phrase. In many case this should be full-path. not good."
          },
          {
            "group": "Parameter",
            "type": "String(Reserved)",
            "field": "format",
            "optional": false,
            "description": "construct string with bracket([, and ]) injected value."
          },
          {
            "group": "Parameter",
            "type": "String(Optional, Reserved)",
            "field": "\"",
            "optional": false,
            "description": "\"(empty) is allowed for using String array."
          },
          {
            "group": "Parameter",
            "type": "String(Optional)",
            "field": "ANYSTRING",
            "optional": false,
            "description": "the key and value pair will be translated to [ANYSTRING value]. every array contents will concat with space."
          },
          {
            "group": "Parameter",
            "type": "Int(Optional, Reserved)",
            "field": "delay",
            "optional": false,
            "description": "ruh shellScript after delay in another thread."
          },
          {
            "group": "Parameter",
            "type": "Bool(Optional, Reserved)",
            "field": "debug",
            "optional": false,
            "description": "show eventual executed command string. By default false."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "runSushiJSON",
    "type": "SushiJSON",
    "url": "runSushiJSON:{JSON}",
    "title": "run SushiJSON formatted string as APISuites.",
    "examples": [
      {
        "title": "[example]",
        "content": "runSushiJSON: {\n  \"path\": \"SUBLIMESOCKET_PATH:tests/testResources/sample_SushiJSON.txt\",\n  \"selectors\": [\n      {\n          \"showAtLog<-logs\": {\n              \"format\": \"runSetting logs:[logs]\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String(Optional)",
            "field": "path",
            "optional": false,
            "description": "the path of SushiJSON descripted file."
          },
          {
            "group": "Parameter",
            "type": "String(Optional)",
            "field": "data",
            "optional": false,
            "description": "the strings of SushiJSON."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "Strings",
            "field": "logs",
            "optional": false,
            "description": "the list of the SushiJSON's result = \"showAtLog\" message which was running inside path / data."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "scrollTo",
    "type": "SushiJSON",
    "url": "scrollTo:{JSON}",
    "title": "scroll to the point of file.",
    "examples": [
      {
        "title": "[example]",
        "content": "scrollTo: {\n  \"name\": \"sample.txt\",\n  \"line\": 30,\n  \"selectors\": [\n      {\n          \"showAtLog\": {\n              \"message\": \"scroll done.\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "the target file's last part of file path or fullpath or parts."
          },
          {
            "group": "Parameter",
            "type": "Int(Optional)",
            "field": "line",
            "optional": false,
            "description": "target line number."
          },
          {
            "group": "Parameter",
            "type": "Int(Optional)",
            "field": "count",
            "optional": false,
            "description": "target point."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "scrollTo",
    "type": "SushiJSON",
    "url": "scrollTo:{JSON}",
    "title": "scroll to the point of file.",
    "examples": [
      {
        "title": "[example]",
        "content": "scrollTo: {\n  \"name\": \"sample.txt\",\n  \"line\": 30,\n  \"selectors\": [\n      {\n          \"showAtLog\": {\n              \"message\": \"scroll done.\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "the target file's last part of file path or fullpath or parts."
          },
          {
            "group": "Parameter",
            "type": "Int(Optional)",
            "field": "line",
            "optional": false,
            "description": "target line number."
          },
          {
            "group": "Parameter",
            "type": "Int(Optional)",
            "field": "count",
            "optional": false,
            "description": "target point."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "selectedRegions",
    "type": "SushiJSON",
    "url": "selectedRegions:{JSON}",
    "title": "output the contents of region if the selection contains region",
    "examples": [
      {
        "title": "[example]",
        "content": "setViewReactor: {\n  \"react\": \"on_selection_modified\",\n  \"reactors\": [\n      {\n          \"selectedRegions<-name, selecteds\": {\n              \"isexactly\": false,\n              \"selectors\": [\n                  {\n                      \"showAtLog<-line, from, to\": {\n                          \"format\": \"L:[line], ([from], [to])\"\n                      }\n                  }\n              ]\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "the name of file."
          },
          {
            "group": "Parameter",
            "type": "List",
            "field": "selecteds",
            "optional": false,
            "description": "the list of selections. e,g, [ [from1, to1], [from2, to2] ]."
          },
          {
            "group": "Parameter",
            "type": "Bool(Optional)",
            "field": "isexactly",
            "optional": false,
            "description": "if false, react with contains region exactly. By default this is true."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String",
            "field": "path",
            "optional": false,
            "description": "the full path of the file."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "the name of the file."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "crossed",
            "optional": false,
            "description": "the displayed contents of the selected region."
          },
          {
            "group": "Injects",
            "type": "Int",
            "field": "line",
            "optional": false,
            "description": "the line count where the selected region located."
          },
          {
            "group": "Injects",
            "type": "Int",
            "field": "from",
            "optional": false,
            "description": "start point of region."
          },
          {
            "group": "Injects",
            "type": "Int",
            "field": "to",
            "optional": false,
            "description": "end point of region."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "message",
            "optional": false,
            "description": "the message parameter of the selected region."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "setEventReactor",
    "type": "SushiJSON",
    "url": "setEventReactor:{JSON}",
    "title": "set self-defined event reactor. run when the reactive-event/foundation-event appeared.",
    "examples": [
      {
        "title": "[example]",
        "content": "setEventReactor: {\n  \"react\": \"event_accept_event\",// you can define it. must starts with \"event_\" prefix.\n  \"reactors\": [\n      {\n          \"showAtLog\": {\n              \"message\": \"hereComes\"\n          }\n      },\n      {\n          \"showAtLog<-messageFromEventEmit\": {\n              \"format\": \"from [messageFromEventEmit]\"\n          }\n      }\n  ]\n}->eventEmit: {\n  \"messageFromEventEmit\": \"the message from eventEmit\"\n}\n"
      },
      {
        "title": "[example of receive foundation event]",
        "content": "setEventReactor: {\n  \"react\": \"ss_f_noViewFound\",\n  \"reactors\": [\n      {\n          \"showAtLog<-name\": {\n              \"message\": \"no view found\",\n              \"format\": \"view [name] not found.\"\n          }\n      }\n  ],\n  \"selectors\": [\n      {\n          \"showAtLog<-delay\": {\n              \"format\": \"[delay]\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "react",
            "optional": false,
            "description": "target event name."
          },
          {
            "group": "Parameter",
            "type": "JSON",
            "field": "reactors",
            "optional": false,
            "description": "run when target-event/foundation-event appeared."
          },
          {
            "group": "Parameter",
            "type": "Int(Optional)",
            "field": "delay",
            "optional": false,
            "description": "milliseconds. delay ignore running reactors, when the event appeared multitimes in this delay."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "JSON",
            "field": "reactors",
            "optional": false,
            "description": "reactors block."
          },
          {
            "group": "Injects",
            "type": "Int",
            "field": "delay",
            "optional": false,
            "description": "0 or inputted value."
          }
        ]
      }
    },
    "error": {
      "fields": {
        "Injects via reactors": [
          {
            "group": "Injects via reactors",
            "type": "String",
            "field": "identity",
            "optional": false,
            "description": "the generated uuid4 string for each event."
          },
          {
            "group": "Injects via reactors",
            "type": "Everything",
            "field": "keys_and_values",
            "optional": false,
            "description": "run when this event appeared. run with caller API's injects."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "setSelection",
    "type": "SushiJSON",
    "url": "setSelection:{JSON}",
    "title": "set selection to the file.",
    "examples": [
      {
        "title": "[example]",
        "content": "setSelection: {\n  \"name\": \"sample.txt\",\n  \"selections\": [\n      {\n          \"from\": 10,\n          \"to\": 11\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "the target file's last part of file path or fullpath or parts."
          },
          {
            "group": "Parameter",
            "type": "Dictionary",
            "field": "selections",
            "optional": false,
            "description": "pair of key-value of selecting regions. [from]:Int and [to]:Int"
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "Event",
            "field": "ss_on_selection_modified_by_setselection",
            "optional": false,
            "description": "the ss_on_selection_modified_by_setselection event will raise."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "path",
            "optional": false,
            "description": "selected file's path."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "selected file's name."
          },
          {
            "group": "Injects",
            "type": "Array",
            "field": "selecteds",
            "optional": false,
            "description": "the list of [from] and [to]."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "setSublimeSocketWindowBasePath",
    "type": "SushiJSON",
    "url": "setSublimeSocketWindowBasePath:{JSON}",
    "title": "set current file's path to SublimeSocketWindowBasePath param. this param is set to latest opened file's path automatically.",
    "examples": [
      {
        "title": "[example]",
        "content": "setSublimeSocketWindowBasePath: {\n  \"selectors\": [\n      {\n          \"showAtLog<-basename\": {\n              \"format\": \"[basename]\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String",
            "field": "path",
            "optional": false,
            "description": "file's path."
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "file's name."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "setViewReactor",
    "type": "SushiJSON",
    "url": "setViewReactor:{JSON}",
    "title": "set defined view-event reactor. run when the event appeared.",
    "name": "b",
    "examples": [
      {
        "title": "[example]",
        "content": "setViewReactor: {\n  \"react\": \"on_post_save\",\n  \"reactors\": [\n      {\n         \"showAtLog<-name\": {\n              \"format\": \"name is [name]\"\n          }\n      }\n  ]\n}\n"
      },
      {
        "title": "[view-events]",
        "content": "on_new\non_clone\non_close\non_load\non_modified\non_query_completions\non_pre_save\non_post_save\non_selection_modified\nss_on_selection_modified_by_setselection\nss_v_decreased\nss_v_increased\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "react",
            "optional": false,
            "description": "target event name."
          },
          {
            "group": "Parameter",
            "type": "JSON",
            "field": "reactors",
            "optional": false,
            "description": "run when target-event/foundation-event appeared."
          },
          {
            "group": "Parameter",
            "type": "Int(Optional)",
            "field": "delay",
            "optional": false,
            "description": "milliseconds. delay ignore running reactors, when the event appeared multitimes in this delay."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "JSON",
            "field": "reactors",
            "optional": false,
            "description": "reactors block."
          },
          {
            "group": "Injects",
            "type": "Int",
            "field": "delay",
            "optional": false,
            "description": "0 or inputted value."
          }
        ]
      }
    },
    "error": {
      "fields": {
        "Injects via reactors": [
          {
            "group": "Injects via reactors",
            "type": "String",
            "field": "path",
            "optional": false,
            "description": "the full path of the file. if the file is not exist, = buffer, path becomes name of buffer."
          },
          {
            "group": "Injects via reactors",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "the last path of the file."
          },
          {
            "group": "Injects via reactors",
            "type": "[[Int, Int]]",
            "field": "selecteds",
            "optional": false,
            "description": "the list of list(from, to)."
          },
          {
            "group": "Injects via reactors",
            "type": "Bool",
            "field": "isExist",
            "optional": false,
            "description": "the view is exist or not."
          },
          {
            "group": "Injects via reactors",
            "type": "String",
            "field": "identity",
            "optional": false,
            "description": "the generated uuid4 string for each event."
          },
          {
            "group": "Injects via reactors",
            "type": "ViewInstance",
            "field": "view",
            "optional": false,
            "description": "the instance of view.(not good to use. use \"name\", \"path\" to find file.)"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "showAtLog",
    "type": "SushiJSON",
    "url": "showAtLog:{JSON}",
    "title": "show message to log with prefix.",
    "examples": [
      {
        "title": "[example]",
        "content": "showAtLog: {\n  \"message\": \"Hello world\"\n}\nor\n\"showAtLog<-head, body, tail\": {\n  \"format\": \"Hello, [head], [body] and [tail]!\"\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "message",
            "optional": false,
            "description": "contents."
          },
          {
            "group": "Parameter",
            "type": "String(Optional)",
            "field": "format",
            "optional": false,
            "description": "construct string with bracket([, and ]) injected value."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "showDialog",
    "type": "SushiJSON",
    "url": "showDialog:{JSON}",
    "title": "show dialog with specific message.",
    "examples": [
      {
        "title": "[example]",
        "content": "showDialog: {\n  \"message\": \"here comes daredevil\",\n  \"selectors\": [\n      {\n          \"showAtLog<-message\": {\n           }\n      }\n  ]\n}\nor\n\"showDialog<-head, body\": {\n  \"format\": \"here comes [head] [body]\"\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "message",
            "optional": false,
            "description": "contents."
          },
          {
            "group": "Parameter",
            "type": "String(Optional)",
            "field": "format",
            "optional": false,
            "description": "construct string with bracket([, and ]) injected value."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String",
            "field": "message",
            "optional": false,
            "description": "inputted message."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "showStatusMessage",
    "type": "SushiJSON",
    "url": "showStatusMessage:{JSON}",
    "title": "show message to statusbar.",
    "examples": [
      {
        "title": "[example]",
        "content": "showStatusMessage: {\n  \"message\": \"testStatusMessage\",\n  \"debug\": true\n}\nor\n\"showStatusMessage<-head, body, tail\": {\n  \"format\": \"testStatusMessage, [head], [body], [tail]\"\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "message",
            "optional": false,
            "description": "contents."
          },
          {
            "group": "Parameter",
            "type": "String(Optional)",
            "field": "format",
            "optional": false,
            "description": "construct string with bracket([, and ]) injected value."
          },
          {
            "group": "Parameter",
            "type": "Bool(Optional)",
            "field": "debug",
            "optional": false,
            "description": "also show message into log or not. By default false."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "showToolTip",
    "type": "SushiJSON",
    "url": "showToolTip:{JSON}",
    "title": "show tooltip with titles & selectors.",
    "examples": [
      {
        "title": "[example]",
        "content": "showToolTip: {\n  \"name\": \"sample.txt\",\n  \"onselected\": [\n      {\n          \"sample!\": [\n              {\n                  \"showAtLog\": {\n                      \"message\": \"sample! selected!\"\n                  }\n              }\n          ]\n      }\n  ],\n  \"oncancelled\": [\n      {\n          \"showAtLog\": {\n              \"message\": \"sample selected!\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": "the target file's last part of file path or fullpath or parts."
          },
          {
            "group": "Parameter",
            "type": "SelectorsWithKey",
            "field": "onselected",
            "optional": false,
            "description": "titles and selectors which will be ignite when the title of tooltip selected."
          },
          {
            "group": "Parameter",
            "type": "Selectors",
            "field": "oncancelled",
            "optional": false,
            "description": "selectors which will be ignite when the tooltip cancelled."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "finally",
            "optional": false,
            "description": "selectors which will be ignite when the tooltip disappeared."
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String",
            "field": "path",
            "optional": false,
            "description": ""
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "name",
            "optional": false,
            "description": ""
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "titles",
            "optional": false,
            "description": ""
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "selectedtitle",
            "optional": false,
            "description": ""
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "startTailing(deprecated)",
    "type": "SushiJSON",
    "url": "startTailing:{JSON}",
    "title": "start tailing the target file and run reactor.",
    "examples": [
      {
        "title": "[example]",
        "content": "startTailing: {\n  \"identity\": \"startTailing\",\n  \"path\": \"SUBLIMESOCKET_PATH:tests/testResources/runShellTarget.txt\",\n  \"reactors\": [\n      {\n          \"showAtLog<-source\": {\n              \"format\": \"tailed, [source]\"\n          }\n      }\n  ],\n  \"selectors\": [\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "identity",
            "optional": false,
            "description": "identifier of this tail process.(only defined. no usage yet.)"
          },
          {
            "group": "Parameter",
            "type": "String",
            "field": "path",
            "optional": false,
            "description": "the target file path. must be full-path."
          },
          {
            "group": "Parameter",
            "type": "JSON",
            "field": "reactors",
            "optional": false,
            "description": "run when tailed-data incoming. \"source\" param will be injected."
          },
          {
            "group": "Parameter",
            "type": "Selectors",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "String",
            "field": "path",
            "optional": false,
            "description": "the tail-started file path."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "tearDown",
    "type": "SushiJSON",
    "url": "tearDown:{}",
    "title": "teardown the SublimeSocket Server itself.",
    "examples": [
      {
        "title": "[example]",
        "content": "tearDown: {}\n"
      }
    ],
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "versionVerify",
    "type": "SushiJSON",
    "url": "versionVerify:{JSON}",
    "title": "check SublimeSocket version from client.",
    "examples": [
      {
        "title": "[example]",
        "content": "versionVerify: {\n  \"socketVersion\": 3,\n  \"apiVersion\": \"1.-1.0\",\n  \"injects\": {\n      \"code\": \"code\",\n      \"message\": \"theMessage\"\n  },\n  \"selectors\": [\n      {\n          \"showAtLog<-code, theMessage\": {\n              \"format\": \"[code] [theMessage]\"\n          }\n      }\n  ]\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "String",
            "field": "socketVersion",
            "optional": false,
            "description": "the version of expected SublimeSocket version.(2 or 3)"
          },
          {
            "group": "Parameter",
            "type": "String",
            "field": "apiVersion",
            "optional": false,
            "description": "the version of expected SublimeSocket API version.(a.b.c)"
          },
          {
            "group": "Parameter",
            "type": "Selectors(Optional)",
            "field": "selectors",
            "optional": false,
            "description": "selectors."
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Injects": [
          {
            "group": "Injects",
            "type": "Int",
            "field": "code_2",
            "optional": false,
            "description": "(2) VERIFICATION_CODE_VERIFIED_CLIENT_UPDATE"
          },
          {
            "group": "Injects",
            "type": "Int",
            "field": "code_1",
            "optional": false,
            "description": "(1) VERIFICATION_CODE_VERIFIED"
          },
          {
            "group": "Injects",
            "type": "Int",
            "field": "code_0",
            "optional": false,
            "description": "(0) VERIFICATION_CODE_REFUSED_DIFFERENT_SUBLIMESOCKET"
          },
          {
            "group": "Injects",
            "type": "Int",
            "field": "code_-1",
            "optional": false,
            "description": "(-1) VERIFICATION_CODE_REFUSED_SUBLIMESOCKET_UPDATE"
          },
          {
            "group": "Injects",
            "type": "Int",
            "field": "code_-2",
            "optional": false,
            "description": "(-2) VERIFICATION_CODE_REFUSED_CLIENT_UPDATE"
          },
          {
            "group": "Injects",
            "type": "String",
            "field": "message",
            "optional": false,
            "description": "result message of verification."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  },
  {
    "group": "wait",
    "type": "SushiJSON",
    "url": "wait:{JSON}",
    "title": "wait milliseconds and go to next.",
    "examples": [
      {
        "title": "[example]",
        "content": "wait:{\n  \"ms\": 200\n}\n"
      }
    ],
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Int",
            "field": "ms",
            "optional": false,
            "description": "wait milliseconds."
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "/Users/highvision/Desktop/SublimeSocket3/SublimeSocketAPISettings.py"
  }
] });