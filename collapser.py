#!/usr/bin/python

import sys

inputFile = ""
outputFile = ""
inputText = ""
outputText = ""

def showUsage():
	print """Usage: collapser <INPUT> <OUTPUT> options"""


def readInputFile(inputFile):
	fileContents = ""
	with open(inputFile, "r") as fileObject:
		return fileObject.read()
	print "Can't read '%s'." % inputFile
	sys.exit()

def processText(inputText):
	return inputText

def writeOutputFile(outputFile, outputText):
	with open(outputFile, "w") as fileObject:
		fileObject.write(outputText)
		print "\nWrote to '%s'.\n" % outputFile


print """Collapser 0.1"""

if len(sys.argv) != 3:
	showUsage()
	sys.exit()



inputFile = sys.argv[1]
outputFile = sys.argv[2]

inputText = readInputFile(inputFile)

print "Here is the input:\n%s" % inputText

outputText = processText(inputText)

print "\n\nHere is the output:\n%s" % outputText

writeOutputFile(outputFile, outputText)