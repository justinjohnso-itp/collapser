# coding=utf-8


import renderer
import re
import fileio

class RendererMarkdown(renderer.Renderer):

	def render(self):
		self.makeStagedFile()
		self.makeOutputFile()

	def makeStagedFile(self):
		print "Rendering to Markdown."
		self.collapsedText = prepForMarkdownOutput(self.collapsedText)
		workFile = self.renderFormattingSequences()
		workFile = specialMarkdownFixes(workFile)
		postMarkdownificationSanityCheck(workFile)
		outputFileName = self.params["outputDir"] + self.params["fileId"] + ".md"
		fileio.writeOutputFile(outputFileName, workFile)

	def makeOutputFile(self):
		pass

	def renderFormattingSequence(self, contents):
		code = contents[0]
		if code == "part":
			partNum = contents[1]
			partTitle = contents[2]
			epigraph = contents[3]
			source = contents[4]
			return "\n\n# " + partNum + ": " + partTitle + "\n\n" + indent(epigraph) + "\n>\n> " + source + "\n\n"
		if code == "epigraph":
			epigraph = contents[1]
			source = contents[2]
			return "\n\n" + indent(epigraph) + ">\n>\n" + indent(source) + "\n\n"
		if code == "chapter":
			chapNum = contents[1]
			intro = "" if chapNum == "EPILOGUE" else "Chapter "
			return "\n\n# " + intro + chapNum + "\n\n"
		if code == "section_break":
			return "\n***\n"
		if code == "verse":
			text = indent(contents[1])
			return "\n\n" + text + "\n\n"
		if code == "verse_inline":
			text = indent(contents[1])
			return "\n" + text + "\n"
		if code == "pp":
			return "\n\n"
		if code == "i":
			text = contents[1]
			return "*" + text + "*"
		if code == "vspace":
			# TODO: Make this work if there's a need.
			return "\n\n\n"

		raise ValueError("Unrecognized command '%s' in control sequence '%s'" % (code, contents)) 


def indent(text):
	lines = text.split('\n')
	lines_indented = map(lambda line: "> " + line + "", lines)
	return '\n'.join(lines_indented)

def prepForMarkdownOutput(text):
	# Fixes that need to happen before we expand formatting sequences.

	# Fix extra spacing around {pp} tags.
	text = re.sub(r"[\n ]*\{pp\}[\n ]*", "{pp}", text)

	# Remove Latex explicit line break markers
	text = re.sub(r"\\\\[ ]*\n", "  \n", text)
	text = re.sub(r"\\\\[ ]*", "  \n", text)

	return text

def specialMarkdownFixes(text):
	# Fixes that should happen after all output is rendered.
	# Fix unicode quotes and special chars
	text = re.sub(r"…", "...", text)
	text = re.sub(r"—", "---", text)

	# Collapse multiple line breaks in a row (before formatter adds any)
	text = re.sub(r"[\n]{3,}", "\n\n", text)

	# Fix single spaces at start of new lines (we can't get rid of these earlier because we might have a tag like {pp} we haven't processed yet, but we only look for single spaces to avoid removing epigraph indents.)
	text = re.sub(r"\n (\w)", r"\n\1", text)

	return text

def postMarkdownificationSanityCheck(text):
	# Look for unexpected characters etc. here
	pos = text.find('{')
	if pos is not -1:
		raise ValueError("Found invalid underscore '{' character on line %d:\n%s" % (result.find_line_number(text, pos), result.find_line_text(text, pos)) )



