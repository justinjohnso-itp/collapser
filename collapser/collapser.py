#!/usr/bin/python
# coding=utf-8

# TODO: Make an abstraction that holds the tokens for the book and rendered text in parallel, so you can say "show me the rendered text(s) for this particular control sequence", interrogate the control sequence at a specific position in the rendered text, etc.

# TODO: Proof 01915 has Part 3 starting on the wrong page. 

import sys
import getopt
import re

import fileio
import collapse
import quantlex
import quantparse
import chooser
import result
import differ
import renderer_latex
import renderer_text
import renderer_html
import renderer_markdown
import renderer_epub
import renderer_mobi

manifestFile = "manifest.txt"
outputDir = "output/"
alternateOutputFile = outputDir + "alternate"
collapsedFileName = outputDir + "collapsed.txt"



def showUsage():
	print """Usage: collapser -i <INPUT> -o <OUTPUT_KEY> options
Arguments:
  --help         Show this message
  --front		 Include frontmatter
  --seed=x       Use the given integer as a seed
  --seed=random  Don't use an incremental seed; use one purely at random.
  --output=x	 Format to output (default none)
  				 "pdf" (for POD), "pdfdigital" (for online use),
  				 "txt", "html", "md", "epub", "mobi"
  --noconfirm	 Skip variant confirmation
  --strategy=x   Selection strategy.
  		"random": default
  		"skipbanned": random, but avoid banned alternatives
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
	outputFormat = ""
	doFront = False
	doConfirm = True
	setDefines = []
	discourseVarChance = 80
	preferenceForAuthorsVersion = 20
	padding = -1
	randSeed = False
	isDigital = False

	VALID_OUTPUTS = ["pdf", "pdfdigital", "txt", "html", "md", "epub", "mobi", "none"]

	opts, args = getopt.getopt(sys.argv[1:], "i:o:", ["help", "seed=", "strategy=", "output=", "noconfirm", "front", "set=", "discourseVarChance=", "pickAuthorChance=", "padding="])
	if len(args) > 0:
		print "Unrecognized arguments: %s" % args
		sys.exit()
	for opt, arg in opts:
		if opt == "-i":
			inputFile = arg
		elif opt == "-o":
			if len(re.findall(r"(\/|(\.(pdf|tex|txt)))", arg)) > 0:
				print "Please do not include paths or file extensions in output file (use --output to specify format)."
				sys.exit()
			outputFile = arg
		elif opt == "--help":
			print "Help."
			showUsage()
			sys.exit()
		elif opt == "--seed":
			if arg == "random":
				randSeed = True
			else:
				try:
					seed = int(arg)
				except:
					print "Invalid --seed parameter '%s': not an integer." % arg
					sys.exit()
		elif opt == "--strategy":
			if arg not in quantparse.ParseParams.VALID_STRATEGIES:
				print "Invalid --strategy parameter '%s': must be one of %s" % (arg, quantparse.ParseParams.VALID_STRATEGIES)
			strategy = arg
		elif opt == "--output":
			if arg != "" and arg not in VALID_OUTPUTS:
				print "Invalid --output parameter '%s': must be one of %s" % (arg, VALID_OUTPUTS)
			if arg == "pdfdigital":
				arg = "pdf"
				isDigital = True
			outputFormat = arg
			if arg == "none":
				outputFormat = ""
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

	if seed is not -1 and strategy is not "random" and strategy is not "skipbanned":
		print "*** You set seed to %d but strategy to '%s'; a seed can only be used when strategy is 'random' or 'skipbanned' ***\n" % (seed, strategy)
		sys.exit()

	if seed is not -1 and len(setDefines) is not 0:
		print "*** You set seed to %d but also set variables %s; you need to do one or the other ***\n" % (seed, setDefines)
		sys.exit()

	params = quantparse.ParseParams(chooseStrategy = strategy, preferenceForAuthorsVersion = preferenceForAuthorsVersion, setDefines = setDefines, doConfirm = doConfirm, discourseVarChance = discourseVarChance)

	if strategy == "pair":
		# TODO make this work with new output format.
		texts = []
		tries = 10
		seeds = []
		seed = chooser.nextSeed()
		for x in range(tries):
			seeds.append(seed)
			texts.append(collapseInputText(inputFile, params))
			seed = chooser.nextSeed()
		leastSimilarPair = differ.getTwoLeastSimilar(texts)
		text0 = texts[leastSimilarPair[0]]
		seed0 = seeds[leastSimilarPair[0]]
		text1 = texts[leastSimilarPair[1]]
		seed1 = seeds[leastSimilarPair[1]]
		render(outputFormat, text0, outputDir, outputFile, seed0, doFront, padding, isDigital)
		render(outputFormat, text1, outputDir, alternateOutputFile, seed1, doFront, padding, isDigital)

	else:
		if strategy is not "random" and strategy is not "skipbanned":
			print "Ignoring seed (b/c strategy = %s)" % strategy
		elif randSeed:
			seed = chooser.randomSeed()
			print "Seed (purely random): %d" % seed
		elif seed is -1:
			seed = chooser.nextSeed()
			print "Seed (next): %d" % seed
		else:
			chooser.setSeed(seed)
			print "Seed (requested): %d" % seed

		collapsedText = collapseInputText(inputFile, params)
		fileio.writeOutputFile(collapsedFileName, collapsedText)

		render(outputFormat, collapsedText, outputDir, outputFile, seed, doFront, padding, isDigital)


def render(outputFormat, collapsedText, outputDir, outputFile, seed, doFront, padding, isDigital):
	if outputFormat != "":
		print "isDigital: %s" % isDigital
		renderParams = {
			"fileId": outputFile,
			"seed": seed,
			"doFront": doFront,
			"padding": padding,
			"outputDir": outputDir,
			"isDigital": isDigital
		}
		renderer = None
		if outputFormat == "pdf":
			renderer = renderer_latex.RendererLatex(collapsedText, renderParams)
		elif outputFormat == "txt":
			renderer = renderer_text.RendererText(collapsedText, renderParams)
		elif outputFormat == "html":
			renderer = renderer_html.RendererHTML(collapsedText, renderParams)
		elif outputFormat == "md":
			renderer = renderer_markdown.RendererMarkdown(collapsedText, renderParams)
		elif outputFormat == "epub":
			renderer = renderer_epub.RendererEPub(collapsedText, renderParams)
		elif outputFormat == "mobi":
			renderer = renderer_mobi.RendererMobi(collapsedText, renderParams)

		if renderer is None:
			print "No rendering requested or available."
		else:
			renderer.render()



def collapseInputText(inputFile, params):
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






main()
