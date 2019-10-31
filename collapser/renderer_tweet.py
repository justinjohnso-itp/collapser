# coding=utf-8


import renderer
import re
import fileio
import renderer_text

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



def splitIntoTweets(text):
	sentences = splitIntoSentences(text)
	return sentences


# ["Sentence.", "SPACE", "Second sentence.", "PARAGRAPH", ]

def splitIntoSentences(text):
	outputArr = []
	pos = 0
	pattern = r"([.!?_\"])([ \n]+)"
	for match in re.finditer(pattern, text):
		startPos = match.start()
		endPos = match.end()
		print 'Sentence ended with char "%s" at %d:%d' % (text[startPos:endPos], startPos, endPos)


	return text



