# coding=utf-8

import discourseVars
import pytest

def test_getNumBeVerbsInText():
	text = '''Absolutely none of those nasty verbs here.'''
	assert discourseVars.getNumBeVerbsInText(text) == 0
	text = '''A bee or an island don't count.'''
	assert discourseVars.getNumBeVerbsInText(text) == 0
	text = '''be at the start: okay.'''
	assert discourseVars.getNumBeVerbsInText(text) == 1
	text = '''A capital Be also counts'''
	assert discourseVars.getNumBeVerbsInText(text) == 1
	text = '''To be or not to be.'''
	assert discourseVars.getNumBeVerbsInText(text) == 2
	text = '''I wasn’t going to care about smart quotes.'''
	assert discourseVars.getNumBeVerbsInText(text) == 1
	text = '''I wasn't going to be angry, but they're being gross.'''
	assert discourseVars.getNumBeVerbsInText(text) == 4
	text = '''Punctuation:be?Was:were,isn't.'''
	assert discourseVars.getNumBeVerbsInText(text) == 4
