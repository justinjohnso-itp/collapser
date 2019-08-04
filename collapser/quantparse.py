
# Array of chunks. Each chunk is either text or a control sequence. A control sequence might have metadata and also a payload, which is an array of textons that each can have their own metadata. 



import macros
import variables
import ctrlseq

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
			rendered = ctrlseq.render(ctrl_contents, parseParams)

		output.append(rendered)
		
		index += 1

	return output



