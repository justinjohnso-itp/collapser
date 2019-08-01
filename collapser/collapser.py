#!/usr/bin/python

import sys

import fileio
import collapse
import latexifier
import quantlex

inputFile = ""
outputFile = ""
inputText = ""
outputText = ""

latexBegin = "fragments/begin.tex"
latexEnd = "fragments/end.tex"
latexFrontMatter = "fragments/frontmatter.tex"
latexPostFrontMatter = "fragments/postfrontmatter.tex"

def showUsage():
	print """Usage: collapser <INPUT> <OUTPUT> options"""


def latexWrapper(text, includeFrontMatter=True):
	begin = fileio.readInputFile(latexBegin)
	end = fileio.readInputFile(latexEnd)
	frontMatter = fileio.readInputFile(latexFrontMatter)
	postFrontMatter = fileio.readInputFile(latexPostFrontMatter)
	output = begin
	if includeFrontMatter:
		output += frontMatter
	output += postFrontMatter
	output += text
	output += end
	return output



# Pre-latexifier.
def postLatexSanityCheck(text):
	# Look for unexpected characters etc. here
	pos = text.find('_')
	if pos is not -1:
		raise ValueError("Found invalid underscore '_' character on line %d:\n%s" % (quantlex.find_line_number(text, pos), quantlex.find_line_text(text, pos)) )
	return

def main():

	print """Collapser 0.1"""

	if len(sys.argv) != 3:
		showUsage()
		sys.exit()

	inputFile = sys.argv[1]
	outputFile = sys.argv[2]

	files = []
	inputText = fileio.readInputFile(inputFile)
	if inputFile[-12:] == "manifest.txt":
		path = inputFile[:-12]
		print "Reading manifest '%s'" % inputFile
		files = fileio.loadManifest(path, inputText)
	else:
		print "Reading file '%s'" % inputFile
		files = [inputText]

	fileTexts = []
	for file in files:
		fileTexts.append(file)
	joinedFileTexts = ''.join(fileTexts)
	collapsedText = collapse.go(joinedFileTexts)

	outputText = latexifier.go(collapsedText)

	postLatexSanityCheck(outputText)

	outputText = latexWrapper(outputText, includeFrontMatter=False)	

	fileio.writeOutputFile(outputFile, outputText)



main()
