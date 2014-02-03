assert "selecteditem" in inputs, "not included in:"+str(inputs)

selectedItemName = inputs["selecteditem"]

output({"source":selectedItemName})