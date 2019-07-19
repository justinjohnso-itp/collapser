
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

