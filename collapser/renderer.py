
import abc
import re

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

	@abc.abstractmethod
	def renderFormattingSequence(self, text):
		return text


	# Handle any text preparation that's agnostic across output formats.
	def prepareInputText(self):

		# Strip file identifiers (used by the lexer and parser to know what source file a given line comes from, so useful error messages can be printed).
		text = re.sub(r"\% file (.*)\n", "", self.collapsedText)

		self.collapsedText = text


	def renderFormattingSequences(self):
		self.resetCtrlSeqPos()
		ctrlSeq = self.getNextCtrlSeq()
		output = []
		while ctrlSeq is not None:
			leadingText = ctrlSeq[0]
			seqParams = ctrlSeq[1:]
			rendered = self.renderFormattingSequence(seqParams)
			output.append(leadingText)
			output.append(rendered)
			ctrlSeq = self.getNextCtrlSeq()
		output.append(self.collapsedText[self.seqPos:])
		return ''.join(output)


	def resetCtrlSeqPos(self):
		self.seqPos = 0

	# Returns an array [contentSinceLast, parts] with all the content since the previous control sequence in position 0, and the parts of the control sequence found in subsequent positions.
	def getNextCtrlSeq(self):
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






