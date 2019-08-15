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



latexBegin = "fragments/begin.tex"
latexEnd = "fragments/end.tex"
latexFrontMatter = "fragments/frontmatter.tex"
latexPostFrontMatter = "fragments/postfrontmatter.tex"



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
def postConversionSanityCheck(text):
	# Look for unexpected characters etc. here
	pos = text.find('_')
	if pos is not -1:
		raise ValueError("Found invalid underscore '_' character on line %d:\n%s" % (quantlex.find_line_number(text, pos), quantlex.find_line_text(text, pos)) )
	
	# pos = text.find('''"''')
	# if pos is not -1:
	# 	raise ValueError("Found dumb quote character on line %d; use “ ” \n%s" % (quantlex.find_line_number(text, pos), quantlex.find_line_text(text, pos)) )

	return

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
  		"longest"
  		"shortest"
  --set=x,y,z	 A list of variables to set true for this run.
"""


def main():

	print """Collapser 0.1"""

	inputFile = ""
	outputFile = ""
	inputText = ""
	outputText = ""
	seed = -1
	strategy = "random"
	doPDF = True
	doFront = False
	doConfirm = True
	pdfOutputDir = "output/"
	setDefines = []

	opts, args = getopt.getopt(sys.argv[1:], "i:o:", ["help", "seed=", "strategy=", "nopdf", "noconfirm", "front", "set="])
	print opts
	print args
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

	if inputFile == "" or outputFile == "":
		print "Missing input or output file."
		showUsage()
		sys.exit()

	if seed is -1:
		seed = chooser.number(10000000)
		print "Seed (random): %d" % seed
	else:
		print "Seed (requested): %d" % seed
	chooser.setSeed(seed)

	files = []
	inputText = fileio.readInputFile(inputFile)
	if inputFile[-12:] == "manifest.txt":
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
	params = quantparse.ParseParams(chooseStrategy = strategy, preferenceForAuthorsVersion = 20, setDefines = setDefines, doConfirm = doConfirm)
	collapsedText = collapse.go(joinedFileTexts, params)
	if collapsedText == "":
		sys.exit()

	fileio.writeOutputFile("output/raw_out.txt", collapsedText)

	outputText = latexifier.go(collapsedText)

	postConversionSanityCheck(outputText)

	outputText = latexWrapper(outputText, includeFrontMatter=doFront)	

	fileio.writeOutputFile(outputFile, outputText)

	if doPDF:
		print "Running lualatex..."
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
	else:
		print "Skipping PDF."


main()
