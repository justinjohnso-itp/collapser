
# Array of chunks. Each chunk is either text or a control sequence. A control sequence might have metadata and also a payload, which is an array of textons that each can have their own metadata. 



import macros
import variables
import ctrlseq
import chooser
import result
import confirm
import discourseVars

import sys


class ParseParams:

	VALID_STRATEGIES = ["random", "skipbanned", "author", "longest", "shortest", "pair"]

	def __init__(self, chooseStrategy="random", preferenceForAuthorsVersion=25, setDefines=[], doConfirm=False, discourseVarChance=80, originalText=""):
		if chooseStrategy not in self.VALID_STRATEGIES:
			raise ValueError("Unrecognized choose strategy '%s'" % chooseStrategy)
		self.chooseStrategy = chooseStrategy
		self.preferenceForAuthorsVersion = preferenceForAuthorsVersion
		self.setDefines = setDefines
		self.doConfirm = doConfirm
		self.discourseVarChance = discourseVarChance
		self.originalText = ""

	def __str__(self):
		return "chooseStrategy: %s, preferenceForAuthorsVersion: %s, setDefines: %s, discourseVarChance: %d" % (self.chooseStrategy, self.preferenceForAuthorsVersion, self.setDefines, self.discourseVarChance)

	def copy(self):
		return ParseParams(chooseStrategy=self.chooseStrategy, preferenceForAuthorsVersion=self.preferenceForAuthorsVersion, setDefines=list(self.setDefines), discourseVarChance=self.discourseVarChance, originalText=self.originalText)


# Call with an object of type ParseParams.
def parse(tokens, sourceText, parseParams):
	print "** PARSING **"
	parseParams.originalText = sourceText

	# Calculate and pre-set variables for Longest/Shortest case.
	if parseParams.chooseStrategy in ["longest", "shortest"]:
		print "Calculating %s defines (ignoring seed)..." % parseParams.chooseStrategy
		print parseParams
		bestDefines = []

		# Process all the DEFINEs in the code, with a copy of everything.
		variables.reset()
		macros.reset()
		tempTokens = list(tokens)
		tempTokens = variables.handleDefs(tempTokens, parseParams)
		tempTokens = macros.handleDefs(tempTokens, parseParams)
		parseParamsCopy = parseParams.copy()
		parseParamsCopy.preferenceForAuthorsVersion = 0
		chooser.setSeed(chooser.number(100000))

		# Now for each option in a define group, see which one is best.
		groups = variables.__v.varGroups.keys()
		for groupname in groups:
			optsToTry = list(variables.__v.varGroups[groupname])

			# If just one option, we want to try it as True and False.
			if len(optsToTry) is 1:
				optsToTry.append("^" + optsToTry[0])

			bestPos = -1
			bestLen = -1
			secondBestLen = -1
			isShortest = parseParams.chooseStrategy == "shortest"
			if isShortest:
				secondBestLen = 999999999
				bestLen = 999999999
			for pos, key in enumerate(optsToTry):
				variables.setAllTo(False)

				if key[0] != "^":
					variables.__v.variables[key] = True

				thisLen = len(handleParsing(tempTokens, parseParamsCopy))

				isBetter = False
				if isShortest:
					isBetter = thisLen < bestLen
				else:
					isBetter = thisLen > bestLen
				if isBetter:
					bestPos = pos
					secondBestLen = bestLen
					bestLen = thisLen
				elif (isShortest and thisLen < secondBestLen) or (not isShortest and thisLen > secondBestLen):
					secondBestLen = thisLen

			print "Best was %s (%d chars %s than next best)" % (optsToTry[bestPos], abs(bestLen - secondBestLen), "longer" if parseParams.chooseStrategy == "longest" else "shorter")
			bestDefines.append(optsToTry[bestPos])

		parseParams.setDefines = bestDefines

	# Handle the rendering.
	try:
		preppedTokens = handleVariablesAndMacros(tokens, sourceText, parseParams)
		# TODO: for the above to work, we'd need to be stripping out the DEFINE and MACRO tags from sourceText also as we went.
		if parseParams.doConfirm:
			confirm.process(preppedTokens, sourceText, ParseParams())
		renderedString = handleParsing(preppedTokens, parseParams)
	except result.ParseException, e:
		print e
		return e.result
	output = result.Result(result.PARSE_RESULT)
	output.package = renderedString
	return output

def handleVariablesAndMacros(tokens, sourceText, parseParams):
	variables.reset()
	macros.reset()
	tokens = variables.handleDefs(tokens, parseParams)
	tokens = macros.handleDefs(tokens, parseParams)
	print "vars: %s" % variables.showVars()
	return tokens


def handleParsing(tokens, params):
	renderedChunks = process(tokens, params)
	renderedString = ''.join(renderedChunks)
	renderedString = macros.expand(renderedString, params)
	return renderedString




# The lexer should have guaranteed that we have a series of TEXT tokens interspersed with sequences of others nested between CTRLBEGIN and CTRLEND with no issues with nesting or incomplete tags.
def process(tokens, parseParams):
	output = []
	index = 0
	discourseVars.resetStats()
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

	discourseVars.showStats(variables)
	return output



