
import variables
import quantlex
import quantparse


def parseResult(text, params = None):
	lexed = quantlex.lex(text)
	if not lexed.isValid:
		print lexed
		assert False
	if params == None:
		params = quantparse.ParseParams(chooseStrategy="random", doConfirm=False)
	params.originalText = text
	preppedTokens = quantparse.handleVariablesAndMacros(lexed.package, text, params)
	return preppedTokens

def getFirstCtrlSeq(tokens):
	index = 0
	while index < len(tokens):
		token = tokens[index]
		if token.type == "CTRLBEGIN":
			ctrl_contents = []
			index += 1
			token = tokens[index]
			while token.type != "CTRLEND":
				ctrl_contents.append(token)
				index += 1
				token = tokens[index]
			return ctrl_contents
		index += 1
	return []

def parseAndGetAlts(text):
	tokens = parseResult(text)
	ctrlseq = getFirstCtrlSeq(tokens)
	return variables.renderAll(ctrlseq)

def test_renderAllVariables():
	text = "[DEFINE @alpha1]This is some text. [@alpha1>Variant the first|Version the second]. And some final text."
	alts = parseAndGetAlts(text)
	assert alts[0].txt == "Variant the first"
	assert alts[1].txt == "Version the second"

	text = "[DEFINE @beta]Text. [@beta>Only if beta.] End."
	alts = parseAndGetAlts(text)
	assert alts[0].txt == "Only if beta."
	assert alts[1].txt == ""

	text = "[DEFINE @gamma|@delta]Text. [@gamma>Gamma forever|@delta>This is delta|Or not] End."
	alts = parseAndGetAlts(text)
	assert alts[0].txt == "Gamma forever"
	assert alts[1].txt == "This is delta"
	assert alts[2].txt == "Or not"




