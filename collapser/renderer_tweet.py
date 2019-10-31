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

def splitIntoTweets(text):
	sentences = splitIntoSentences(text)
	# for sentence in sentences:
	# 	print "> %s" % sentence[0]
	# print "Found %d sentences:" % len(sentences)

	tweets = []
	sPos = 0
	while sPos < len(sentences):
		
		tweet = ""

		while len(tweet) <= MAX_TWEET_SIZE and sPos < len(sentences):
			nextSentence = sentences[sPos][0]
			nextJoin = sentences[sPos][1]

			if len(tweet) + len(nextSentence) <= MAX_TWEET_SIZE:
				tweet += nextSentence
				sPos += 1
				if nextJoin != "SPACE":
					break
				tweet += " "
			else:
				chunks = breakSentenceIntoChunks(nextSentence, nextJoin)
				sentences = sentences[:sPos] + chunks + sentences[sPos+1:]
				continue

		if tweet == "":
			print "Skipping too-long sentence."
			sPos += 1

		print "Tweet (%d):\n%s\n\n" % (len(tweet), tweet)
		tweets.append(tweet)

	return ""


def breakSentenceIntoChunks(txt, endJoin):
	# TODO pairs like () ? 
	splitCharsInBestOrder = [';', ':', ',', '---', ',"', '...']
	for spl in splitCharsInBestOrder:
		result = trySentenceSplit(txt, endJoin, spl)
		if result is not None:
			return result
	print "Couldn't split sentence."
	return [txt, endJoin]


def trySentenceSplit(txt, endJoin, splitChar):
	parts = txt.split(splitChar)
	if len(parts) > 1:
		output = []
		for part, pos in enumerate(parts):
			if len(part) <= 3:  # This split is not useful
				return None
			if pos == len(parts)-1:
				output.append([part, endJoin])
			else:
				output.append([part + splitChar, "SPACE"])
		return output
	return None


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

		outputArr.append([sentence, join])

		prevPos = endPos


	return outputArr



