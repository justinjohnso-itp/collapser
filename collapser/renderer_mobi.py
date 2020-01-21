# coding=utf-8


import renderer
import re
import fileio
import renderer_epub
import sys
import terminal

class RendererMobi(renderer.Renderer):

	def render(self):
		self.makeStagedFile()
		self.makeOutputFile()

	def makeStagedFile(self):
		renderer = renderer_epub.RendererEPub(self.collapsedText, self.params)
		renderer.render()

	def makeOutputFile(self):
		print "Rendering to mobi."
		inputFile = self.params.outputDir + self.params.fileId + ".epub"
		outputEPub(inputFile)

	def renderFormattingSequence(self, contents):
		pass

	def suggestEndMatters(self):
		return renderer_epub.RendererEPub(self.collapsedText, self.params).suggestEndMatters()



# Note: This requires KindleGen to be installed on the OS.
def outputEPub(inputFile):
	result = terminal.runCommand('./kindlegen/kindlegen', '%s' % (inputFile))
	if not result["success"]:
		print "*** Couldn't run kindlegen; aborting."
		print result["output"]
		sys.exit()
