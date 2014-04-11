#TypeScript Filter


======
![SS](/tool/nodeTailSocket/SublimeSocket+NodeTailSocket.png)
![SS](/tool/nodeTailSocket/screenshot.png)

##Compile TypeScript with SublimeText + SublimeSocket + Node.js + tsc


This feature depends on **node.js** and these packages.

* ws
* tail
* typescript

Also depends on SublimeSocket(This repo).


##ready project folder:
This feature compiles *.ts which are in the single folder by default.

And you need to prepare empty "tscompile.log" file in the folder too.

	sample/
		*.ts
		
		tscompile.log //<- need it!
		

##ignite

#####1.kickstart SublimeSocket

	In Sublime Text:
	⌘ + shift + p -> SublimeSocket: on


#####2.kickstart node.js from commandline.

	node node_tailsocket_typescript.js tscwithenv.sh FOLDER_PATH_OF_sample
	
	
#####3.Start compiling and show error if exist after SAVE(command + s) action.



That's all.

