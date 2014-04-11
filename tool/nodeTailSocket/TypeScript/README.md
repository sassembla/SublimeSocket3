#NodeTailSocket + TypeScript Filter


======
![SS](/tool/nodeTailSocket/TypeScript/SublimeSocket+NodeTailSocket.png)
![SS](/tool/nodeTailSocket/TypeScript/screenshot.png)

##Compile TypeScript with SublimeText + SublimeSocket + Node.js + tsc


This feature depends on **node.js** and these packages.

* ws
* tail
* typescript

Also depends on SublimeSocket(This repo).


##ready project folder:
This feature compiles *.ts which are located in the **single folder by default**.

And you need to prepare empty "tscompile.log" file in the folder too.

	sample/
		*.ts
		
		tscompile.log //<- need it!
		
If you wanna compile more huge project, you can modify **tscwithenv.sh**.

##ignite

#####1.kickstart SublimeSocket

	In Sublime Text:
	⌘ + shift + p -> SublimeSocket: on


#####2.kickstart node.js from commandline.

	node node_tailsocket_typescript.js tscwithenv.sh FOLDER_PATH_OF_sample
	
	
#####3.Start compiling and show error if exist after SAVE(command + s) action.



That's all.


##troubleShooting

1.compile never end:
	
	Maybe the path of tsc is wrong.
	By default the tsc path is defined as "/usr/local/bin/tsc" in the tscwithenv.sh .
	You should change it.
	
