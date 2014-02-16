Sushi:{JSON}
======
	╔═╗┬ ┬┌─┐┬ ┬┬
	╚═╗│ │└─┐├─┤│ : {JSON}
	╚═╝└─┘└─┘┴ ┴┴

The partial-parse-designed DSL which contains JSON with naming rule.  
Mainly made for controlling the text editor. like the **Sublime Text**, **Vim**, and the other.


##example

	defineFilter: {
    	"name": "error_example",
	    "patterns": [
    	    {
            	"(.*)[(]([0-9].*?),.*[)]: error .*: (.*)": {
            		"injects": {
            			"groups[0]": "filename",
            			"groups[1]": "line",
            			"groups[2]": "reason",
            		},
                	"selectors": [
                		{
                			"showAtLog<-filename, line, reason": {
                				"format": "ERROR: on [filename]:[line] [reason]"
                			}
                		}
                	]
                }
            }
        ]
	}->filtering: {
		"name": "error_example",
		"source": "Somewhere/Something.cs(30,23): error CS1002: Expecting `;'"
	}



##expressions

standard:

	APIName: {JSON}
	
orderd:

	APIName: {JSON}->APIName: {JSON}

nested:
	
	APIName: {
		"selectors": [
			{
				"APIName": {JSON}
			}
		]
	}

nested & accepts:
	
	APIName: {
		"selectors <- param": [
			{
				"APIName": {JSON}
			}
		]
	}


nested, injects & accepts:
	
	APIName: {
		"injects": {
			"result": "param"
		},
		"selectors <- param": [
			{
				"APIName": {JSON}
			}
		]
	}

## features

#####JSON inside. 

	filtering: {
		"name": "error_example",
		"source": "Somewhere/Something.cs(30,23): error CS1002: Expecting `;'"
	}

The below part is purely JSON. and this works as attaching parameters to the API.

	{
		"name": "error_example",
		"source": "Somewhere/Something.cs(30,23): error CS1002: Expecting `;'"
	}
	
	
Same in Python,

	filtering(name="error_example", source="Somewhere/Something.cs(30,23): error CS1002: Expecting `;'");

Each API can be defined these parameter keys and values,  
and it's easy to add specific keys and values too.

#####Ordered and separeted.
**[ -> "right arrow" ]** rules the order of execution and cannot sent parameter between the **[ -> ]**.

	showAtLog: {
		"message": "1st"
	}->showAtLog: {
		"message": "2nd"
	}
	
in JSON part the **[ -> ]** is described as "**selectors**" phrase.

	"selectors": [
		{
			"showAtLog": {
				"message": "Hello world"
			}
		},
		{
			"showAtLog": {
				"and see you tomorrow."
			}
		}
	]
                
Each "showAtLog" command has no relationship & no parameter sharing over [ -> ].

Anyway, you can evaluate each JSON **partially** on the runtime.


#####injects & accepts

**[ <- "left arrow" ]** means "this API accepts the named-value from the result of parent-API".

	parentAPIName: {
		"selectors": [
			{
				"childAPIName <- key_of_parentAPI's_result": {
					// implicitly accept the param,
					// "key_of_parentAPI's_result": "value_of_parentAPI's_result"
				}
			}
		]
	}



"injects" keyword makes change the key of the result of the parentAPI.

each API has results. these are implicitly inject to "selectors" API.

	APIName: {
		"injects": {
			"key_of_result": "new_key_of_result"
		},
		
		"selectors": [
			{
				"childAPIName <- new_key_of_result": {
					// implicitly accept the param,
					// "new_key_of_result": "value_of_parentAPI's_result"
				}
			}
		]
	}




This feature can be use for injecting the original parameter, like below.

	APIName: {
		"original_key": "original_value",
		
		"injects": {
			"original_key": "new_key_of_original_value"
		},
		
		"selectors": [
			{
				"childAPIName <- new_key_of_original_value": {
					// implicitly accept the param,
					// "new_key_of_original_value": "original_value"
				}
			}
		]
	}
	

[ <- ] with no key name means "accept everything from parentAPI".

	parentAPIName: {
		"key1": "value1",
		"key2": "value2",
		
		"injects": {
			"key1": "key1",
			"key2": "key2"
		},
		
		"selectors": [
			{
				"childAPIName <-": {
					// implicitly accept all params from parent,
					// "key1": "value1",
					// "key2": "value2"
				}
			}
		]
	}
	
