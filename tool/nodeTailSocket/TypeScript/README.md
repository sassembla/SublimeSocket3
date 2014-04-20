#NodeTailSocket + TypeScript Filter


======
v1.1.0


![SS](/tool/nodeTailSocket/TypeScript/SublimeSocket+NodeTailSocket.png)
![SS](/tool/nodeTailSocket/TypeScript/screenshot.png)

##movie
[the quickstart usage](https://vimeo.com/91687931)


##quickstart
#####0.copy this folder to your Desktop
	
	YourDesktopOrElse/
		TypeScript/
			node_tailsocket_typescript.js
			tscwithenv.sh
			
			sample/
				src/
					Greet.ts
					deep/
						Greet2.ts
							
			README.md(this)
			and more..
				
	
	
#####1.kickstart SublimeSocket

	In Sublime Text:
	⌘ + shift + p -> SublimeSocket: on


#####2.kickstart node.js from commandline.

	node PATH_OF_PROJECT/node_tailsocket_typescript.js
	
or

	node PATH_OF_node_tailsocket_typescript.js PATH_OF_PROJECT
	
	
	
#####3.Open Greet.ts in Sublime Text

#####4.Do SAVE(command + s) action, system automatically starts compiling and show error if exist.



That's all.

##Compile TypeScript with SublimeText + SublimeSocket + Node.js + tsc


This feature depends on **node.js** and these packages.

* ws
* tail
* typescript

Also depends on SublimeSocket(This repo).


##ready project folder:
This feature compiles all *.ts" files which are located under the project folder.

	project/
		src_folder/
			*.ts
			other_folder/
				*.ts
				...
		
If you wanna change compilation behavior, please modify **tscwithenv.sh**.


##troubleShooting

1.compile never end:
	
	Maybe the path of tsc is wrong.
	By default the tsc path is defined as "/usr/local/bin/tsc" in the tscwithenv.sh .
