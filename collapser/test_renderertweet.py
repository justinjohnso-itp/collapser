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


def test_breakSentenceIntoChunks():
	sen = renderer_tweet.Sentence("This is my; sample sentence.", "PARAGRAPH")
	result = renderer_tweet.breakSentenceIntoChunks(sen)
	assert len(result) == 2
	assert result[0].sentence == "This is my;"
	assert result[0].join == "SPACE"
	assert result[1].sentence == " sample sentence."
	assert result[1].join == "PARAGRAPH"

	sen = renderer_tweet.Sentence("This is my sample sentence.", "SPACE")
	result = renderer_tweet.breakSentenceIntoChunks(sen)
	assert len(result) == 1
	assert result[0].sentence == "This is my sample sentence."
	assert result[0].join == "SPACE"

	sen = renderer_tweet.Sentence(";Semicolons bad, but commas good", "SPACE")
	result = renderer_tweet.breakSentenceIntoChunks(sen)
	assert len(result) == 2
	assert result[0].sentence == ";Semicolons bad,"
	assert result[1].sentence == " but commas good"

def test_breakSentenceIntoChunks_Recursive():
	sen = renderer_tweet.Sentence("Verbose; verbose, verbose: verbose;", "PARAGRAPH")
	result = renderer_tweet.breakSentenceIntoChunks(sen, 10)
	assert len(result) == 4
	assert result[0].sentence == "Verbose;"
	assert result[0].join == "SPACE"
	assert result[1].sentence == " verbose,"
	assert result[1].join == "SPACE"
	assert result[2].sentence == " verbose:"
	assert result[2].join == "SPACE"
	assert result[3].sentence == " verbose;"
	assert result[3].join == "PARAGRAPH"





