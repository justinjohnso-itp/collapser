

import quantlex
import quantparse
import pytest

def parse(text, params = None):
	lexed = quantlex.lex(text)
	if not lexed.isValid:
		print lexed
		assert False
	if params == None:
		params = quantparse.ParseParams(useAuthorPreferred=False)
	return quantparse.parse(lexed.tokens, params)

def test_alts():
	text = "We could be [heroes|villains]."
	options = ["We could be heroes.", "We could be villains."]
	for i in range(10):
		assert parse(text) in options
	text = "[a|b|c|d|e][1|2]"
	options = ["a1", "b1", "c1", "d1", "e1", "a2", "b2", "c2", "d2", "e2"]
	for i in range(10):
		assert parse(text) in options

def test_alt_spacing():
	text = "[a|aaa] [.|...]"
	options = ["a .", "a ...", "aaa .", "aaa ..."]
	for i in range(10):
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
	for i in range(10):
		assert parse(text) in options

	text = "She was [rather |]charming."
	options = ["She was charming.", "She was rather charming."]
	for i in range(10):
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
	for i in range(10):
		assert parse(text, params) == "A"

	text = "[^A|B|C]"
	for i in range(10):
		assert parse(text, params) == "A"

	text = "[A|B|^C|D]"
	for i in range(10):
		assert parse(text, params) == "C"

	text = "[A|^Z]"
	for i in range(10):
		assert parse(text, params) == "Z"

	text = "[A|^|C|D|E|F|G|H|I|J|K]"
	for i in range(10):
		assert parse(text, params) == ""

	text = "The author prefers no [|flowery |disgusting ]adjectives."
	for i in range(10):
		assert parse(text, params) == "The author prefers no adjectives."

def test_author_preferred_single():
	text = "A[^B]C"
	params = quantparse.ParseParams(useAuthorPreferred=True)
	for i in range(10):
		assert parse(text, params) == "ABC"
	text = "A[B]C"
	for i in range(10):
		assert parse(text, params) == "AC"

def test_always():
	text = "[~alpha]"
	for i in range(10):
		assert parse(text) == "alpha"

def test_always_is_exclusive():
	text = "[~alpha|beta]"
	with pytest.raises(Exception) as e_info:
		parse(text)

def test_number_values_cant_exceed_100():
	text = "[50>alpha|50>omega]"
	assert parse(text) in ["alpha", "omega"]
	text = "[50>alpha|51>omega]"
	with pytest.raises(Exception) as e_info:
		parse(text)
	text = "[50>alpha|50>omega|50>omega|50>omega|50>omega]"
	with pytest.raises(Exception) as e_info:
		parse(text)

def test_can_use_author_preferred_with_prob():
	text = "[80>alpha|10>beta|10>^gamma]"
	assert parse(text) in ["alpha", "omega", "gamma"]
	params = quantparse.ParseParams(useAuthorPreferred=True)
	for i in range(10):
		assert parse(text, params) == "gamma"

def test_can_use_blanks_with_prob():
	text = "[60>|40>pizza]"
	foundBlank = False
	foundPizza = False;
	ctr = 0
	while ((not foundBlank) or (not foundPizza)) and ctr < 100:
		result = parse(text)
		if result == "":
			foundBlank = True
		elif result == "pizza":
			foundPizza = True
		else:
			assert False
	assert foundBlank
	assert foundPizza

	text = "[65>pizza|35>]"
	foundBlank = False
	foundPizza = False;
	ctr = 0
	while ((not foundBlank) or (not foundPizza)) and ctr < 100:
		result = parse(text)
		if result == "":
			foundBlank = True
		if result == "pizza":
			foundPizza = True
	assert foundBlank
	assert foundPizza

def test_probability_works():
	text = "[90>alpha|10>beta]"
	timesA = 0
	timesB = 0
	for _ in range(100):
		result = parse(text)
		if result == "alpha":
			timesA += 1
		if result == "beta":
			timesB += 1
	assert timesA > timesB

	text = "[10>alpha|90>beta]"
	timesA = 0
	timesB = 0
	for _ in range(100):
		result = parse(text)
		if result == "alpha":
			timesA += 1
		if result == "beta":
			timesB += 1
	assert timesB > timesA

def test_less_than_100_is_chance_of_blank():
	text = "[25>alpha|35>beta]"
	foundA = False
	foundB = False;
	foundBlank = False;
	ctr = 0
	while ((not foundA) or (not foundB) or (not foundBlank)) and ctr < 100:
		result = parse(text)
		if result == "":
			foundBlank = True
		elif result == "alpha":
			foundA = True
		elif result == "beta":
			foundB = True
	assert foundA
	assert foundB
	assert foundBlank

def test_defines_are_stripped():
	text = "[DEFINE @test1][DEFINE @test2]This is a test of [DEFINE @test3]stripping.[DEFINE   @test4]"
	assert parse(text) == "This is a test of stripping."

def test_simple_defines_set_randomly():
	text = "[DEFINE @test]"
	foundY = False
	foundN = False
	ctr = 0
	while ((not foundY) or (not foundN)) and ctr < 100:
		result = parse(text)
		if quantparse.checkVar("test") == True:
			foundY = True
		elif quantparse.checkVar("test") == False:
			foundN = True
		ctr += 1
	assert foundY
	assert foundN

def test_simple_define_with_author_preferred():
	text = "[DEFINE ^@test]"
	params = quantparse.ParseParams(useAuthorPreferred=True)
	for _ in range(100):
		parse(text, params)
		assert quantparse.checkVar("test") == True
	text = "[DEFINE @test]"
	for _ in range(100):
		parse(text, params)
		assert quantparse.checkVar("test") == False

def test_defines_with_probabilities():
	text = "A [DEFINE 80>@beta|20>^@barcelona] C"
	params = quantparse.ParseParams(useAuthorPreferred=True)
	for _ in range(100):
		output = parse(text, params)
		assert quantparse.variables["barcelona"] == True

def test_defines_with_probabilities_must_sum_to_100():
	text = "[DEFINE 80>@A|19>@B]"
	with pytest.raises(Exception) as e_info:
		parse(text)
	text = "[DEFINE 80>@A|21>@B]"
	with pytest.raises(Exception) as e_info:
		parse(text)

	text = "[DEFINE 99>@A]"
	with pytest.raises(Exception) as e_info:
		parse(text)
	text = "[DEFINE 1>@A]"
	with pytest.raises(Exception) as e_info:
		parse(text)

	text = "[DEFINE 10>@A|15>@B|4>@C|31>@D|38>@E|2>@F]"
	assert parse(text) == ""
	text = "[DEFINE 10>@A|15>@B|31>@D|38>@E|2>@F]"
	with pytest.raises(Exception) as e_info:
		parse(text)

def test_multiple_defines_is_bad():
	text = "[DEFINE @alpha] Some text. [@alpha>Yes.] Some more. [DEFINE 80>@beta|20>@alpha]. Some final text."
	with pytest.raises(Exception) as e_info:
		parse(text)
	text = "[DEFINE 25>@alpha|75>^@alpha]."
	with pytest.raises(Exception) as e_info:
		parse(text)

def test_okay_to_define_after_using():
	text = "[@test>Test test.] Then stuff. [DEFINE ^@test]"
	params = quantparse.ParseParams(useAuthorPreferred=True)
	assert parse(text, params) == "Test test. Then stuff. "

def test_vars_collected_and_stripped():
	text = "[DEFINE @alpha][DEFINE 50>@beta|50>@gamma]Hello, friends![DEFINE @omega]"
	result = parse(text)
	keys = quantparse.showVars()
	assert len(keys) == 4
	assert "alpha" in keys
	assert "beta" in keys
	assert "gamma" in keys
	assert "omega" in keys
	assert result == "Hello, friends!"
	assert quantparse.checkVar("random") == False

def test_variable_refs():
	text = "[DEFINE ^@test][@test>This is a test message. ]Huzzah!"
	params = quantparse.ParseParams(useAuthorPreferred=True)
	result = parse(text, params)
	assert result == "This is a test message. Huzzah!"
	params = quantparse.ParseParams(useAuthorPreferred=False)
	result = parse(text, params)
	assert result == "Huzzah!"










	