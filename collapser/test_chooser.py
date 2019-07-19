

import chooser

def test_oneOf():
	options = ["a", "b", "c"]
	result = chooser.oneOf(options)
	assert result in options
