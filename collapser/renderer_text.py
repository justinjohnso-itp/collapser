# coding=utf-8


import renderer
import re
import fileio

class RendererText(renderer.Renderer):

	def render(self):
		print "Rendering to plain text."
		self.makeStagedFile()
		self.makeOutputFile()

	def makeStagedFile(self):
		pass

	def makeOutputFile(self):
		workFile = self.renderControlSequences()
		workFile = specialTextFixes(workFile)
		postTextificationSanityCheck(workFile)
		outputFileName = self.params["outputDir"] + self.params["fileId"] + ".txt"
		fileio.writeOutputFile(outputFileName, workFile)

	def renderControlSequence(self, contents):
		code = contents[0]
		if code == "part":
			partNum = contents[1]
			partTitle = contents[2]
			epigraph = contents[3]
			source = contents[4]
			return "\n\n\n" + partNum + "\n\n" + partTitle + "\n\n\n" + epigraph + "\n\n" + source + "\n\n\n\n"
		if code == "epigraph":
			epigraph = contents[1]
			source = contents[2]
			return "\n\n" + epigraph + "\n\n" + source + "\n\n"
		if code == "chapter":
			chapNum = contents[1]
			return "\n\n\n\nChapter " + chapNum + "\n\n\n"
		if code == "section_break":
			return "\n\n         * * * * * * * * * * * * * * * * * * * * * * * * * *\n\n"
		if code == "verse":
			text = contents[1]
			# TODO need to indent lines
			return "\n\n" + text + "\n\n"
		if code == "verse_inline":
			text = contents[1]
			return "\n    " + text + "\n"
		if code == "pp":
			return "\n\n"
		if code == "i":
			text = contents[1]
			return "/" + text + "/"
		if code == "vspace":
			# TODO: Make this work if there's a need.
			return "\n\n\n"

		raise ValueError("Unrecognized command '%s' in control sequence '%s'" % (code, contents)) 


def specialTextFixes(text):
	text = re.sub(r"’", "'", text)
	text = re.sub(r"‘", "'", text)
	text = re.sub(r"“", '"', text)
	text = re.sub(r"”", '"', text)
	return text

def postTextificationSanityCheck(text):
	# Look for unexpected characters etc. here
	pos = text.find('{')
	if pos is not -1:
		raise ValueError("Found invalid underscore '{' character on line %d:\n%s" % (result.find_line_number(text, pos), result.find_line_text(text, pos)) )



