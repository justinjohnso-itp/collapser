

import quantlex
import quantparse

def parse(text):
	lexed = quantlex.lex(text)
	return quantparse.parse(lexed.tokens)

def test_basic_parse():
	result = parse("This is text with [some values] inside.")
	assert result == "This is text with (control sequence with 1 tokens) inside."
