
import quantparse
import chooser

variables = {}

# Note that this can be false EITHER if the variable has never been defined OR if it was set to false.
def checkVar(key):
	global variables
	if key in variables:
		return variables[key]
	return False

def showVars():
	global variables
	return variables.keys()

def reset():
	global variables
	variables = {}

def render(tokens, params):
	assert tokens[0].type == "VARIABLE"
	varName = tokens[0].value
	if tokens[1].type == "TEXT":
		# [@test>text]
		text = tokens[1].value
		if checkVar(varName):
			return text
		if len(tokens) == 2:
			return ""
		# [@test>text1|text2]
		assert tokens[2].type == "DIVIDER"
		assert tokens[3].type == "TEXT"
		return tokens[3].value
	else:
		# [@test>|text]
		assert tokens[1].type == "DIVIDER"
		assert len(tokens) == 3
		text = tokens[2].value
		if checkVar(varName):
			return ""
		return text


# Store all DEFINE definitions in "variables" and strip them from the token stream.
def handleDefs(tokens, params):
	output = []
	index = 0
	global variables
	while index < len(tokens):
		foundAuthorPreferred = False
		token = tokens[index]
		if token.type != "CTRLBEGIN":
			output.append(token)
			index += 1
			continue
		index += 1
		token = tokens[index]
		if token.type != "DEFINE":
			output.append(tokens[index-1])
			output.append(token)
			index += 1
			continue
		index += 1
		token = tokens[index]
		alts = quantparse.Alts()
		probTotal = 0
		foundSetDefine = False
		while token.type != "CTRLEND":
			ctrl_contents = []
			while token.type not in ["DIVIDER", "CTRLEND"]:
				ctrl_contents.append(token)
				index += 1
				token = tokens[index]
			item = quantparse.parseItem(ctrl_contents)
			assert tokens[index-1].type == "VARIABLE"
			if item.txt in variables:
				raise ValueError("Variable '@%s' is defined twice." % item.txt)
			if item.txt in params.setDefines:
				variables[item.txt] = True
				foundSetDefine = True
			elif "!" + item.txt in params.setDefines:
				variables[item.txt] = False
				foundSetDefine = True
			else:
				if item.authorPreferred:
					foundAuthorPreferred = True
					alts.setAuthorPreferred()
				if item.prob:
					probTotal += item.prob
				alts.add(item.txt, item.prob)
				variables[item.txt] = False

			if token.type == "DIVIDER":
				index += 1 
				token = tokens[index]

		if not foundSetDefine:
			if probTotal != 0 and probTotal != 100:
				raise ValueError("Probabilities in a DEFINE must sum to 100: found %d instead. '%s'" % (probTotal, alts))
			if params.chooseStrategy == "author" and len(alts) == 1 and not foundAuthorPreferred:
				varPicked = alts.getAuthorPreferred()
				variables[varPicked] = False
			elif params.chooseStrategy == "author" or chooser.percent(params.preferenceForAuthorsVersion):
				varPicked = alts.getAuthorPreferred()
				variables[varPicked] = True
			# TODO: Figure out how to do Defines with longest/shortest
			elif len(alts) == 1:
				varPicked = alts.getRandom()
				variables[varPicked] = chooser.percent(50)
			else:
				varPicked = alts.getRandom()
				variables[varPicked] = True

		index += 1 # skip over final CTRLEND
	return output

