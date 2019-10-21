
import renderer
import pytest

class AbstractRenderer(renderer.Renderer):

	def render(self):
		self.makeStagedFile()
		self.makeOutputFile()

	def makeStagedFile(self):
		pass

	def makeOutputFile(self):
		pass

	def renderControlSequence(self, contents):
		code = contents[0]
		if code == "i":
			text = contents[1]
			return "/" + text + "/"
		if code == "epigraph":
			epigraph = contents[1]
			source = contents[2]
			return "-- " + epigraph + " -- (" + source + ")"
		else:
			return "*" + code + "*"


def test_getNextCtrlSeq_Basic():
	text = '''This is a test of {i/emphasis} and {epigraph/A quotation/Rand Miller} other stuff.'''
	emptyParams = {}
	ar = AbstractRenderer(text, emptyParams)
	ar.resetCtrlSeqPos()
	assert ar.seqPos == 0
	result = ar.getNextCtrlSeq()
	assert result[0] == "This is a test of "
	assert result[1] == "i"
	assert result[2] == "emphasis"
	assert ar.seqPos == 30
	result = ar.getNextCtrlSeq()	
	assert result[0] == " and "
	assert result[1] == "epigraph"
	assert result[2] == "A quotation"
	assert result[3] == "Rand Miller"
	assert ar.seqPos == 69
	result = ar.getNextCtrlSeq()
	assert result is None
	result = ar.getNextCtrlSeq()
	result = ar.getNextCtrlSeq()
	result = ar.getNextCtrlSeq()
	assert result is None
	ar.resetCtrlSeqPos()
	assert ar.seqPos == 0
	result = ar.getNextCtrlSeq()
	assert result[0] == "This is a test of "
	assert result[1] == "i"
	assert result[2] == "emphasis"
	assert ar.seqPos == 30

def test_getNextCtrlSeq_EdgeCases():
	text = '''No control seqs here.'''
	emptyParams = {}
	ar = AbstractRenderer(text, emptyParams)
	ar.resetCtrlSeqPos()
	result = ar.getNextCtrlSeq()
	assert result is None

	text = '''{i/Starts} with a control sequence.'''
	ar = AbstractRenderer(text, emptyParams)
	ar.resetCtrlSeqPos()
	result = ar.getNextCtrlSeq()
	assert result[0] == ""
	assert result[1] == "i"
	assert result[2] == "Starts"
	result = ar.getNextCtrlSeq()
	assert result is None

	text = '''Control sequence at the {i/end}'''
	ar = AbstractRenderer(text, emptyParams)
	ar.resetCtrlSeqPos()
	result = ar.getNextCtrlSeq()
	assert result[0] == "Control sequence at the "
	assert result[1] == "i"
	assert result[2] == "end"
	result = ar.getNextCtrlSeq()
	assert result is None

	text = '''{i/adjacent}{i/sequences}'''
	ar = AbstractRenderer(text, emptyParams)
	ar.resetCtrlSeqPos()
	result = ar.getNextCtrlSeq()
	assert result[0] == ""
	assert result[2] == "adjacent"
	result = ar.getNextCtrlSeq()
	assert result[0] == ""
	assert result[2] == "sequences"
	result = ar.getNextCtrlSeq()
	assert result is None


def test_renderControlSequences():
	text = '''This is a test of {i/emphasis} and {epigraph/A quotation/Rand Miller} other stuff.'''
	emptyParams = {}
	ar = AbstractRenderer(text, emptyParams)
	expectedOutput = '''This is a test of /emphasis/ and -- A quotation -- (Rand Miller) other stuff.'''
	result = ar.renderControlSequences()
	assert result == expectedOutput
	result = ar.renderControlSequences()
	assert result == expectedOutput

def test_renderControlSequences_EdgeCases():
	emptyParams = {}

	text = '''No control seqs here.'''
	ar = AbstractRenderer(text, emptyParams)
	result = ar.renderControlSequences()
	assert result == text

	text = '''{i/One}{i/Two}{i/Three}'''
	ar = AbstractRenderer(text, emptyParams)
	result = ar.renderControlSequences()
	assert result == "/One//Two//Three/"

	text = '''{i/One} more time.'''
	ar = AbstractRenderer(text, emptyParams)
	result = ar.renderControlSequences()
	assert result == "/One/ more time."

	text = '''One more {i/time}'''
	ar = AbstractRenderer(text, emptyParams)
	result = ar.renderControlSequences()
	assert result == "One more /time/"

	text = '''One more {i/time}!'''
	ar = AbstractRenderer(text, emptyParams)
	result = ar.renderControlSequences()
	assert result == "One more /time/!"

