import pytest
import renderer_tweet

def test_getNearestPosToMiddle():
	txt = "Words;Words Words * Words;Words Words"
	result = renderer_tweet.getNearestPosToMiddle(txt, ";", 3)
	assert result == 25
	txt = "Words;Words Words * Words Words Words"
	result = renderer_tweet.getNearestPosToMiddle(txt, ";", 3)
	assert result == 5
	txt = "Words Words Words ; Words Words Words"
	result = renderer_tweet.getNearestPosToMiddle(txt, ";", 3)
	assert result == 18
	txt = "Words Words Words;*;Words Words Words"
	result = renderer_tweet.getNearestPosToMiddle(txt, ";", 3)
	assert result in [17, 19]

def test_getNearestPosToMiddle_EdgeCases():
	txt = "Words Words Words * Words Words Words"
	result = renderer_tweet.getNearestPosToMiddle(txt, ";", 3)
	assert result == -1
	txt = ""
	result = renderer_tweet.getNearestPosToMiddle(txt, ";", 3)
	assert result == -1

def test_getNearestPosToMiddle_LongEnough():
	txt = "Words Words Words * Words Words Words;"
	result = renderer_tweet.getNearestPosToMiddle(txt, ";", 3)
	assert result == -1
	txt = ";Words Words Words * Words Words Words"
	result = renderer_tweet.getNearestPosToMiddle(txt, ";", 3)
	assert result == -1
	txt = "Words Words Words * Words Words Wor;ds"
	result = renderer_tweet.getNearestPosToMiddle(txt, ";", 3)
	assert result == -1
	txt = "Wo;rds Words Words * Words Words Words"
	result = renderer_tweet.getNearestPosToMiddle(txt, ";", 3)
	assert result == -1

	txt = "Words;Words Words * Word;s"
	result = renderer_tweet.getNearestPosToMiddle(txt, ";", 3)
	assert result == 5
	txt = "W;ords * Words Words;Words"
	result = renderer_tweet.getNearestPosToMiddle(txt, ";", 3)
	assert result == 20
