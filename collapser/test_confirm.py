# coding=utf-8

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

def confirmRenderVariant(text, variantPos, trunc, maxWidth):
	tokens = parseResult(text)
	confirm.preprocessTokens(tokens)
	confirm.ctrlSeqPos = 0
	ctrlcontents = confirm.ctrlSeqsFound[0]
	parseParams = quantparse.ParseParams()
	variants = ctrlseq.renderAll(ctrlcontents[0], parseParams, showAllVars=True)
	ctrlEndPos = ctrlcontents[1]
	ctrlStartPos = text.rfind("[", 0, ctrlEndPos)
	pre = confirm.getPre(text, ctrlStartPos, ctrlEndPos)
	post = confirm.origGetPost(text, ctrlEndPos)
	firstVariant = variants.alts[variantPos].txt
	result = confirm.renderVariant(trunc, pre, firstVariant, post, trunc, maxWidth, text, parseParams, ctrlEndPos)
	return result




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
	assert rendered == """...
It was a very wonderful day....
              ^       ^
"""

def test_carets_without_trunc():
	text = """
We're so [happy|sad] to see you."""
	rendered = confirmRenderVariant(text, 0, "", 70)
	assert rendered == """
We're so happy to see you.
         ^   ^
"""

def test_without_leading_newlines():
	text = """
So I inserted a lot of stuff here because what I was most interested in was the situation where [this happened and I regretted so much all the things I'd said, the people I'd hurt,|the other thing took place despite all the best laid plans of mice and men to prevent it] and it was hard to watch without knowing the way the story was going to end."""
	rendered = confirmRenderVariant(text, 0, "...", 80)
	assert rendered == """                                                               v
...cause what I was most interested in was the situation where this happened and
I regretted so much all the things I'd said, the people I'd hurt, and it was
                                                                ^
hard to watch without knowing the way the story...
"""

def test_unicode():
	text = """
“Oh, shit.” Niko hadn’t found [the end of the hallway|my socks]. It had twisted a couple more times, he said,"""
	rendered = confirmRenderVariant(text, 0, "", 70)
	assert rendered == """
                              v
"Oh, shit." Niko hadn't found the end of the hallway. It had twisted a
                                                   ^
couple more times, he said,
"""

def test_new_lines_after_variant():
	text = """
Although our story really did happen.

[Fine then. Here goes.|Okay, so. Here goes.|Fine. So.|Fine. Okay.] You ready?

This is what happened."""
	rendered = confirmRenderVariant(text, 0, "", 70)
	assert rendered == """
Although our story really did happen.

v
Fine then. Here goes. You ready?
                    ^

This is what happened.
"""

def test_post_expansions_single_line():
	text = """
This is our story. Our [real|fake] story. [And how|Yep]. Great."""
	rendered = confirmRenderVariant(text, 0, "", 70)
	assert rendered in ["""
This is our story. Our real story. And how. Great.
                       ^  ^
""", """
This is our story. Our real story. Yep. Great.
                       ^  ^
"""]

def test_post_expansions_multi_line():
	text = """
This is our story. Our [real|amazingly true] story. [And no one can ever tell us that we didn't really believe in what happened.|But it'll never be the same again after the things that occured to us, now will it bucko? No I absolutely don't think it will.]"""
	rendered = confirmRenderVariant(text, 0, "", 70)
	assert rendered in ["""
                       v
This is our story. Our real story. And no one can ever tell us that we
                          ^
didn't really be
""", """
                       v
This is our story. Our real story. But it'll never be the same again
                          ^
after the things t
"""]


