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


// 実行フェーズがどうしてもSS側に来ちゃうのをどうしようかなー感がある。
// httpサーバを上げて下げる
// test>addTransfer: {
//     "identity": "testHttpServer",
//     "protocol": "http",
//     "params": {
//         "serve": "127.0.0.1",
//         "port": "8823"
//     }
// }


// まずはWebSocketServerを増やすことを考える。っていうかhttpのサーバとwebsocketのサーバって共有できるの？出来そうだけどそれって分派するとしたらかなり限られるのでは？
// 最悪内部でルーティングする感じ？
// とりあえず同じipが振れるかどうか試してみるか。多分無理。
test>addTransfer: {
    "transferIdentity": "testAdditionalWebSocket",
    "connectionIdentity": "testAdditionalConnection",
    "protocol": "ws",
    "params": {
        "serve": "127.0.0.1",
        "port": "8824"
    }
}

