
import ctrlseq
import chooser

class Variables:
	def __init__(self):
		self.variables = {}
		self.varGroups = {}   # key=groupname, val=array of var keys in that group

	# Note that this can be false EITHER if the variable has never been defined OR if it was set to false.
	def check(self, key):
		if key in self.variables:
			return self.variables[key]
		return False

	def set(self, groupname, key, val = True):
		self.variables[key] = val
		if groupname not in self.varGroups:
			self.varGroups[groupname] = []
		if key not in self.varGroups[groupname]:
			self.varGroups[groupname].append(key)

	def render(self, tokens, params):
		assert tokens[0].type == "VARIABLE"
		varName = tokens[0].value
		if tokens[1].type == "TEXT":
			# [@test>text]
			text = tokens[1].value
			if self.check(varName):
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
			if self.check(varName):
				return ""
			return text


__v = Variables()

def showVars():
	global __v
	return __v.variables.keys()

def showGroups():
	global __v
	return __v.varGroups

def reset():
	global __v
	__v = Variables()

def setAllTo(val):
	global __v
	for key in __v.variables:
		__v.variables[key] = val

def render(tokens, params):
	global __v
	return __v.render(tokens, params)

def check(key):
	global __v
	return __v.check(key)


# Store all DEFINE definitions in "variables" and strip them from the token stream.
def handleDefs(tokens, params):
	output = []
	index = 0
	global __v
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
		alts = ctrlseq.Alts()
		probTotal = 0
		foundSetDefine = False
		groupName = "group%d" % chooser.iter("groups")
		while token.type != "CTRLEND":
			ctrl_contents = []
			while token.type not in ["DIVIDER", "CTRLEND"]:
				ctrl_contents.append(token)
				index += 1
				token = tokens[index]
			item = ctrlseq.parseItem(ctrl_contents)
			assert tokens[index-1].type == "VARIABLE"
			if item.txt in __v.variables:
				raise ValueError("Variable '@%s' is defined twice." % item.txt)
			if item.txt in params.setDefines:
				__v.set(groupName, item.txt)
				foundSetDefine = True
			elif "!" + item.txt in params.setDefines:
				__v.set(groupName, item.txt, False)
				foundSetDefine = True
			else:
				if item.authorPreferred:
					foundAuthorPreferred = True
					alts.setAuthorPreferred()
				if item.prob:
					probTotal += item.prob
				alts.add(item.txt, item.prob)
				__v.set(groupName, item.txt, False)

			if token.type == "DIVIDER":
				index += 1 
				token = tokens[index]

		if not foundSetDefine:
			if probTotal != 0 and probTotal != 100:
				raise ValueError("Probabilities in a DEFINE must sum to 100: found %d instead. '%s'" % (probTotal, alts))
			if params.chooseStrategy == "author" and len(alts) == 1 and not foundAuthorPreferred:
				varPicked = alts.getAuthorPreferred()
				__v.set(groupName, varPicked, False)
			elif params.chooseStrategy == "author" or chooser.percent(params.preferenceForAuthorsVersion):
				varPicked = alts.getAuthorPreferred()
				__v.set(groupName, varPicked)
			# TODO: Figure out how to do Defines with longest/shortest
			elif len(alts) == 1:
				varPicked = alts.getRandom()
				__v.set(groupName, varPicked, chooser.percent(50))
			else:
				varPicked = alts.getRandom()
				__v.set(groupName, varPicked)

		index += 1 # skip over final CTRLEND
	return output

