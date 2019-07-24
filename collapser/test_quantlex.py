
import quantlex


def dumpTokens(toks):
	print "DUMP"
	for pos, tok in enumerate(toks):
		print "%d: (%s) %s" % (pos, tok.type, tok.value)

def test_basic_count():
	text = "This is text with [some values] inside."
	result = quantlex.lex(text)
	assert result.isValid
	assert len(result.tokens) == 5  # text, ctrlbegin, text, ctrlend, text

def test_identify_text():
	text = "This is text."
	toks = quantlex.lex(text).tokens
	assert len(toks) == 1
	assert toks[0].type == "TEXT"
	assert toks[0].value == "This is text."

def test_full_line_comments_ignored():
	text = """# This is a comment. This is still a comment.
But this is text.
#And another # comment####.   # 
More normal text.
Even more normal text"""
	toks = quantlex.lex(text).tokens
	assert len(toks) == 2
	assert toks[0].type == "TEXT"
	assert toks[0].value == "But this is text.\n"
	assert toks[1].type == "TEXT"
	assert toks[1].value == "More normal text.\nEven more normal text"

def test_end_line_comments_ignored():
	text = "This is text. #and this is a comment."
	toks = quantlex.lex(text).tokens
	assert len(toks) == 1
	assert toks[0].type == "TEXT"
	assert toks[0].value == "This is text. "

def test_alternatives():
	text = "This is text with [some|alternatives] inside it."
	toks = quantlex.lex(text).tokens
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
	toks = quantlex.lex(text).tokens
	assert toks[0].type == "CTRLBEGIN"
	assert toks[1].type == "AUTHOR"
	assert toks[2].type == "TEXT"
	assert toks[2].value == "author preferred"

# Must be followed by a text block; can't be preceeded by a text block.
def test_bad_author_preferred():
	text = "[cant_be_at_end^|of block]"
	result = quantlex.lex(text)
	assert result.isValid == False
	text = "[cant_be_in_^middle|of block]"
	result = quantlex.lex(text)
	assert result.isValid == False

def test_always_print():
	text = "[~always print this]"
	toks = quantlex.lex(text).tokens
	assert toks[0].type == "CTRLBEGIN"
	assert toks[1].type == "ALWAYS"
	assert toks[2].type == "TEXT"
	assert toks[2].value == "always print this"

def test_prevent_nesting():
	text = "[don't allow [nested] sequences]"
	result = quantlex.lex(text)
	assert result.isValid == False
	assert result.errorLineNumber == 1
	assert result.errorColumn == 14

def test_multiline_sequences():
	text = """
This is the [start of a big
sequence that spans a number
of lines and goes on for a
while before ending] with the
last character."""
	result = quantlex.lex(text)
	assert result.isValid
	assert len(result.tokens) == 5
	assert result.tokens[2].value == "start of a big\nsequence that spans a number\nof lines and goes on for a\nwhile before ending"

def test_no_end_ctrl():
	text = """
This [is] the [start of a control
sequence that never ends, whoops,
we should do something about
that really."""
	result = quantlex.lex(text)
	assert result.isValid == False
	assert result.errorLineNumber == 2
	assert result.errorColumn == 15

def test_extra_end_ctrl():
	text = """
This is [a series of perfectly
legitimate] control [seqs] but
we've got an extra here] which
really shouldn't be there."""
	result = quantlex.lex(text)
	assert result.isValid == False
	assert result.errorLineNumber == 4
	assert result.errorColumn == 24

def test_bad_divider_pos():
	text = "A divider | can't be outside a [sequence]."
	result = quantlex.lex(text)
	assert result.isValid == False
	assert result.errorLineNumber == 1
	assert result.errorColumn == 11

# TODO test empty control sequence []


def test_lex_probabilities():
	text = "Text [40>alpha|60>gamma] text"
	result = quantlex.lex(text)
	assert result.isValid == True
	toks = result.tokens
	assert toks[0].type == "TEXT"
	assert toks[1].type == "CTRLBEGIN"
	assert toks[2].type == "NUMBER"
	assert toks[2].value == 40
	assert toks[3].type == "TEXT"
	assert toks[3].value == "alpha"
	assert toks[4].type == "DIVIDER"
	assert toks[5].type == "NUMBER"
	assert toks[5].value == 60
	assert toks[6].type == "TEXT"
	assert toks[6].value == "gamma"
	assert toks[7].type == "CTRLEND"
	assert toks[8].type == "TEXT"
	assert toks[8].value == " text"

def test_numbers_one_or_two_digits():
	text = "[>test]"
	result = quantlex.lex(text)
	assert result.isValid == False
	text = "[1>test]"
	result = quantlex.lex(text)
	assert result.isValid == True
	text = "[10>test]"
	result = quantlex.lex(text)
	assert result.isValid == True
	text = "[100>test]"
	result = quantlex.lex(text)
	assert result.isValid == False
	text = "[999>test]"
	result = quantlex.lex(text)
	assert result.isValid == False
	text = "[837183735>test]"
	result = quantlex.lex(text)
	assert result.isValid == False


def test_numbers_only_parsed_in_right_place():
	text = "I'm 40 years old! [50>alpha]"
	toks = quantlex.lex(text).tokens
	assert toks[0].type == "TEXT"
	assert toks[0].value == "I'm 40 years old! "
	
	text = "[10>I'm 50 years old.|90>I'm 90 years old.]"
	toks = quantlex.lex(text).tokens
	assert toks[2].value == "I'm 50 years old."
	assert toks[5].value == "I'm 90 years old."

	text = "[This > isn't right]"
	result = quantlex.lex(text)
	assert result.isValid == False

	text = "[alpha 50>|beta 60>]"
	result = quantlex.lex(text)
	assert result.isValid == False

def test_variable_lexing():
	text = "Should see [DEFINE @temp]."
	result = quantlex.lex(text)
	assert result.isValid == True
	toks = result.tokens
	assert toks[2].type == "DEFINE"
	assert toks[3].type == "VARIABLE"
	assert toks[3].value == "temp"
	assert toks[5].type == "TEXT"
	assert toks[5].value == "."



