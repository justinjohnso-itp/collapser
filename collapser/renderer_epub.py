# coding=utf-8


import renderer
import re
import fileio
import renderer_markdown
import sys
import terminal

class RendererEPub(renderer.Renderer):

	def render(self):
		self.makeStagedFile()
		self.makeOutputFile()

	def makeStagedFile(self):
		renderer = renderer_markdown.RendererMarkdown(self.collapsedText, self.params)
		renderer.render()

	def makeOutputFile(self):
		print "Rendering to epub."
		outputDir = self.params["outputDir"]
		inputFile = outputDir + self.params["fileId"] + ".md"
		outputFile = outputDir + self.params["fileId"] + ".epub"
		title = generateTitle(self.params["seed"])
		fileio.writeOutputFile(outputDir + "title.md", title)
		outputEPub(outputDir, inputFile, outputFile)

	def renderFormattingSequence(self, contents):
		pass


def generateTitle(seed):
	if seed == -1:
		seed = "01893-b"
	return """---
title: Subcutanean %s
author: Aaron A. Reed
rights: All Rights Reserved
language: en-US
date: 2020-02-02
cover-image: fragments/subcutanean-ebook-cover.jpg
...

""" % seed

# Note: This requires pandoc to be installed on the OS.
def outputEPub(outputDir, inputFile, outputFile):
	result = terminal.runCommand('pandoc', '%stitle.md %s -o %s --css=fragments/epub.css --toc' % (outputDir, inputFile, outputFile))
	if not result["success"]:
		print "*** Couldn't run pandoc; aborting."
		print result["output"]
		sys.exit()
