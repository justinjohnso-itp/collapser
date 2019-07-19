

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

def test_alts():
	text = "We could be [heroes|villains]."
	options = ["We could be heroes.", "We could be villains."]
	for i in range(1,10):
		assert parse(text) in options
	text = "[a|b|c|d|e][1|2]"
	options = ["a1", "b1", "c1", "d1", "e1", "a2", "b2", "c2", "d2", "e2"]
	for i in range(1,10):
		assert parse(text) in options

def test_alt_spacing():
	text = "[a|aaa] [.|...]"
	options = ["a .", "a ...", "aaa .", "aaa ..."]
	for i in range(1,10):
		assert parse(text) in options

def test_all_alts():
	text = "[A|B|C]"
	foundA = False
	foundB = False
	foundC = False
	ctr = 0
	while ((not foundA) or (not foundB) or (not foundC)) and ctr < 100:
		result = parse(text)
		if result == "A":
			foundA = True
		if result == "B":
			foundB = True
		if result == "C":
			foundC = True
		ctr += 1
	assert foundA
	assert foundB
	assert foundC
	



