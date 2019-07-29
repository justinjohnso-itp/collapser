#!/usr/bin/python

import sys

import fileio
import collapse
import latexifier

inputFile = ""
outputFile = ""
inputText = ""
outputText = ""

def showUsage():
	print """Usage: collapser <INPUT> <OUTPUT> options"""


def sanityCheck(text):
	# Look for unexpected characters etc. here
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

	sanityCheck(outputText)

	# print "\n\nHere is the output:\n%s" % outputText

	fileio.writeOutputFile(outputFile, outputText)



main()
