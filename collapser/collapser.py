#!/usr/bin/python
# coding=utf-8

import sys
import getopt
import subprocess
import shlex
import re

import fileio
import collapse
import latexifier
import quantlex
import quantparse
import chooser
import result
import differ


latexBegin = "fragments/begin.tex"
latexEnd = "fragments/end.tex"
latexFrontMatter = "fragments/frontmatter.tex"
latexPostFrontMatter = "fragments/postfrontmatter.tex"
manifestFile = "manifest.txt"
alternateOutputFile = "output/alternate.tex"
rawOutputFile = "output/raw_out.txt"

def postLatexSanityCheck(latexLog):
	numPages = 0

	overfulls = len(re.findall(r"\nOverfull \\hbox", latexLog))
	if overfulls > 500:
		print "Too many overfulls (found %d); halting." % overfulls
		return False

	status = re.search(r"Output written on .*\.pdf \(([0-9]+) pages, ([0-9]+) bytes", latexLog)
	if status:
		numPages = int(status.groups()[0])
		numBytes = int(status.groups()[1])
		if numPages < 5 or numPages > 300:
			print "Unexpected page length (%d); halting." % numPages
			return False
		if numBytes < 100000 or numBytes > 1000000:
			print "Unexpected size (%d kb); halting." % (numBytes / 1000)
			return False
	else:
		print "Couldn't find output line; halting."
		return False

	return numPages


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
  --discourseVarChance=x   Likelihood to defer to a discourse var (default 80)
  --pickAuthorChance=x		Likelihood to pick author-preferred at random
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

	opts, args = getopt.getopt(sys.argv[1:], "i:o:", ["help", "seed=", "strategy=", "nopdf", "noconfirm", "front", "set=", "discourseVarChance=", "pickAuthorChance="])
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
			outputPDF(outputFile)
			print "Running lualatex (text 2)..."
			outputPDF(alternateOutputFile)

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
			outputPDF(outputFile)
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

def outputPDF(outputFile):
	pdfOutputDir = "output/"
	cmdParams = '-interaction=nonstopmode -synctex=1 -recorder --output-directory="%s" "%s" ' % (pdfOutputDir, outputFile)
	cmdArray = shlex.split(cmdParams)
	cmdArray.insert(0, "lualatex")

	try:
		output = subprocess.check_output(cmdArray,stderr=subprocess.STDOUT)
	except subprocess.CalledProcessError as e:
		# For some reason this is failing with error code 1 even when it successfully works, so we need to do our own post-processing.
		latexlog = e.output
		result = postLatexSanityCheck(latexlog)
		if result is False:
			print "*** Generation failed. Check .log file in output folder."
		else:
			print "Success! Generated %d page PDF." % result
		# raise RuntimeError("command '{}' return with error (code {})".format(e.cmd, e.returncode))	


main()
