#!/usr/bin/python
# coding=utf-8

import sys
import getopt
import re

import fileio
import collapse
import latexifier
import quantlex
import quantparse
import chooser
import result
import differ
import terminal

latexBegin = "fragments/begin.tex"
latexEnd = "fragments/end.tex"
latexFrontMatter = "fragments/frontmatter.tex"
latexPostFrontMatter = "fragments/postfrontmatter.tex"
manifestFile = "manifest.txt"
pdfOutputDir = "output/"
alternateOutputFile = pdfOutputDir + "alternate.tex"
rawOutputFile = pdfOutputDir + "raw_out.txt"
blankPDF = "extras/blankpages.pdf"



def showUsage():
	print """Usage: collapser -i <INPUT> -o <OUTPUT> options
Arguments:
  --help         Show this message
  --front		 Include frontmatter
  --seed=x       Use the given integer as a seed
  --nopdf		 Skip pdf generation
  --noconfirm	 Skip variant confirmation
  --strategy=x   Selection strategy.
  		"random": default
  		"author": Author's preferred
  		"pair": Two versions optimizing for difference
  		"longest"
  		"shortest"
  --set=x,y,z	 A list of variables to set true for this run.
                 Preface with ^ to negate
  --discourseVarChance=x   Likelihood to defer to a discourse var (default 80)
  --pickAuthorChance=x		Likelihood to pick author-preferred at random
  --padding=x		Pad the output PDF to the given number of pages
"""


def main():

	print """Collapser 0.1\n"""

	inputFile = ""
	outputFile = ""
	inputText = ""
	outputText = ""
	seed = -1
	strategy = "random"
	doPDF = True
	doFront = False
	doConfirm = True
	setDefines = []
	discourseVarChance = 80
	preferenceForAuthorsVersion = 20
	padding = -1

	opts, args = getopt.getopt(sys.argv[1:], "i:o:", ["help", "seed=", "strategy=", "nopdf", "noconfirm", "front", "set=", "discourseVarChance=", "pickAuthorChance=", "padding="])
	if len(args) > 0:
		print "Unrecognized arguments: %s" % args
		sys.exit()
	for opt, arg in opts:
		if opt == "-i":
			inputFile = arg
		elif opt == "-o":
			outputFile = arg
		elif opt == "--help":
			print "Help."
			showUsage()
			sys.exit()
		elif opt == "--seed":
			try:
				seed = int(arg)
			except:
				print "Invalid --seed parameter '%s': not an integer." % arg
				sys.exit()
		elif opt == "--strategy":
			if arg not in quantparse.ParseParams.VALID_STRATEGIES:
				print "Invalid --strategy parameter '%s': must be one of %s" % (arg, quantparse.ParseParams.VALID_STRATEGIES)
			strategy = arg
		elif opt == "--nopdf":
			doPDF = False
		elif opt == "--noconfirm":
			doConfirm = False
		elif opt == "--front":
			doFront = True
		elif opt == "--set":
			setDefines = arg.split(',')
		elif opt == "--discourseVarChance":
			try:
				discourseVarChance = int(arg)
			except:
				print "Invalid --discourseVarChance parameter '%s': not an integer." % arg
				sys.exit()
		elif opt == "--pickAuthorChance":
			try:
				preferenceForAuthorsVersion = int(arg)
			except:
				print "Invalid --pickAuthorChance parameter '%s': not an integer." % arg
				sys.exit()
		elif opt == "--padding":
			try:
				padding = int(arg)
			except:
				print "Invalid --padding parameter '%s': not an integer." % arg
				sys.exit()

	if inputFile == "" or outputFile == "":
		print "*** Missing input or output file. ***\n"
		showUsage()
		sys.exit()

	if seed is not -1 and strategy is not "random":
		print "*** You set seed to %d but strategy to '%s'; a seed can only be used when strategy is 'random' ***\n" % (seed, strategy)
		sys.exit()

	if seed is not -1 and len(setDefines) is not 0:
		print "*** You set seed to %d but also set variables %s; you need to do one or the other ***\n" % (seed, setDefines)
		sys.exit()

	params = quantparse.ParseParams(chooseStrategy = strategy, preferenceForAuthorsVersion = preferenceForAuthorsVersion, setDefines = setDefines, doConfirm = doConfirm, discourseVarChance = discourseVarChance)

	if strategy == "pair":
		texts = []
		tries = 10
		seeds = []
		seed = chooser.nextSeed()
		for x in range(tries):
			seeds.append(seed)
			texts.append(getCollapsedTextFromFile(inputFile, params))
			seed = chooser.nextSeed()
		leastSimilarPair = differ.getTwoLeastSimilar(texts)
		text0 = texts[leastSimilarPair[0]]
		seed0 = seeds[leastSimilarPair[0]]
		text1 = texts[leastSimilarPair[1]]
		seed1 = seeds[leastSimilarPair[1]]
		makeOutputFile(text0, outputFile, seed0, doFront)
		makeOutputFile(text1, alternateOutputFile, seed1, doFront)
		if doPDF:
			print "Running lualatex (text 1)..."
			outputPDF(outputFile, padding)
			print "Running lualatex (text 2)..."
			outputPDF(alternateOutputFile, padding)

	else:
		if strategy != "random":
			print "Ignoring seed (b/c strategy = %s)" % strategy
		elif seed is -1:
			seed = chooser.nextSeed()
			print "Seed (next): %d" % seed
		else:
			chooser.setSeed(seed)
			print "Seed (requested): %d" % seed
		collapsedText = getCollapsedTextFromFile(inputFile, params)
		makeOutputFile(collapsedText, outputFile, seed, doFront)
		if doPDF:
			print "Running lualatex..."
			outputPDF(outputFile, padding)
		else:
			print "Skipping PDF."



def getCollapsedTextFromFile(inputFile, params):
	files = []
	inputText = fileio.readInputFile(inputFile)
	if inputFile[-12:] == manifestFile:
		path = inputFile[:-12]
		print "Reading manifest '%s'" % inputFile
		files = fileio.loadManifest(path, inputText)
	else:
		print "Reading file '%s'" % inputFile
		fileHeader = fileio.getFileId(inputFile)
		files = [fileHeader + inputText]

	fileTexts = []
	for file in files:
		fileTexts.append(file)
	joinedFileTexts = ''.join(fileTexts)
	collapsedText = collapse.go(joinedFileTexts, params)
	if collapsedText == "":
		sys.exit()

	return collapsedText

def makeOutputFile(collapsedText, outputFile, seed, doFront):
	fileio.writeOutputFile(rawOutputFile, collapsedText)

	latexTemplateFiles = {
		"begin": fileio.readInputFile(latexBegin),
		"end": fileio.readInputFile(latexEnd),
		"frontMatter": fileio.readInputFile(latexFrontMatter),
		"postFrontMatter": fileio.readInputFile(latexPostFrontMatter)
	}

	outputText = latexifier.go(collapsedText, latexTemplateFiles, seed, doFront)
	fileio.writeOutputFile(outputFile, outputText)

def outputPDF(outputFile, padding):
	result = terminal.runCommand('lualatex', '-interaction=nonstopmode -synctex=1 -recorder --output-directory="%s" "%s" ' % (pdfOutputDir, outputFile))
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

	return True

def getStats(latexLog):
	data = { "numPages": -1, "numBytes": -1 }
	result = re.search(r"Output written on .*\.pdf \(([0-9]+) pages, ([0-9]+) bytes", latexLog)
	if result:
		data["numPages"] = int(result.groups()[0])
		data["numBytes"] = int(result.groups()[1])
	return data



def addPadding(outputFile, reportedPages, desiredPageCount):

	numPDFPages = terminal.countPages("output/combined.pdf")
	if numPDFPages != reportedPages:
		print "*** Latex reported generating %d page PDF, but pdftk reported the output was %d pages instead. Aborting." % (reportedPages, numPDFPages)
		sys.exit()

	if numPDFPages > desiredPageCount:
		print "*** Generation exceeded maximum length of %d page: was %d pages." % (desiredPageCount, numPDFPages)
		sys.exit()

	# If equal, no action needed. Otherwise, add padding to the desired number of pages, which must remain constant in print on demand so the cover art doesn't need to be resized.

	if numPDFPages < desiredPageCount:
		terminal.addBlankPages("output/combined.pdf", "output/combined-padded.pdf", desiredPageCount - numPDFPages)
		numCombinedPages = terminal.countPages("output/combined-padded.pdf")
		if numCombinedPages != desiredPageCount:
			print "*** Tried to pad output PDF to %d pages but result was %d pages instead." % (desiredPageCount, numPDFPages)
			sys.exit()




main()
