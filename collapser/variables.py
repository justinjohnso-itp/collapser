
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

	def getGroupFromVar(self, key):
		for groupKey, groupVal in self.varGroups.iteritems():
			if key in groupVal:
				return groupKey
		return ""

	# [ @alpha> A ]
	# [ @alpha> A | B ]
	# [ @alpha> | B ]
	# [ @alpha> A | @beta> B]
	# TODO This should be invalid: [ B | @alpha> A ]

	def render(self, tokens, params):
		pos = 0

		# First ensure all vars are in same control group
		varCtrlGroup = ""
		while pos < len(tokens):
			if tokens[pos].type == "VARIABLE":
				varName = tokens[pos].value
				thisCtrlGroup = self.getGroupFromVar(varName)
				if varCtrlGroup == "":
					varCtrlGroup = thisCtrlGroup
				elif varCtrlGroup != thisCtrlGroup:
					raise ValueError("Found variables from different groups in tokenstream '%'" % tokens)
			pos += 1

		# Now figure out how to render.
		pos = 0
		while pos < len(tokens):
			# For this group, if we have only text, this is an alternative where nothing previous matched; we should return it.
			if tokens[pos].type == "TEXT":
				return tokens[pos].value

			if tokens[pos].type == "DIVIDER":
				pos += 1
				continue

			#Otherwise, we must be at a variable.
			assert tokens[pos].type == "VARIABLE"
			varName = tokens[pos].value
			pos += 1

			# A variable can be followed by either text, or a divider or end of the stream. If text, return the text if that variable is true.
			if tokens[pos].type == "TEXT":
				if self.check(varName):
					return tokens[pos].value

			# If it's a divider, return an empty string if the variable is true.
			elif tokens[pos].type == "DIVIDER":
				if self.check(varName):
					return ""

			pos += 1

		return ""



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

