# SublimeSocket
======
![SS](/main.png)

**The set of API Server, KVS and Executor** for the SublimeText3.   
Connect something to editor.  
Control EditorAPI by inputted **JSON string**.  

You can construct **the chain of filters and events** that you want to do. 

ver 1.4.1


##demos & samples
* [**TypeScript**: show runtime error on code sample](https://vimeo.com/88961966) 
	[tool/nodeTailSocket/TypeScript](https://github.com/sassembla/SublimeSocket3/tree/master/tool/nodeTailSocket/TypeScript)
	
* [**Work with Unity**	:Build and show parameters and errors](https://vimeo.com/71323225)  


##installation
1. DL.
2. move SublimeSocket3 folder to Sublime Text 3's packages folder.
3. that's all.


##usage: CommandPalette >  
start WebSocket server

	SublimeSocket: on
	
	start serving ws at http://localhost:8823 by default.

show status
	
	SublimeSocket: status
	
	show SublimeSocket's status and list current connections name.

test

	SublimeSocket: on > test
	
	run SublimeSocket's test on current view.
	
teardown

	SublimeSocket: off
	
	teardown.

##APIs
now loading...


##Purpose/Motivation
* Control SublimeText API from the other process, data, input.
* Pick out all heavy-process from SublimeText to the outside & keep async.


##Next
* Atom adopt.