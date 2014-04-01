beforeafter>SSではなく、プロトコル切り替え部分について、自動化とテストを行う。/selector: {
    "beforeselectors": [
        {
            "showAtLog": {
                "message": "start test"
            }
        }
    ],
    "afterselectors": [
        {
            "showAtLog": {
                "message": "test over"
            }
        }
    ]
}


test>add new WebSocketServer transfer/afterAsync: {
    "identity": "addTransfer",
    "ms": 1,
    "selectors":[
        {
            "addTransfer": {
                "transferIdentity": "testAdditionalWebSocket",
                "connectionIdentity": "testAdditionalConnection",
                "protocol": "WebSocketServer",
                "params": {
                    "host": "127.0.0.1",
                    "port": 8824
                },
                "selectors": [
                    {
                        "showAtLog<-transferIdentity": {
                            "format": "transfer [transferIdentity] added."
                        }
                    }
                ]
            }
        },
        {
            "wait in same thread./assertResult": {
                "id": "websocketServer added",
                "contains": {
                    "showAtLog": {
                        "output": "transfer testAdditionalWebSocket added."
                    }
                },
                "description": "not match."
            }
        }
    ]
}->wait: {
    "ms": 100
}->removeTransfer: {
    "transferIdentity": "testAdditionalWebSocket"
}->wait: {
    // wait for sending result to WebSocketClient. because of latency of WebSocketServer.
    "ms": 10
}


test>oneShotのrunSushiJSONのrunnerをaddTransferで生成する/addTransfer: {
    "transferIdentity": "testAdditionalSushiJSONServer",
    "connectionIdentity": "testAdditionalSushiJSONConnection",
    "protocol": "RunSushiJSONServer",
    "params": {
        "path": "SUBLIMESOCKET_PATH:tests/testResources/sample_SushiJSON.txt"
    },
    "selectors": [
        {
            "showAtLog<-transferIdentity": {
                "format": "transfer [transferIdentity] added."
            }
        }
    ]
}->wait: {
    "ms": 100
}->assertResult: {
    "id": "oneshot-runSushiJSONServer added",
    "contains": {
        "showAtLog": {
            "output": "transfer testAdditionalSushiJSONServer added."
        }
    },
    "description": "not match."
}->removeTransfer: {
    "transferIdentity": "testAdditionalSushiJSONServer"
}


test>continuationのあるrunSushiJSONのrunnerをaddTransferで生成する/afterAsync: {
    "identity": "continue-runSushiJSONServer",
    "ms": 1,
    "selectors": [
        {
            "addTransfer": {
                "transferIdentity": "testAdditionalSushiJSONServer2",
                "connectionIdentity": "testAdditionalSushiJSONConnection",
                "protocol": "RunSushiJSONServer",
                "params": {
                    "path": "SUBLIMESOCKET_PATH:tests/testResources/sample_SushiJSON.txt",
                    "continuation": true
                },
                "selectors": [
                    {
                        "showAtLog<-transferIdentity": {
                            "format": "transfer [transferIdentity] added."
                        }
                    }
                ]
            }
        },
        {
            "assertResult": {
                "id": "continue-runSushiJSONServer added",
                "contains": {
                    "showAtLog": {
                        "output": "transfer testAdditionalSushiJSONServer2 added."
                    }
                },
                "description": "not match."
            }
        }
    ]
}->wait: {
    "ms": 100
}->removeTransfer: {
    "transferIdentity": "testAdditionalSushiJSONServer2"
}->wait: {
    // wait for sending result to WebSocketClient. because of latency of runSushiJSONServer.
    "ms": 200
}


test>httpServerを上げて下げる/afterAsync: {
    "identity": "for testAdditionalHTTPServer",
    "ms": 10,
    "selectors": [
        {
            "addTransfer": {
                "transferIdentity": "testAdditionalHTTPServer",
                "connectionIdentity": "testAdditionalHTTPConnection",
                "protocol": "HTTPServer",
                "params": {
                    "host": "127.0.0.1",
                    "port": 8825
                },
                "selectors": [
                    {
                        "showAtLog<-transferIdentity": {
                            "format": "httpServer [transferIdentity] added."
                        }
                    }
                ]
            }
        },
        {
            "assertResult": {
                "id": "httpServer added.",
                "contains": {
                    "showAtLog": {
                        "output": "httpServer testAdditionalHTTPServer added."
                    }
                },
                "description": "not match."
            }
        }
    ]
}->wait: {
    "ms": 100
}->removeTransfer: {
    "transferIdentity": "testAdditionalHTTPServer"
}->wait: {
    "ms": 10
}


test>PROTOCOL_BYTEDATA_SERVERを一つ立てて、消す/afterAsync: {
    "identity": "addTransfer",
    "ms": 1,
    "selectors":[
        {
            "addTransfer": {
                "transferIdentity": "byteDataServer",
                "connectionIdentity": "byteDataConnection",
                "protocol": "ByteDataServer",
                "params":{
                    "binders": [
                        {
                            "<policy-file-request/>":"<?xml version=\"1.0\"?><cross-domain-policy><allow-access-from domain=\"*\" to-ports=\"*\"/></cross-domain-policy>"
                        }
                    ],
                    "host": "127.0.0.1",
                    "port": 8824
                },
                "selectors": [
                    {
                        "showAtLog<-transferIdentity": {
                            "format": "transfer [transferIdentity] added."
                        }
                    }
                
                ]
            }
        },
        {
            "wait in same thread./assertResult": {
                "id": "websocketServer added",
                "contains": {
                    "showAtLog": {
                        "output": "transfer byteDataServer added."
                    }
                },
                "description": "not match."
            }
        }
    ]
}->wait: {
    "ms": 100
}->removeTransfer: {
    "transferIdentity": "byteDataServer"
}->wait: {
    // wait for sending result to WebSocketClient. because of latency of WebSocketServer.
    "ms": 10
}






