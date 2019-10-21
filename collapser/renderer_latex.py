# coding=utf-8

import renderer

import re
import result
import fileio
import terminal
import sys

latexBegin = "fragments/begin.tex"
latexEnd = "fragments/end.tex"
latexFrontMatter = "fragments/frontmatter.tex"
latexPostFrontMatter = "fragments/postfrontmatter.tex"

# TODO Add cleanup step to get rid of temp files

class RendererLatex(renderer.Renderer):

	# collapsedText, params

	def render(self):
		print "Rendering to LaTeX/PDF."
		self.makeStagedFile()
		self.makeOutputFile()

	def makeStagedFile(self):
		workFile = specialFixes(self.collapsedText)
		workFile = self.renderControlSequences()
		postLatexificationSanityCheck(workFile)
		stagedFileText = latexWrapper(workFile, self.params["seed"], self.params["doFront"])
		latexFileName = self.params["fileId"] + ".tex"
		fileio.writeOutputFile(latexFileName, stagedFileText)

	def makeOutputFile(self):
		inputFileName = self.params["fileId"] + ".tex"
		outputFileName = self.params["fileId"] + ".pdf"
		outputPDF(self.params["outputDir"], inputFileName, outputFileName, self.params["padding"])

	def renderControlSequence(self, contents):
		code = contents[0]
		if code == "part":
			partNum = contents[1]
			partTitle = contents[2]
			epigraph = contents[3]
			source = contents[4]
			# Hack to get "\mainmatter" to appear in right spot for opening chapter (otherwise page 1 is on the blank page preceeding and inner/outer positioning is wrong.)
			optMainMatter = ""
			if partNum == "PART ONE":
				optMainMatter = "\\mainmatter"
			return template_part[0] + optMainMatter + template_part[1] + partNum + template_part[2] + partTitle + template_part[3] + epigraph + template_part[4] + source + template_part[5]
		if code == "epigraph":
			epigraph = contents[1]
			source = contents[2]
			return template_epigraph[0] + epigraph + template_epigraph[1] + source + template_epigraph[2]
		if code == "chapter":
			chapNum = contents[1]
			return template_chapter[0] + chapNum + template_chapter[1]
		if code == "section_break":
			return template_section_break
		if code == "verse":
			text = contents[1]
			return template_verse[0] + text + template_verse[1]
		if code == "verse_inline":
			text = contents[1]
			return template_verse_inline[0] + text + template_verse_inline[1]
		if code == "pp":
			return template_pp
		if code == "i":
			text = contents[1]
			return template_i[0] + text + template_i[1]
		if code == "vspace":
			text = contents[1]
			return template_vspace[0] + text + template_vspace[1]

		raise ValueError("Unrecognized command '%s' in control sequence '%s'" % (code, codeSeq)) 



# Handle any tweaks to the rendered text before we begin the latex conversion.
def specialFixes(text):

	# Ensure verses don't break across pages.
	# {verse/A looking-glass held above this stream...}
	text = re.sub(r"{verse/(.*)}", r"{verse/\g<1> \\nowidow }", text)

	# Ensure no widows right before chapter breaks.
	text = re.sub(r"([\n\s]*){chapter/", r" \\nowidow \g<1>{chapter/", text)

	# Ensure no orphans right after section breaks.
	text = re.sub(r"{section_break}(\n*)(.*)\n", r"{section_break}\g<1>\g<2> \\noclub \n", text)

	# Use proper latex elipses
	text = re.sub(r"\.\.\. ", r"\ldots\ ", text)
	text = re.sub(r"… ", r"\ldots\ ", text)

	return text





# Raise errors if anything unexpected is found in the converted output.
def postLatexificationSanityCheck(text):
	# Look for unexpected characters etc. here
	# Note: can't use find_line_number_for_file etc. b/c those markers have been stripped.
	pos = text.find('_')
	if pos is not -1:
		raise ValueError("Found invalid underscore '_' character on line %d:\n%s" % (result.find_line_number(text, pos), result.find_line_text(text, pos)) )
	
	pos = text.find('''"''')
	if pos is not -1:
		raise ValueError("Found dumb quote character on line %d; use “ ” \n%s" % (result.find_line_number_for_file(text, pos), result.find_line_text(text, pos)) )

	return


# Wrap the converted latex in appropriate header/footers.
def latexWrapper(text, seed, includeFrontMatter):

	templates = {
		"begin": fileio.readInputFile(latexBegin),
		"end": fileio.readInputFile(latexEnd),
		"frontMatter": fileio.readInputFile(latexFrontMatter),
		"postFrontMatter": fileio.readInputFile(latexPostFrontMatter)
	}

	output = templates["begin"]
	if includeFrontMatter:
		output += templates["frontMatter"]
	output += templates["postFrontMatter"]
	output += text
	output += templates["end"]

	if seed < 9999:
		seed = "0%d" % seed

	# Insert the seed number where it appeared in front matter.
	msg = "This copy was generated from seed #%s and is the only copy generated from that seed." % seed
	if seed == -1:
		seed = "01893"
		msg = "This run of Advance Reader Copies have all been generated from seed #%s." % seed
	output = output.replace("SEED_TEXT", msg)
	output = output.replace("SEED_NUMBER", "%s" % seed)

	return output



def outputPDF(outputDir, inputFile, outputFile, padding):
	result = terminal.runCommand('lualatex', '-interaction=nonstopmode -synctex=1 -recorder --output-directory="%s" "%s" ' % (outputDir, inputFile))
	# lualatex will fail (return exit code 1) even when successfully generating a PDF, so ignore result["success"] and just look at the output.
	latexLooksGood = postLatexSanityCheck(result["output"])
	if not latexLooksGood:
		print "*** Generation failed. Check .log file in output folder."
		sys.exit()
	else:
		stats = getStats(result["output"])
		print "Success! Generated %d page PDF." % stats["numPages"]
		if padding is not -1:
			addPadding(outputFile, stats["numPages"], padding)



def postLatexSanityCheck(latexLog):
	numPages = 0

	overfulls = len(re.findall(r"\nOverfull \\hbox", latexLog))
	if overfulls > 500:
		print "Too many overfulls (found %d); halting." % overfulls
		return False

	result = getStats(latexLog)
	if result["numPages"] == -1:
		print "Couldn't find output line; halting."
		return False

	if result["numPages"] < 5 or result["numPages"] > 300:
		print "Unexpected page length (%d); halting." % result["numPages"]
		return False
	if result["numBytes"] < 100000 or result["numBytes"] > 3000000:
		print "Unexpected size (%d kb); halting." % (result["numBytes"] / 1000)
		return False

	# TODO: Check that it contains a key phrase that should exist in every version

	return True

def getStats(latexLog):
	data = { "numPages": -1, "numBytes": -1 }
	result = re.search(r"Output written on .*\.pdf \(([0-9]+) pages, ([0-9]+) bytes", latexLog)
	if result:
		data["numPages"] = int(result.groups()[0])
		data["numBytes"] = int(result.groups()[1])
	return data



def addPadding(outputFile, reportedPages, desiredPageCount):

	numPDFPages = countPages("output/combined.pdf")
	if numPDFPages != reportedPages:
		print "*** Latex reported generating %d page PDF, but pdftk reported the output was %d pages instead. Aborting." % (reportedPages, numPDFPages)
		sys.exit()

	if numPDFPages > desiredPageCount:
		print "*** Generation exceeded maximum length of %d page: was %d pages." % (desiredPageCount, numPDFPages)
		sys.exit()

	# If equal, no action needed. Otherwise, add padding to the desired number of pages, which must remain constant in print on demand so the cover art doesn't need to be resized.

	if numPDFPages < desiredPageCount:
		addBlankPages("output/combined.pdf", "output/combined-padded.pdf", desiredPageCount - numPDFPages)
		numCombinedPages = countPages("output/combined-padded.pdf")
		if numCombinedPages != desiredPageCount:
			print "*** Tried to pad output PDF to %d pages but result was %d pages instead." % (desiredPageCount, numPDFPages)
			sys.exit()



# Note: This requires pdftk, and specifically the version here updated for newer MacOS: https://stackoverflow.com/questions/39750883/pdftk-hanging-on-macos-sierra
# https://www.pdflabs.com/docs/pdftk-man-page/

def countPages(pdfPath):
	result = terminal.runCommand("pdftk", "%s dump_data | grep NumberOfPages" % pdfPath, shell=True)
	if not result["success"]:
		print "*** Couldn't get stats on output PDF; aborting."
		sys.exit()
	# == "NumberOfPages: 18"
	pagesResult = re.search(r"NumberOfPages: ([0-9]+)", result["output"])
	numPDFPages = int(pagesResult.groups()[0])
	return numPDFPages


# This also required pdftk, plus a blankpages.pdf with a large number of empty pages of the same size as the rest of the book.
def addBlankPages(inputPDF, outputPDF, numBlankPages):
	result = terminal.runCommand("pdftk", "A=%s B=extras/blankpages.pdf cat A B1-%s output %s" % (inputPDF, numBlankPages, outputPDF))
	if not result["success"]:
		print "*** Couldn't generate padded PDF. %s" % result["output"]
		sys.exit()




template_chapter = ['''

\\clearpage 

\\begin{ChapterStart}
\\vspace*{2\\nbs} 
\\ChapterTitle{\\decoglyph{l8694} ''', ''' \\decoglyph{l11057}} 
\\end{ChapterStart}

''']

template_part = ['''

\\cleartorecto
\\thispagestyle{empty}
''', '''
\\begin{ChapterStart}
\\vspace*{4\\nbs} 
\\ChapterTitle{''', '''} 
\\vspace*{2\\nbs} 
\\ChapterTitle{''', '''} 
\\end{ChapterStart}

\\vspace*{4\\nbs} 
\\begin{adjustwidth}{3em}{3em}
\\begin{parascale}[0.88]
''', '''\\\\
\\par
\\noindent \\textit{''', '''}
\\end{parascale}
\\end{adjustwidth}

\\cleartorecto

''']

template_epigraph = ['''
\\begin{adjustwidth}{3em}{3em}
\\begin{parascale}[0.88]
''', '''\\\\
\\par
\\noindent \\textit{''', '''}
\\end{parascale}
\\end{adjustwidth}
\\vspace*{2\\nbs} 
''']

template_section_break = '''

\\scenebreak

'''

template_pp = '''

'''

template_i = ['''\\textit{''', '''}''']

template_verse = ['''

\\vspace{1\\nbs}
\\begin{adjustwidth}{3em}{} 
\\textit{''', '''}
\\end{adjustwidth}
\\vspace{1\\nbs}

''']

template_verse_inline = ['''\\begin{adjustwidth}{3em}{} 
\\textit{''', '''}
\\end{adjustwidth}
\\noindent ''']

template_vspace = ['''

\\vspace*{''', '''\\nbs}

'''] 



