# SublimeSocket
======
![SS](/main.png)

**The set of API Server, KVS and Executor** for the SublimeText and more.   
Connect something to editor.  
Control EditorAPI by inputted **JSON string**.  

You can construct **the chain of filters and events** that you want to do. 

ver 1.4.1


##demos
* [Ruby show runtime error sample](https://vimeo.com/62957311)

* [Work with Unity	:	Build and show parameters and errors](https://vimeo.com/62957311)  
* [Work with TypeScript	:	Build and show errors with Chrome Ext](https://vimeo.com/63188211)  



##usage: CommandPalette >  
start WebSocket server

	SublimeSocket: on
	
	start serving ws at http://localhost:8823 by default.

show status
	
	SublimeSocket: status
	
	show SublimeSocket's status and list current connections name.

test

	SublimeSocket: on > test
	
	show SublimeSocket's status and current connections.
	
teardown

	SublimeSocket: off
	
	teardown.


#Purpose/Motivation
* Control SublimeText API from the other process, data, input.
* Pick out all heavy-process from SublimeText to the outside & keep async.


#Next
* Atom adopt.