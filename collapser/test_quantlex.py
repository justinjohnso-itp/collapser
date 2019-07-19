
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

def test_alternatives():
	text = "This is text with [some|alternatives] inside it."
	toks = getTokens(text)
	assert len(toks) == 7
	assert toks[0].type == "TEXT"
	assert toks[0].value == "This is text with "
	assert toks[1].type == "CTRLBEGIN"
	assert toks[2].type == "TEXT"
	assert toks[2].value == "some"
	assert toks[3].type == "DIVIDER"
	assert toks[4].type == "TEXT"
	assert toks[4].value == "alternatives"
	assert toks[5].type == "CTRLEND"
	assert toks[6].type == "TEXT"
	assert toks[6].value == " inside it."

def test_author_preferred():
	text = "[^author preferred|alt]"
	toks = getTokens(text)
	assert toks[0].type == "CTRLBEGIN"
	assert toks[1].type == "AUTHOR"
	assert toks[2].type == "TEXT"
	assert toks[2].value == "author preferred"

def test_always_print():
	text = "[~always print this]"
	toks = getTokens(text)
	assert toks[0].type == "CTRLBEGIN"
	assert toks[1].type == "ALWAYS"
	assert toks[2].type == "TEXT"
	assert toks[2].value == "always print this"





