
import quantlex




def test_basic_count():
	text = "This is text with [some values] inside."
	quantlex.lexer.input(text)
	tokCount = 0
	while True:
	    tok = quantlex.lexer.token()
	    if not tok: 
	        break      # No more input
	    tokCount += 1
	assert tokCount == 5  # text, ctrlbegin, text, ctrlend, text

def test_identify_text():
	text = "This is text."
	quantlex.lexer.input(text)
	tok = quantlex.lexer.token()
	assert tok.type == "TEXT"
	assert tok.value == "This is text."