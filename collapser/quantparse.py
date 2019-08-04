
# Array of chunks. Each chunk is either text or a control sequence. A control sequence might have metadata and also a payload, which is an array of textons that each can have their own metadata. 



import macros
import variables
import ctrlseq
import chooser

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
		return "chooseStrategy: %s, preferenceForAuthorsVersion: %s, setDefines: %s" % (self.chooseStrategy, self.preferenceForAuthorsVersion, self.setDefines)

	def copy(self):
		return ParseParams(chooseStrategy=self.chooseStrategy, preferenceForAuthorsVersion=self.preferenceForAuthorsVersion, setDefines=list(self.setDefines))


# Call with an object of type ParseParams.
def parse(tokens, parseParams):
	print "** PARSING **"
	if parseParams.chooseStrategy == "longest":
		print "Calculating longest defines (ignoring seed)..."
		print parseParams
		longerDefines = []

		# Process all the DEFINEs in the code, with a copy of everything.
		variables.reset()
		macros.reset()
		tempTokens = list(tokens)
		tempTokens = variables.handleDefs(tempTokens, parseParams)
		tempTokens = macros.handleDefs(tempTokens, parseParams)

		# Now for each option in a define group, see which one makes the longest text.
		for info in variables.groups():
			optsToTry = list(info)
			# If just one option, we want to try it as True and False.
			if len(optsToTry) is 1:
				optsToTry.append("!" + optsToTry[0])
			print "optsToTry: %s" % optsToTry

			longestPos = -1
			longestLen = -1
			for pos, key in enumerate(optsToTry):
				parseParamsCopy = parseParams.copy()
				parseParamsCopy.setDefines.append(key)
				chooser.unSeed()

				oldVal = ""
				if key[0] != "!":
					oldVal = variables.__v.variables[key]
					variables.__v.variables[key] = True
				else:
					oldVal = variables.__v.variables[key[1:]]
					variables.__v.variables[key[1:]] = False

				testRender = handleParsing(tempTokens, parseParamsCopy)

				variables.__v.variables[key] = oldVal

				thisLen = len(testRender)
				if thisLen > longestLen:
					longestPos = pos
					longestLen = thisLen

				print "for %s, len=%d" % (key, thisLen)

			print "Longest was %s at %d" % (optsToTry[longestPos], longestLen)
			longerDefines.append(optsToTry[longestPos])

		print "Longest: %s" % longerDefines
		parseParams.setDefines = longerDefines
		print "parseParams is now: %s" % parseParams

	variables.reset()
	macros.reset()
	tokens = variables.handleDefs(tokens, parseParams)
	tokens = macros.handleDefs(tokens, parseParams)
	renderedString = handleParsing(tokens, parseParams)
	return renderedString


def handleParsing(tokens, params):
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



