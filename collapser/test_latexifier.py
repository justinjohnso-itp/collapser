
import latexifier
import pytest

def test_stringSwap():
	text = "This is a test of {test} standalone."
	result = latexifier.go(text)
	assert result == "This is a test of <<TEST_STANDALONE>> standalone."

	text = "{test}{test}"
	result = latexifier.go(text)
	assert result == "<<TEST_STANDALONE>><<TEST_STANDALONE>>"

	text = "This is my {test_param/alpha}"
	result = latexifier.go(text)
	assert result == "This is my <<TEST_PARAMS>>alpha<<END>>"

def test_formatting():
	text = "This is {i/italic}."
	result = latexifier.go(text)
	assert result == "This is \itshape{italic}."