
import quantparse
import ctrlseq

import abc
import re


class RenderParams:

	def __init__(self, outputFormat = "", fileId = "", seed = -1, randSeed = False, doFront = False, skipPadding = False, endMatter = False, outputDir = "", isDigital = False, copies = 1, parseParams = None):
		self.outputFormat = outputFormat
		self.fileId = fileId
		self.seed = seed
		self.randSeed = randSeed
		self.doFront = doFront
		self.skipPadding = skipPadding
		self.endMatter = endMatter
		self.outputDir = outputDir
		self.isDigital = isDigital
		self.copies = copies
		self.renderer = None
		self.pdfPages = -1
		self.parseParams = parseParams



class Renderer(object):
	__metaclass__ = abc.ABCMeta

	def __init__(self, collapsedText, params):
		self.collapsedText = collapsedText
		self.params = params
		self.seqPos = 0
		self.prepareInputText()

	# Main entry point: takes a collapsed file and writes an output file in the given format.
	@abc.abstractmethod
	def render(self):
		pass

	# Part 1: takes the collapsed file and turns it into a valid input file for the desired output format (i.e., collapsed text to LaTeX, Markdown, etc.). Generally only called by render.
	@abc.abstractmethod
	def makeStagedFile(self):
		pass

	# Part 2: Takes the staged input file and creates the desired output format (i.e. LaTeX to PDF, Markdown to HTML, etc)
	@abc.abstractmethod
	def makeOutputFile(self):
		pass

	# Convert a formatting sequence like {i/italics} into the proper coding for this output format.
	@abc.abstractmethod
	def renderFormattingSequence(self, text):
		return text

	# Suggest an array of endMatters to append that won't exceed the page budget (if this format has one) based on stats stored from the last time we rendered; return an empty array if no suggestions.
	@abc.abstractmethod
	def suggestEndMatters(self):
		return []

	# Handle any text preparation that's agnostic across output formats.
	def prepareInputText(self):

		# Strip file identifiers (used by the lexer and parser to know what source file a given line comes from, so useful error messages can be printed).
		text = re.sub(r"\% file (.*)\n", "", self.collapsedText)

		self.collapsedText = text


	def renderFormattingSequences(self):
		self.resetFormattingSeqPos()
		fSeq = self.getNextFormatSeq()
		output = []
		while fSeq is not None:
			leadingText = fSeq[0]
			seqParams = fSeq[1:]
			if seqParams[0] == "alternate_scene":
				rendered = renderAlternateSequence(self.params.parseParams)
			else:
				rendered = self.renderFormattingSequence(seqParams)
			output.append(leadingText)
			output.append(rendered)
			fSeq = self.getNextFormatSeq()
		output.append(self.collapsedText[self.seqPos:])
		return ''.join(output)


	def resetFormattingSeqPos(self):
		self.seqPos = 0

	# Returns an array [contentSinceLast, parts] with all the content since the previous control sequence in position 0, and the parts of the control sequence found in subsequent positions.
	def getNextFormatSeq(self):
		startPos = self.collapsedText.find("{", self.seqPos)
		if startPos is -1:
			return None
		endPos = self.collapsedText.find("}", startPos)
		if endPos is -1:
			raise ValueError("Found { without closing brace.")
		codeSeq = self.collapsedText[startPos:endPos+1]
		contents = codeSeq[1:-1].split('/')
		contentSinceLast = self.collapsedText[self.seqPos:startPos]
		self.seqPos = endPos+1
		return [contentSinceLast] + contents





def renderAlternateSequence(parseParams):
	sequencePicked = getSequenceToRender()
	seq = quantparse.get_ctrlseq(sequencePicked)
	rendered = ctrlseq.render(seq, parseParams)
	return rendered

def getSequenceToRender():
	return "Ch1IntroScene"





