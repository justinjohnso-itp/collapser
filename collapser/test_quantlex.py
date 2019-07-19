
import quantlex


def getTokens(text):
	quantlex.lexer.input(text)
	toksList = []
	while True:
	    tok = quantlex.lexer.token()
	    if not tok: 
	        break      # No more input
	    toksList.append(tok)
	return toksList

def dumpTokens(toks):
	print "DUMP"
	for pos, tok in enumerate(toks):
		print "%d: (%s) %s" % (pos, tok.type, tok.value)

def test_basic_count():
	text = "This is text with [some values] inside."
	toks = getTokens(text)
	assert len(toks) == 5  # text, ctrlbegin, text, ctrlend, text

def test_identify_text():
	text = "This is text."
	toks = getTokens(text)
	assert len(toks) == 1
	assert toks[0].type == "TEXT"
	assert toks[0].value == "This is text."

def test_full_line_comments_ignored():
	text = """# This is a comment. This is still a comment.
But this is text.
#And another # comment####.   # 
More normal text.
Even more normal text"""
	toks = getTokens(text)
	assert len(toks) == 2
	assert toks[0].type == "TEXT"
	assert toks[0].value == "But this is text.\n"
	assert toks[1].type == "TEXT"
	assert toks[1].value == "More normal text.\nEven more normal text"

def test_end_line_comments_ignored():
	text = "This is text. #and this is a comment."
	toks = getTokens(text)
	assert len(toks) == 1
	assert toks[0].type == "TEXT"
	assert toks[0].value == "This is text. "


