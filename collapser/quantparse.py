
# Array of chunks. Each chunk is either text or a control sequence. A control sequence might have metadata and also a payload, which is an array of textons that each can have their own metadata. 



from quantlex import tokens
import chooser
import macros
import variables

import sys


class ParseParams:

	VALID_STRATEGIES = ["random", "author", "longest"]

	def __init__(self, chooseStrategy="random", preferenceForAuthorsVersion=25, setDefines=[]):
		if chooseStrategy not in self.VALID_STRATEGIES:
			raise ValueError("Unrecognized choose strategy '%s'" % chooseStrategy)
		self.chooseStrategy = chooseStrategy
		self.preferenceForAuthorsVersion = preferenceForAuthorsVersion
		self.setDefines = setDefines

	def __str__(self):
		return "chooseStrategy: %s, preferenceForAuthorsVersion: %s" % (self.chooseStrategy, self.preferenceForAuthorsVersion)

	def copy(self):
		return ParseParams(chooseStrategy=self.chooseStrategy, preferenceForAuthorsVersion=self.preferenceForAuthorsVersion, setDefines=list(self.setDefines))


# Call with an object of type ParseParams.
def parse(tokens, parseParams):
	# print "** PARSING **"
	# if parseParams.chooseStrategy == "longest":
	# 	sys.stdout.write("Calculating longest defines...")
	# 	longerDefines = []
	# 	ts = list(tokens)
	# 	handleDefines(ts, parseParams)
	# 	for key in variables:
	# 		pp = parseParams.copy()
	# 		pp.setDefines.append(key)
	# 		testRender = handleParsing(tokens, pp)
	# 		lenWith = len(testRender)
	# 		pp = parseParams.copy()
	# 		pp.setDefines.append("!" + key)
	# 		testRender = handleParsing(tokens, pp)
	# 		lenWithout = len(testRender)
	# 		print "for %s: with=%d, without=%d" % (key, lenWith, lenWithout)
	# 		if lenWith > lenWithout:
	# 			longerDefines.append(key)
	# 		else:
	# 			longerDefines.append("!" + key)
	# 	parseParams.setDefines = longerDefines
	# 	print longerDefines

	renderedString = handleParsing(tokens, parseParams)
	return renderedString


def handleParsing(origtokens, params):
	variables.reset()
	macros.reset()
	tokens = variables.handleDefs(origtokens, params)
	tokens = macros.handleDefs(tokens, params)
	renderedChunks = process(tokens, params)
	renderedString = ''.join(renderedChunks)
	renderedString = macros.expand(renderedString, params)
	return renderedString



# Create a class to store possible text alternatives we might print, and handle choosing an appropriate one.

class Alts:

	def __init__(self):
		self.alts = []
		self.authorPreferredPos = 0
		self.probabilityTotal = 0

	def add(self, txt, prob=None):
		self.alts.append(Item(txt, prob, False))
		if prob is not None:
			self.probabilityTotal += prob
			if self.probabilityTotal > 100:
				raise ValueError("Probabilities in ctrl sequence add up to %d which is > 100: '%s'" % (self.probabilityTotal, self))
		# print "Adding alt: list is now %s" % self

	def setAuthorPreferred(self):
		self.authorPreferredPos = len(self.alts)

	def getAuthorPreferred(self):
		return self.alts[self.authorPreferredPos].txt

	def getRandom(self):
		if self.probabilityTotal == 0:
			return chooser.oneOf(self.alts).txt
		else:
			return chooser.distributedPick(self.alts)

	def getLongest(self):
		longestPos = -1
		longestLength = -1
		for pos, alt in enumerate(self.alts):
			length = len(alt.txt)
			if length > longestLength:
				longestLength = length
				longestPos = pos
		return self.alts[longestPos].txt

	def __len__(self):
		return len(self.alts)

	def __str__(self):
		output = []
		for pos, item in enumerate(self.alts):
			ap = "^" if pos == self.authorPreferredPos else ""
			output.append("%s%s" % (ap, item))
		return str(output)

		# return str(list(map(lambda x: "%s%s" % ("^", x), self.alts)))

# Create a class for a single text item with probability.

class Item:
	def __init__(self, txt, prob, authorPreferred):
		self.txt = txt
		self.prob = prob
		self.authorPreferred = authorPreferred

	def __str__(self):
		base = "%s%s" % ("^" if self.authorPreferred else "", self.txt)
		if self.prob is not None:
			return "%s>%s" % (self.prob, base)
		return base
		

# A chunk will be one alternative and metadata: "alpha", "80>alpha", "45>^", "". This is always in a context where we have multiple possibilities.
def parseItem(altBits):
	index = 0
	text = ""
	ap = False
	prob = None
	while index < len(altBits):
		token = altBits[index]
		if token.type in ("TEXT", "VARIABLE"):
			text = token.value
		elif token.type == "AUTHOR":
			ap = True
		elif token.type == "NUMBER":
			prob = token.value
		else:
			raise ValueError("Unhandled token %s: '%s'" % (token.type, token.value))		
		index += 1

	return Item(text, prob, ap)




# The lexer should have guaranteed that we have a series of TEXT tokens interspersed with sequences of others nested between CTRLBEGIN and CTRLEND with no issues with nesting or incomplete tags.
def process(tokens, parseParams):
	output = []
	index = 0
	while index < len(tokens):
		token = tokens[index]
		rendered = ""
		if token.type == "TEXT":
			rendered = token.value
		elif token.type == "CTRLBEGIN":
			ctrl_contents = []
			index += 1
			token = tokens[index]
			while token.type != "CTRLEND":
				ctrl_contents.append(token)
				index += 1
				token = tokens[index]
			rendered = renderControlSequence(ctrl_contents, parseParams)

		output.append(rendered)
		
		index += 1

	return output


# We have a series of tokens for a control sequence, everything between (and excluding) the square brackets. Each token has .type and .value.

def renderControlSequence(tokens, params):

	# Handle []
	if len(tokens) == 0:
		return ""

	if tokens[0].type == "VARIABLE":
		return variables.render(tokens, params)

	alts = Alts()

	# [text] means a random chance of "text" or "", but if authorPreferred is true, never show it.
	if len(tokens) == 1 and tokens[0].type == "TEXT":
		alts.add("")
		if params.chooseStrategy != "author":
			alts.add(tokens[0].value)

	# [^text] means always show the text if authorPreferred is true.
	elif len(tokens) == 2 and tokens[0].type == "AUTHOR" and tokens[1].type == "TEXT":
		alts.add(tokens[1].value)
		if params.chooseStrategy != "author":
			alts.add("")

	# [~always print this]
	elif len(tokens) == 2 and tokens[0].type == "ALWAYS" and tokens[1].type == "TEXT":
		alts.add(tokens[1].value)

	else:
		# We have a series of alternates which we want to handle individually.
		index = 0
		numDividers = 0
		while index < len(tokens):

			thisAltBits = []

			endBit = False
			while not endBit and index < len(tokens):
				token = tokens[index]
				endBit = token.type == "DIVIDER"
				if not endBit:
					thisAltBits.append(token)
					index += 1

			item = parseItem(thisAltBits)
			if item.authorPreferred:
				alts.setAuthorPreferred()
			alts.add(item.txt, item.prob)

			index += 1

		if token.type == "DIVIDER":
			alts.add("")

	if params.chooseStrategy == "longest":
		return alts.getLongest()
	elif params.chooseStrategy == "author" or chooser.percent(params.preferenceForAuthorsVersion):
		result = alts.getAuthorPreferred()
	else:
		result = alts.getRandom()
	return result

