# coding=utf-8


import renderer
import re
import fileio
import renderer_epub
import sys
import terminal

class RendererKPF(renderer.Renderer):

	def render(self):
		self.makeStagedFile()
		self.makeOutputFile()

	def makeStagedFile(self):
		renderer = renderer_epub.RendererEPub(self.collapsedText, self.params)
		renderer.render()

	def makeOutputFile(self):
		print "Rendering to kpf."
		# We start with an .epub file in the outputDir.
		inputFile = "%s%s.epub" % (self.params.workDir, self.params.fileId)
		if self.params.finalOutput:
			inputFile = "%s%s.epub" % (self.params.outputDir, self.params.fileId)
		outputEPub(inputFile)
		# Now we also have a .kpf file in outputDir/KPF.
		kpfLoc = "%s/output/KPF/%s.kpf" % (self.params.workDir, self.params.fileId)
		terminal.move(kpfLoc, "%s%s.kpf" % (self.params.outputDir, self.params.fileId))
		# If final output, move the .epub file to work.
		if self.params.finalOutput:
			terminal.move(inputFile, "%s%s.epub" % (self.params.workDir, self.params.fileId))
		terminal.delete("%s/output" % self.params.outputDir, isDir=True)

	def renderFormattingSequence(self, contents):
		pass

	def suggestEndMatters(self):
		return renderer_epub.RendererEPub(self.collapsedText, self.params).suggestEndMatters()



# Note: This requires KindleGen to be installed on the OS.
def outputEPub(inputFile):
	# result = terminal.runCommand('./kindlegen/kindlegen', '%s' % (inputFile))
	result = terminal.runCommand(r'/Applications/Kindle Previewer 3.app/Contents/MacOS/Kindle Previewer 3', '%s -convert' % (inputFile))
	if not result["success"]: # Note: doesn't work for new Amazon
		print "*** Couldn't run Kindle Previewer 3; aborting."
		print result["output"]
		sys.exit()
