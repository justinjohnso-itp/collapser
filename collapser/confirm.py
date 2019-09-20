# coding=utf-8
# Manually confirm each use of variants.

import ctrlseq
import result
import re
import getch
import sys
import textwrap

import fileio

# TODO Macros?
# TODO: Don't add truncs if there's actually nothing to trunc (i.e. we're at the start/end of the sequence)

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


def confirmCtrlSeq(ctrl_contents, sourceText, parseParams, ctrlEndPos):

	maxLineLength = 80
	variants = ctrlseq.renderAll(ctrl_contents, parseParams, showAllVars=True)
	ctrlStartPos = sourceText.rfind("[", 0, ctrlEndPos)
	pre = getPre(sourceText, ctrlStartPos, ctrlEndPos)
	post = getPost(sourceText, ctrlEndPos)
	originalCtrlSeq = sourceText[ctrlStartPos:ctrlEndPos+1]
	filename = result.find_filename(sourceText, ctrlStartPos)
	key = "%s:%s%s%s" % (filename, pre, originalCtrlSeq, post)
	key = re.sub(r'[\W_]', '', key)
	truncStart = "..."
	truncEnd = "..."
	if fileio.isKeyConfirmed(key) == False:
		lineNumber = result.find_line_number_for_file(sourceText, ctrlStartPos)
		lineColumn = result.find_column(sourceText, ctrlStartPos)
		print "\n\n"
		print "##################################################"
		print "VARIANT FOUND IN %s LINE %d COL %d:\n%s" % (filename, lineNumber, lineColumn, originalCtrlSeq)
		for v in variants.alts:
			print '''************************************'''
			rendered = renderVariant(truncStart, pre, v.txt, post, truncEnd, maxLineLength)
			print rendered
		print "************************************"

		choice = -1
		while choice is not "1" and choice is not "2" and choice is not "3":
			sys.stdout.write("\n1) Confirm, 2) Skip, 3) Stop > ")
			choice = getch.getch()
			if choice == "1":
				print "1\n >>> Confirmed."
				fileio.confirmKey(key)
				return
			elif choice == "2":
				print "2\n >>> Skipping."
				return
			elif choice == "3":
				print "3\n >>> Halting."
				fileio.finishConfirmKeys()
				sys.exit(0)


def renderVariant(truncStart, pre, variant, post, truncEnd, maxLineLength):
	rendered = "%s%s%s%s%s" % (truncStart, pre, variant, post, truncEnd)
	rendered = cleanFinal(rendered)
	wrapped = wrap(rendered, maxLineLength)
	print "pre: '%s'" % pre
	# Figure out what line the variant starts on.
	prevNL = result.find_previous(wrapped, "\n", len(truncStart + pre))
	print "prevNL: %d" % prevNL
	numSpaces = len(truncStart + pre) - prevNL
	print "numSpaces: %d" % numSpaces
	spaces = " " * numSpaces
	endVariantPos = len(wrapped) - len(post) - len(truncEnd)
	nextNewLinePos = wrapped.find("\n", len(truncStart + pre + variant))
	print "nextNewLinePos: %d" % nextNewLinePos
	if numSpaces + len(variant + post + truncEnd) < maxLineLength and post.find("\n") == -1:
		print "!! Single line"
		# Single line.
		numSpacesBetween = len(variant) - 2
		print "numSpacesBetween: %d" % numSpacesBetween
		spacesBetween = " " * numSpacesBetween
		wrapped = wrapped + spaces + "^" + spacesBetween + "^\n"
	else:
		print "!! MULTI Line"
		if prevNL == 0:
			wrapped = spaces + "v\n" + wrapped
		else:
			wrapped = wrapped[:prevNL-1] + "\n" + spaces + "v" + wrapped[prevNL-1:]
		endVariantPos = len(wrapped) - len(post) - len(truncEnd)
		nextNewLinePos = wrapped.find("\n", endVariantPos)
		lastNewLinePos = result.find_previous(wrapped, "\n", endVariantPos)
		print "last, next: %d, %d" % (lastNewLinePos, nextNewLinePos)
		numSpaces = endVariantPos - lastNewLinePos - 2
		print "numSpaces: %d" % numSpaces
		spaces = " " * numSpaces
		print "spaces: '%s'" % spaces
		wrapped = wrapped[:nextNewLinePos+1] + spaces + "^\n" + wrapped[nextNewLinePos+1:]	
	return wrapped


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

	# Replace common Unicode chars with ascii equivalents since wrap (for terminal) can't handle them.
	text = re.sub(r"’", "'", text)
	text = re.sub(r"‘", "'", text)
	text = re.sub(r"“", '"', text)
	text = re.sub(r"”", '"', text)

	return text


def cleanFinal(text):
	# Remove doubled spaces (which won't be visible post-Latex and are therefore just a distraction). 
	text = re.sub(r"  +", " ", text)

	return text


def wrap(text, maxLineLength):
	output = ""
	for line in text.split('\n'):
		output += textwrap.fill(line, maxLineLength) + "\n"
	return output
