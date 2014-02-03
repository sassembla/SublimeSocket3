# toolTipを生成する
assert "path" in inputs and "selectedBody" in inputs, "not contained necessary parameters."+str(keys)

import os

path = inputs["path"]

name = os.path.basename(path)

selectedBody = inputs["selectedBody"]
lines = [selectedBody, selectedBody, selectedBody]

# create onselected
onselected = []


for line in lines:
	selectorContents = {"showAtLog":{"message":"here comes "+ line +" as a daredevil!!"}}

	selector = {}
	selector[line] = []
	selector[line].append(selectorContents)
	onselected.append(selector)

# create on cancelled
oncancelled = []
cancelSelector = {"showAtLog":{"message":"cancelled"}}
oncancelled.append(cancelSelector)

output({"name":name, "onselected":onselected, "oncancelled":oncancelled})