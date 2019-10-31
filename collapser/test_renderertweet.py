import pytest
import renderer_tweet

def test_getNearestPosToMiddle():
	txt = "Words;Words Words * Words;Words Words"
	result = renderer_tweet.getNearestPosToMiddle(txt, ";")
	assert result == 25