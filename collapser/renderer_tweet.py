# coding=utf-8


import renderer
import re
import fileio
import renderer_text
import sys

class RendererTweet(renderer.Renderer):

	def render(self):
		print "Rendering to tweets."
		self.makeStagedFile()
		self.makeOutputFile()

	def makeStagedFile(self):
		renderer = renderer_text.RendererText(self.collapsedText, self.params)
		renderer.render()

	def makeOutputFile(self):
		print "Rendering to tweets."
		inputFile = self.params["outputDir"] + self.params["fileId"] + ".txt"
		inputText = fileio.readInputFile(inputFile)
		tweets = splitIntoTweets(inputText)

		outputFileName = self.params["outputDir"] + self.params["fileId"] + ".tweets.txt"
		fileio.writeOutputFile(outputFileName, tweets)

	def renderFormattingSequence(self, contents):
		pass


# How to break tweets?
# - Break at paragraph breaks
# - Fit as many sentences as you can in one tweet.
# - If you can't fit a single sentence in a tweet, break it up in roughly the middle. Repeat if you still can't fit in a tweet.
# - Special handling for chapter/part breaks and quotations.


# Edge cases.
# What about an italics that splits across sentences, like "_Okay. Great. What now?_"
# Quoted dialogue with multiple sentences. Should try to keep together.

MAX_TWEET_SIZE = 240

class Sentence():
	def __init__(self, s, j):
		self.sentence = s
		self.join = j

	def __repr__(self):
		return "(Sentence: \"%s\", join: %s)" % (self.sentence, self.join)

def splitIntoTweets(text, max_size = MAX_TWEET_SIZE):
	sentences = splitIntoSentences(text)
	# for sentence in sentences:
	# 	print "> %s" % sentence[0]
	# print "Found %d sentences:" % len(sentences)

	tweets = []
	sPos = 0
	while sPos < len(sentences):
		
		tweet = ""

		while len(tweet) <= max_size and sPos < len(sentences):
			nextSentence = sentences[sPos].sentence
			nextJoin = sentences[sPos].join

			if len(tweet) + len(nextSentence) <= max_size:
				tweet += nextSentence
				sPos += 1
				if nextJoin != "SPACE":
					break
				tweet += " "
			else:
				chunks = breakSentenceIntoChunks(sentences[sPos])
				if len(chunks) == 1:
					break
				sentences = sentences[:sPos] + chunks + sentences[sPos+1:]
				continue

		if tweet == "":
			print "Skipping too-long sentence."
			sPos += 1

		print "Tweet (%d):\n\"%s\"\n\n" % (len(tweet), tweet)
		if len(tweet) > max_size:
			print "ERROR: Tried to append tweet with length %d" % len(tweet)
			break
		tweets.append(tweet)

	return tweets


def breakSentenceIntoChunks(sentence, max_size = MAX_TWEET_SIZE):
	print "Trying breakSentenceIntoChunks for: %s" % sentence
	splitCharsInBestOrder = [';', ':', ',', '---', ',"', '...']
	text = sentence.sentence
	for spl in splitCharsInBestOrder:
		bestPos = getNearestPosToMiddle(text, spl)
		if bestPos == -1:
			continue
		left = [Sentence(text[:bestPos+len(spl)], "SPACE")]
		right = [Sentence(text[bestPos+len(spl):], sentence.join)]
		if len(left[0].sentence) > max_size:
			left = breakSentenceIntoChunks(left[0], max_size)
		if len(right[0].sentence) > max_size:
			right = breakSentenceIntoChunks(right[0], max_size)
		return left + right

	return [sentence]

def getNearestPosToMiddle(text, spl, MIN_VIABLE_SPLIT_DIFF = 6):
	midPos = len(text) / 2
	prevPos = text.rfind(spl, 0, midPos)
	nextPos = text.find(spl, midPos)
	if prevPos == -1 and nextPos == -1:
		return -1
	if prevPos == -1 and nextPos != -1:
		prevPos = -99999999
	if nextPos == -1 and prevPos != -1:
		nextPos = 99999999
	if midPos - prevPos <= nextPos - midPos:
		if prevPos >= MIN_VIABLE_SPLIT_DIFF:
			return prevPos
	else:
		if nextPos < len(text) - MIN_VIABLE_SPLIT_DIFF - 1:
			return nextPos
	return -1




# [("Sentence.", "SPACE"), ("Second sentence.", "PARAGRAPH"), ]

def splitIntoSentences(text):
	text = re.sub(r" +\n", "\n", text)
	text = re.sub(r"\n{2,}", "\n\n", text)
	outputArr = []
	pos = 0
	pattern = r"([\.!\?][_\"\)]*)([ \n\#]+)(?![a-z])"
	#pattern = r"(\.|!|\?|\._|\?_|!_|\.\"|\?\"|!\"|\.\)|\?\)|!\))([ \n\#]+)"

	prevPos = 0
	for match in re.finditer(pattern, text):
		startPos = match.start()
		endPos = match.end()
		endPunc = match.group(1)
		endSpace = match.group(2)
		# print 'Sentence ended with endPunc "%s" and endSpace "%s" at %d:%d' % (endPunc, endSpace, startPos, endPos)

		sentence = text[prevPos:startPos + len(endPunc)]
		# print '-->sentence: "%s"' % sentence
		join = ""
		if endSpace == " " or endSpace == "  ":
			join = "SPACE"
		elif re.search(r".*\#.*", endSpace):
			join = "SECTIONBREAK"
		elif re.search(r"CHAPTER", endSpace):
			join = "CHAPTERBREAK"
		elif re.search(r"PART", endSpace):
			join = "PARTBREAK"
		elif re.search(r"(\n){2,}", endSpace):
			join = "PARAGRAPH"
		elif endSpace == "\n":
			join = "LINEBREAK"
		# print "-->join: %s" % join
		if join == "":
			print "ERROR"
			sys.exit()

		outputArr.append(Sentence(sentence, join))

		prevPos = endPos

	last = text[prevPos:]
	outputArr.append(Sentence(last, "SPACE"))
	
	return outputArr



