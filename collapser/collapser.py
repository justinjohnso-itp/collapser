#!/usr/bin/python

import sys

import fileio

inputFile = ""
outputFile = ""
inputText = ""
outputText = ""

def showUsage():
	print """Usage: collapser <INPUT> <OUTPUT> options"""




def processText(inputText):
	return inputText


print """Collapser 0.1"""

if len(sys.argv) != 3:
	showUsage()
	sys.exit()



inputFile = sys.argv[1]
outputFile = sys.argv[2]

inputText = fileio.readInputFile(inputFile)

print "Here is the input:\n%s" % inputText

outputText = processText(inputText)

print "\n\nHere is the output:\n%s" % outputText

fileio.writeOutputFile(outputFile, outputText)