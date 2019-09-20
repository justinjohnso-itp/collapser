
import variables
import quantlex
import quantparse
import ctrlseq
import confirm

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
			return [ctrl_contents, token.lexpos]
		index += 1
	return []

def parseAndGetAlts(text):
	tokens = parseResult(text)
	ctrlcontents = getFirstCtrlSeq(tokens)
	return variables.renderAll(ctrlcontents[0])

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

def confirmRenderVariant(text, variantPos, trunc, maxWidth):
	tokens = parseResult(text)
	ctrlcontents = getFirstCtrlSeq(tokens)
	parseParams = quantparse.ParseParams()
	variants = ctrlseq.renderAll(ctrlcontents[0], parseParams, showAllVars=True)
	ctrlEndPos = ctrlcontents[1]
	ctrlStartPos = text.rfind("[", 0, ctrlEndPos)
	pre = confirm.getPre(text, ctrlStartPos, ctrlEndPos)
	post = confirm.getPost(text, ctrlEndPos)
	firstVariant = variants.alts[variantPos].txt
	result = confirm.renderVariant(trunc, pre, firstVariant, post, trunc, maxWidth)
	return result


def test_carets_multiline():
	text = """
So there were tapes where [this happened and I regretted so much all the things I'd said, the people I'd hurt,|the other thing took place despite all the best laid plans of mice and men to prevent it] and it was hard to watch."""
	rendered = confirmRenderVariant(text, 0, "...", 70)
	assert rendered == """...
                          v
So there were tapes where this happened and I regretted so much all
the things I'd said, the people I'd hurt, and it was hard to watch....
                                        ^
"""

def test_carets_singleline():
	text = """
It was a very [wonderful|happy|great] day."""
	rendered = confirmRenderVariant(text, 0, "...", 70)
	print "R:\n%s" % rendered
	assert rendered == """...
It was a very wonderful day....
              ^       ^
"""




