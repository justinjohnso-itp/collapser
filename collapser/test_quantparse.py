

import quantlex
import quantparse
import pytest

def parse(text, params = None):
	lexed = quantlex.lex(text)
	if params == None:
		params = quantparse.ParseParams(useAuthorPreferred=False)
	return quantparse.parse(lexed.tokens, params)

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
	
def test_empty_alts():
	text = "[A|B|]"
	foundEmpty = False
	ctr = 0
	while (not foundEmpty) and ctr < 100:
		result = parse(text)
		if result == "":
			foundEmpty = True
		ctr += 1
	assert foundEmpty

	text = "[A||B]"
	foundEmpty = False
	ctr = 0
	while (not foundEmpty) and ctr < 100:
		result = parse(text)
		if result == "":
			foundEmpty = True
		ctr += 1
	assert foundEmpty

	text = "[|A|B]"
	foundEmpty = False
	ctr = 0
	while (not foundEmpty) and ctr < 100:
		result = parse(text)
		if result == "":
			foundEmpty = True
		ctr += 1
	assert foundEmpty

def test_empty_alts_in_situ():
	text = "Let's go[ already]."
	options = ["Let's go already.", "Let's go."]
	for i in range(1,10):
		assert parse(text) in options

	text = "She was [rather |]charming."
	options = ["She was charming.", "She was rather charming."]
	for i in range(1,10):
		assert parse(text) in options

def test_single_texts():
	text = "alpha [beta ]gamma"
	foundY = False
	foundN = False
	ctr = 0
	while ((not foundY) or (not foundN)) and ctr < 100:
		result = parse(text)
		if result == "alpha beta gamma":
			foundY = True
		if result == "alpha gamma":
			foundN = True
		ctr += 1
	assert foundY
	assert foundN

def test_author_preferred():
	text = "[A|B|C]"
	params = quantparse.ParseParams(useAuthorPreferred=True)
	for i in range(1,10):
		assert parse(text, params) == "A"

	text = "[^A|B|C]"
	for i in range(1,10):
		assert parse(text, params) == "A"

	text = "[A|B|^C|D]"
	for i in range(1,10):
		assert parse(text, params) == "C"

	text = "[A|^Z]"
	for i in range(1,10):
		assert parse(text, params) == "Z"

	text = "[A|^|C|D|E|F|G|H|I|J|K]"
	for i in range(1,10):
		assert parse(text, params) == ""

	text = "The author prefers no [|flowery |disgusting ]adjectives."
	for i in range(1,10):
		assert parse(text, params) == "The author prefers no adjectives."

def test_author_preferred_single():
	text = "A[^B]C"
	params = quantparse.ParseParams(useAuthorPreferred=True)
	for i in range(1,10):
		assert parse(text, params) == "ABC"
	text = "A[B]C"
	for i in range(1,10):
		assert parse(text, params) == "AC"

def test_always():
	text = "[~alpha]"
	for i in range(1,10):
		assert parse(text) == "alpha"

def test_always_is_exclusive():
	text = "[~alpha|beta]"
	with pytest.raises(Exception) as e_info:
		parse(text)

