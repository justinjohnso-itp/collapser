# Manually confirm each use of variants.

import ctrlseq
import result
import re
import getch
import sys
import textwrap

import fileio

# TODO Wordwrap.
# TODO Macros?

# We should have a series of text and CTRLBEGIN/END sequences.
def process(tokens, sourceText, parseParams):
	index = 0
	fileio.startConfirmKeys()
	while index < len(tokens):
		token = tokens[index]
		if token.type == "CTRLBEGIN":
			ctrl_contents = []
			index += 1
			token = tokens[index]
			while token.type != "CTRLEND":
				ctrl_contents.append(token)
				index += 1
				token = tokens[index]
			
			confirmCtrlSeq(ctrl_contents, sourceText, parseParams, token.lexpos)

		index += 1
	fileio.finishConfirmKeys()

maxLineLength = 80

def confirmCtrlSeq(ctrl_contents, sourceText, parseParams, ctrlEndPos):

	variants = ctrlseq.renderAll(ctrl_contents, parseParams, showAllVars=True)
	ctrlStartPos = sourceText.rfind("[", 0, ctrlEndPos)
	pre = getPre(sourceText, ctrlStartPos, ctrlEndPos)
	post = getPost(sourceText, ctrlEndPos)
	originalCtrlSeq = sourceText[ctrlStartPos:ctrlEndPos+1]
	filename = result.find_filename(sourceText, ctrlStartPos)
	key = "%s:%s%s%s" % (filename, pre, originalCtrlSeq, post)
	key = re.sub(r'[\W_]', '', key)
	if fileio.isKeyConfirmed(key) == False:
		lineNumber = result.find_line_number_for_file(sourceText, ctrlStartPos)
		lineColumn = result.find_column(sourceText, ctrlStartPos)
		print "\n\n"
		print "##################################################"
		print "VARIANT FOUND IN %s LINE %d COL %d:\n%s" % (filename, lineNumber, lineColumn, originalCtrlSeq)
		for v in variants.alts:
			showVariant(v.txt, pre, post)
		print "************************************"

		choice = -1
		while choice is not "1" and choice is not "2" and choice is not "3":
			sys.stdout.write("\n1) Confirm, 2) Skip, 3) Stop > ")
			choice = getch.getch()
			if choice == "1":
				print "1\n >>> Confirmed."
				fileio.confirmKey(key)
			elif choice == "2":
				print "2\n >>> Skipping."
			elif choice == "3":
				print "3\n >>> Halting."
				fileio.finishConfirmKeys()
				sys.exit(0)

def showVariant(variant, pre, post):
	print '''************************************'''
	truncStart = "..."
	truncEnd = "..."
	rendered = getRenderedVariant(truncStart, pre, variant, post, truncEnd)
	print rendered


def getRenderedVariant(truncStart, pre, variant, post, truncEnd):
	rendered = "%s%s%s%s%s" % (truncStart, pre, variant, post, truncEnd)
	rendered = cleanFinal(rendered)
	wrapped = wrap(rendered)

	# Figure out what line the variant starts on.
	# What the position in wrapped of the previous newline?
	prevNL = result.find_previous(wrapped, "\n", len(truncStart + pre))
	# How many spaces from that point does the variant start?
	numSpaces = len(truncStart + pre) - prevNL
	spaces = " " * numSpaces
	# Insert spaces right before that.
	wrapped = wrapped[:prevNL-1] + spaces + "v" + wrapped[prevNL-1:]

	# What's the position in wrapped of the end of the variant?
	endVariantPos = len(wrapped) - len(post) - len(truncEnd)
	print "endVariantPos: %d, '%s'" % (endVariantPos, wrapped[endVariantPos-3:endVariantPos+3])
	# What's the position of the new line before that?
	lastNewLinePos = result.find_previous(wrapped, "\n", endVariantPos)
	# What about the next new line?
	nextNewLinePos = wrapped.find("\n", endVariantPos)
	print "last, next: %d, %d" % (lastNewLinePos, nextNewLinePos)
	if lastNewLinePos == prevNL:
		print "On the same line"
	else:
		numSpaces = endVariantPos - lastNewLinePos - 2
		print "numSpaces: %d" % numSpaces
		spaces = " " * numSpaces
		print "spaces: '%s'" % spaces
		wrapped = wrapped[:nextNewLinePos+1] + spaces + "^\n" + wrapped[nextNewLinePos+1:]	
	return wrapped


	# varLine = result.find_line_number(pre, len(pre)) - 1
	# print "varLine: %d" % varLine
	# charsInLine = result.find_previous(pre, "\n", len(pre))
	# wrapped = wrapped[0:len(pre)-charsInLine] + "\n" + (" " * charsInLine) + "v" + wrapped[len(pre)-charsInLine:]
	# # wrappedLines.insert(varLine, padding + "v")

	# # Figure out what line the variant ends on.
	# endLine = result.find_line_number(rendered, len(pre) + len(variant))
	# print "endLine: %d" % endLine
	# posOfEndLineStart = result.find_previous(rendered, "\n", len(pre) + len(variant))
	# endCol = len(pre) + len(variant) - posOfEndLineStart
	# endPadding = " " * endCol
	# # wrappedLines.insert(endLine, padding + "^")

	# print wrapped
	# if len(str(variant)) < maxLineLength:
	# 	print (" " * (preLen+len(truncStart)-1)) + ">" + (" " * (len(str(variant)))) + "<"


def getPre(sourceText, ctrlStartPos, ctrlEndPos):
	preBufferLen = 60
	if ctrlStartPos < preBufferLen:
		preBufferLen = ctrlStartPos
	pre = sourceText[ctrlStartPos-preBufferLen:ctrlStartPos]
	pre = cleanContext(pre)
	return pre

def getPost(sourceText, ctrlEndPos):
	postBufferLen = 60
	if ctrlEndPos + postBufferLen > len(sourceText):
		postBufferLen = len(sourceText) - ctrlEndPos
	post = sourceText[ctrlEndPos+1:ctrlEndPos+postBufferLen]
	post = cleanContext(post)
	return post

def cleanContext(text):
	# Strip comments.
	text = re.sub(r"[#%].*\n", "\n", text)

	# Remove extra blank lines
	text = re.sub(r"\n{3,}", "\n\n", text) 

	return text


def cleanFinal(text):
	# Remove doubled spaces (which won't be visible post-Latex and are therefore just a distraction). 
	text = re.sub(r"  +", " ", text)

	return text


def wrap(text):
	output = ""
	for line in text.split('\n'):
		output += textwrap.fill(line, maxLineLength) + "\n"
	return output
