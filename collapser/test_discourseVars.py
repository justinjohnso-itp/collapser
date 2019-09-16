
import discourseVars
import pytest

def test_getNumBeVerbsInText():
	text = '''To be or not to be.'''
	assert discourseVars.getNumBeVerbsInText(text) == 2