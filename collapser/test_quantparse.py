

import quantlex
import quantparse

def parse(text):
	lexed = quantlex.lex(text)
	return quantparse.parse(lexed.tokens)

# def test_basic_parse():
# 	assert parse("This is text with [some values] inside.") == "This is text with (control sequence with 1 tokens) inside."
# 	assert parse("[a|b|c] 123 [e|f]") == "(control sequence with 5 tokens) 123 (control sequence with 3 tokens)"
# 	assert parse("text") == "text"

def test_one_text():
	assert parse("This is [text].") == "This is text."
	assert parse("[a]") == "a"
	assert parse("[a][b][c]") == "abc"
	assert parse("[ABC]123[DEF]") == "ABC123DEF"