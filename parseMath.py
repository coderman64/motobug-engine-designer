
# a simple function for parsing and executing math-based strings
# doesn't use eval(), so problems don't happen
def parseMath(string):
    currentValue = ""
    valueStack = []
    for i in string:
        if i in "+-*/":
            if all([i in "1234567890." for i in currentValue]) and not currentValue == "":
                valueStack.append(float(currentValue))
                valueStack.append(i)
                currentValue = ""
            else:
                raise ValueError("Malformed math string")
        elif not i == " ":
            currentValue += i
    if currentValue != "":
        valueStack.append(float(currentValue))
    #print(valueStack)
    for i in "*/+-":
        while valueStack.count(i) > 0:
            index = valueStack.index(i)
            valueStack.pop(index)
            valueA = valueStack.pop(index-1)
            valueB = valueStack.pop(index-1)
            if i == "*":
                #print("%f * %f = %f" %(valueA,valueB,valueA*valueB))
                valueStack.insert(index-1,valueA*valueB)
            elif i == "/":
                #print("%f / %f = %f" %(valueA,valueB,valueA/valueB))
                valueStack.insert(index-1,valueA/valueB)
            elif i == "+":
                #print("%f + %f = %f" %(valueA,valueB,valueA+valueB))
                valueStack.insert(index-1,valueA+valueB)
            elif i == "-":
                #print("%f - %f = %f" %(valueA,valueB,valueA-valueB))
                valueStack.insert(index-1,valueA-valueB)
    return valueStack[0]

        