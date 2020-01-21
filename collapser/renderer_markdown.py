# coding=utf-8


import renderer
import re
import fileio
import chooser

class RendererMarkdown(renderer.Renderer):

	def render(self):
		self.makeStagedFile()
		self.makeOutputFile()

	def makeStagedFile(self):
		pass

	def makeOutputFile(self):
		print "Rendering to Markdown."
		self.collapsedText = prepForMarkdownOutput(self.collapsedText)
		workFile = self.renderFormattingSequences()
		workFile = specialMarkdownFixes(workFile)
		if self.params.doFront:
			workFile = generateFrontMatter(self.params.seed) + workFile
		postMarkdownificationSanityCheck(workFile)
		outputFileName = self.params.outputDir + self.params.fileId + ".md"
		fileio.writeOutputFile(outputFileName, workFile)

	def suggestEndMatters(self):
		suggestions = []
		# Should be listed in order you'd want them to appear.
		if chooser.percent(100): # 75
			suggestions.append("end-altscene.txt")
		if chooser.percent(100): # 75
			suggestions.append("end-stats.txt")
		if chooser.percent(100): # 75
			suggestions.append("end-abouttheauthor.txt")
		if chooser.percent(100):
			suggestions.append("end-backers.txt")
		return suggestions


	def renderFormattingSequence(self, contents):
		code = contents[0]
		if code == "part":
			partNum = contents[1]
			partTitle = contents[2]
			return "\n\n# " + partNum + ": " + partTitle
		if code == "endmatter":
			title = contents[1]
			return "\n\n# " + title
		if code == "epigraph":
			epigraph = contents[1]
			source = contents[2]
			return "\n\n" + indent(epigraph) + "\n>\n>" + source + "\n\n"
		if code == "end_part_page":
			return "\n\n"
		if code == "chapter":
			chapNum = contents[1]
			intro = "" if chapNum == "EPILOGUE" else "Chapter "
			return "\n\n# " + intro + chapNum + "\n\n"
		if code == "section_break":
			return "\n***\n"
		if code == "verse" or code == "url":
			text = indent(contents[1])
			return "\n\n" + text + "\n\n"
		if code == "verse_inline" or code == "verse_inline_sc":
			text = indent(contents[1])
			return "\n" + text + "\n"
		if code == "pp" or code == "finish_colophon":
			return "\n\n"
		if code == "i":
			text = contents[1]
			return "*" + text + "*"
		if code == "sc" or code == "scwide":
			text = contents[1]
			return text.upper()
		if code == "vspace":
			# TODO: Make this work if there's a need.
			return "\n\n\n"
		if code == "start_colophon":
			header = contents[1]
			return "\n\n# " + header + "\n\n"
		if code == "columns":
			return "\n\n<div class='columns'>"
		if code == "end_columns":
			return "</div>\n\n"

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


def generateFrontMatter(seed):
	text = ""
	
	if seed == -1:
		seedPrinted = "01893-b"
	elif seed < 9999:
		seedPrinted = "0%d" % seed
	else:
		seedPrinted = "%s" % seed

	if seed == -1:
		text = """
This is a special Advance Reader Copy of *Subcutanean*. In the final version, each printing of the book will be unique, generated from a specific seed. Words, sentences, or whole scenes may appear in some printings but not in others, or vice versa. No two copies will be alike.

For now, each Advance Reader Copy in this printing shares the same seed, and the same text.

subcutanean.textories.com
"""
	else:
		text = """
The book you’re holding is unique. There is no other exactly like it.

Each printing of *Subcutanean* is different. This is the one and only version generated from seed %s. Words, sentences, or whole scenes may appear in this printing but not in others, or vice versa. No two copies are alike.

But all of them are the same story, more or less. Don’t worry about what’s in the other versions. It doesn’t matter. This is the one that’s happening to you.

This is the one you have.

subcutanean.textories.com
""" % seed
	return text


