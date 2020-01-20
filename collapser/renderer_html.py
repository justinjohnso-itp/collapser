# coding=utf-8


import renderer
import re
import fileio

class RendererHTML(renderer.Renderer):

	def render(self):
		print "Rendering to HTML."
		self.makeStagedFile()
		self.makeOutputFile()

	def makeStagedFile(self):
		pass

	def makeOutputFile(self):
		self.collapsedText = prepForHTMLOutput(self.collapsedText)
		workFile = self.renderFormattingSequences()
		workFile = specialHTMLFixes(workFile)
		postHTMLificationSanityCheck(workFile)
		outputFileName = self.params.outputDir + self.params.fileId + ".html"
		fileio.writeOutputFile(outputFileName, workFile)

	def renderFormattingSequence(self, contents):
		code = contents[0]
		if code == "part":
			partNum = contents[1]
			partTitle = contents[2]
			return "<h1>" + partNum + ": " + partTitle + "</h1><p>&nbsp;</p>"
		if code == "epigraph":
			epigraph = contents[1]
			source = contents[2]
			return "<blockquote>" + epigraph + "</blockquote><blockquote><i>" + source + "</i></blockquote><p>&nbsp;</p>"
		if code == "end_part_page":
			return "<p>&nbsp;</p>"
		if code == "chapter":
			chapNum = contents[1]
			intro = "" if chapNum == "EPILOGUE" else "Chapter "
			return "<h2>" + intro + chapNum + "</h2>"
		if code == "section_break":
			return "<hr>"
		if code == "verse":
			text = contents[1]
			return "<blockquote><i>" + text + "</i></blockquote>"
		if code == "verse_inline" or code == "verse_inline_sc":
			text = contents[1]
			return "\n<i>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + text + "</i>\n"
		if code == "pp":
			return "</p><p>"
		if code == "i":
			text = contents[1]
			return "<i>" + text + "</i>"
		if code == "sc" or code == "scwide":
			text = contents[1]
			return text.upper()
		if code == "vspace":
			# TODO: Make this work if there's a need.
			return "<p>&nbsp;</p>"

		raise ValueError("Unrecognized command '%s' in control sequence '%s'" % (code, contents)) 


def prepForHTMLOutput(text):
	# Fixes that need to happen before we expand formatting sequences.

	# Remove space at start of lines (before formatter adds any)
	text = re.sub(r"\n[ \t]*", "\n", text)

	return text

def specialHTMLFixes(text):
	# Fixes that should happen after all output is rendered.
	# Fix unicode quotes and special chars
	text = re.sub(r"'", "&rsquo;", text)
	text = re.sub(r"’", "&rsquo;", text)
	text = re.sub(r"‘", "&lsquo;", text)
	text = re.sub(r"“", '&ldquo;', text)
	text = re.sub(r"”", '&rdquo;', text)
	text = re.sub(r"…", "...", text)
	text = re.sub(r"—", "&mdash;", text)
	text = re.sub(r"---", "&mdash;", text)

	# Convert Latex explicit line break markers
	text = re.sub(r"\\\\", "<br>", text)

	# Fix single spaces at start of new lines (we can't get rid of these earlier because we might have a tag like {pp} we haven't processed yet, but we only look for single spaces to avoid removing epigraph indents.)
	text = re.sub(r"\n (\w)", r"\n\1", text)

	# Fix line breaks in the middle of sentences.
	text = re.sub(r"\n([a-z])", r" \1", text)

	# Convert to paragraphs.
	lines = text.split('\n')
	output_lines = []
	for line in lines:
		if len(line) > 0 and line[0] != "<":
			output_lines.append("<p>" + line + "</p>")
		else:
			output_lines.append(line)
	# text = re.sub(r"\n(.*)\n", r"<p>\1</p>\n\n", text)
	text = '\n\n'.join(output_lines)

	return text

def postHTMLificationSanityCheck(text):
	# Look for unexpected characters etc. here
	pos = text.find('{')
	if pos is not -1:
		raise ValueError("Found invalid underscore '{' character on line %d:\n%s" % (result.find_line_number(text, pos), result.find_line_text(text, pos)) )



