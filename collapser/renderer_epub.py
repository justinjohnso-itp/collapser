# coding=utf-8


import renderer
import re
import fileio

class RendererEPub(renderer.Renderer):

	def render(self):
		self.makeStagedFile()
		self.makeOutputFile()

	def makeStagedFile(self):
		pass

	def makeOutputFile(self):
		pass



def generateTitle():
	return """---
title: Subcutanean
author: Aaron A. Reed
rights: All Rights Reserved
language: en-US
date: 2020-02-02
...

"""


