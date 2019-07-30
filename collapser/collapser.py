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

def showUsage():
	print """Usage: collapser <INPUT> <OUTPUT> options"""


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

	inputText = fileio.readInputFile(inputFile)

	# print "Here is the input:\n%s" % inputText

	collapsedText = collapse.go(inputText)

	outputText = latexifier.go(collapsedText)

	postLatexSanityCheck(outputText)


	# print "\n\nHere is the output:\n%s" % outputText

	fileio.writeOutputFile(outputFile, outputText)



main()
