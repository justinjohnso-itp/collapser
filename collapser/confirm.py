# coding=utf-8
# Manually confirm each use of variants.

import ctrlseq
import result
import re
import getch
import sys
import textwrap
import chooser
import macros

import fileio

# TODO Macros?
# TODO: Don't add truncs if there's actually nothing to trunc (i.e. we're at the start/end of the sequence)

ctrlSeqsFound = []
ctrlSeqPos = -1

def getPreviousCtrlSeq():
	global ctrlSeqsFound
	global ctrlSeqPos
	if ctrlSeqPos <= 0:
		return None
	return ctrlSeqsFound[ctrlSeqPos-1]

def getNextCtrlSeq():
	global ctrlSeqsFound
	global ctrlSeqPos
	if ctrlSeqPos >= len(ctrlSeqsFound) - 1:
		return None
	return ctrlSeqsFound[ctrlSeqPos+1]

# We should have a series of text and CTRLBEGIN/END sequences.
def process(tokens, sourceText, parseParams):
	global ctrlSeqsFound
	global ctrlSeqPos
	
	preprocessTokens(tokens)

	ctrlSeqPos = 0
	fileio.startConfirmKeys()
	for seq, endPos in ctrlSeqsFound:
		confirmCtrlSeq(seq, sourceText, parseParams, endPos)
		ctrlSeqPos += 1

	fileio.finishConfirmKeys()

def preprocessTokens(tokens):
	global ctrlSeqsFound
	index = 0
	ctrlSeqsFound = []
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
			ctrlSeqsFound.append([ctrl_contents, token.lexpos])
		index += 1


def makeKey(sourceText, filename, ctrlStartPos, ctrlEndPos, originalCtrlSeq):
	pre = getRawPre(sourceText, ctrlStartPos, ctrlEndPos)
	post = getRawPost(sourceText, ctrlEndPos)
	key = "%s:%s%s%s" % (filename, pre, originalCtrlSeq, post)
	key = re.sub(r'[\W_]', '', key) # remove non-alphanums
	return key


def confirmCtrlSeq(ctrl_contents, sourceText, parseParams, ctrlEndPos):

	maxLineLength = 80
	variants = ctrlseq.renderAll(ctrl_contents, parseParams, showAllVars=True)
	ctrlStartPos = sourceText.rfind("[", 0, ctrlEndPos)
	filename = result.find_filename(sourceText, ctrlStartPos)
	originalCtrlSeq = sourceText[ctrlStartPos:ctrlEndPos+1]
	key = makeKey(sourceText, filename, ctrlStartPos, ctrlEndPos, originalCtrlSeq)
	truncStart = "..."
	truncEnd = "..."
	if fileio.isKeyConfirmed(key) == False:
		lineNumber = result.find_line_number_for_file(sourceText, ctrlStartPos)
		lineColumn = result.find_column(sourceText, ctrlStartPos)
		print "\n\n"
		print "#################################################################"
		print "VARIANT FOUND IN %s LINE %d COL %d:\n%s" % (filename, lineNumber, lineColumn, originalCtrlSeq)
		for v in variants.alts:
			print '''************************************'''
			rendered = renderVariant(truncStart, v.txt, truncEnd, maxLineLength, sourceText, parseParams, ctrlStartPos, ctrlEndPos)
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


def renderVariant(truncStart, variant, truncEnd, maxLineLength, sourceText, parseParams, ctrlStartPos, ctrlEndPos):
	pre = getRenderedPre(sourceText, parseParams, ctrlStartPos, ctrlEndPos)
	post = getRenderedPost(sourceText, parseParams, ctrlEndPos)
	rendered = "%s%s%s%s%s" % (truncStart, pre, variant, post, truncEnd)
	rendered = cleanFinal(rendered, parseParams)
	wrapped = wrap(rendered, maxLineLength)
	# print "pre: '%s'" % pre
	# Figure out what line the variant starts on.
	prevNL = result.find_previous(wrapped, "\n", len(truncStart + pre))
	# print "prevNL: %d" % prevNL
	numSpaces = len(truncStart + pre) - prevNL
	# print "numSpaces: %d" % numSpaces
	spaces = " " * numSpaces
	endVariantPos = len(wrapped) - len(post) - len(truncEnd)
	nextNewLinePos = wrapped.find("\n", len(truncStart + pre + variant))
	# print "nextNewLinePos: %d" % nextNewLinePos
	if numSpaces + len(variant + post + truncEnd) < maxLineLength and post.find("\n") == -1:
		# print "!! Single line"
		# Single line.
		numSpacesBetween = len(variant) - 2
		# print "numSpacesBetween: %d" % numSpacesBetween
		spacesBetween = " " * numSpacesBetween
		wrapped = wrapped + spaces + "^" + spacesBetween + "^\n"
	else:
		# print "!! MULTI Line"
		if prevNL == 0:
			wrapped = spaces + "v\n" + wrapped
		else:
			wrapped = wrapped[:prevNL-1] + "\n" + spaces + "v" + wrapped[prevNL-1:]
		endVariantPos = len(wrapped) - len(post) - len(truncEnd)
		nextNewLinePos = wrapped.find("\n", endVariantPos)
		lastNewLinePos = result.find_previous(wrapped, "\n", endVariantPos)
		# print "last, next: %d, %d" % (lastNewLinePos, nextNewLinePos)
		numSpaces = endVariantPos - lastNewLinePos - 2
		# print "numSpaces: %d" % numSpaces
		spaces = " " * numSpaces
		# print "spaces: '%s'" % spaces
		wrapped = wrapped[:nextNewLinePos+1] + spaces + "^\n" + wrapped[nextNewLinePos+1:]	
	# print "wrapped: '%s'" % wrapped
	return wrapped


def getRawPre(sourceText, ctrlStartPos, ctrlEndPos):
	preBufferLen = 240
	if ctrlStartPos < preBufferLen:
		preBufferLen = ctrlStartPos
	pre = sourceText[ctrlStartPos-preBufferLen:ctrlStartPos]
	pre = cleanContext(pre)
	return pre[-60:]

def getRawPost(sourceText, ctrlEndPos):
	postBufferLen = 240
	if ctrlEndPos + postBufferLen > len(sourceText):
		postBufferLen = len(sourceText) - ctrlEndPos
	post = sourceText[ctrlEndPos+1:ctrlEndPos+postBufferLen]
	post = cleanContext(post)
	return post[:60]

def getRenderedPost(sourceText, parseParams, ctrlEndPos):
	# print "ctrlEndPos: %d" % ctrlEndPos
	post = getRawPost(sourceText, ctrlEndPos)
	# print "post: '%s'" % post
	newCtrlSeqPos = post.find("[")
	if newCtrlSeqPos >= 0:
		newCtrlSeq = getNextCtrlSeq()
		if newCtrlSeq is not None:
			newVariants = ctrlseq.renderAll(newCtrlSeq[0], parseParams, showAllVars=True)
			# print "newVariants.alts: '%s'" % newVariants.alts
			variantTxt = chooser.oneOf(newVariants.alts, pure=True).txt
			endSeqPos = post.find("]", newCtrlSeqPos)
			if endSeqPos == -1:
				endSeqPos = len(post)
			# print "post was: '%s'" % post
			post = post[:newCtrlSeqPos] + variantTxt + post[endSeqPos+1:]
			# print "post now: '%s'" % post
			# truncate again
			postBufferLen = 60
			post = post[:postBufferLen]
	post = cleanContext(post)
	post = macros.expand(post, parseParams)
	return post

def getRenderedPre(sourceText, parseParams, ctrlStartPos, ctrlEndPos):
	# print "ctrlEndPos: %d" % ctrlEndPos
	pre = getRawPre(sourceText, ctrlStartPos, ctrlEndPos)
	# print "pre: '%s'" % pre
	newCtrlSeqPos = pre.rfind("]")
	if newCtrlSeqPos >= 0:
		newCtrlSeq = getPreviousCtrlSeq()
		if newCtrlSeq is not None:
			newVariants = ctrlseq.renderAll(newCtrlSeq[0], parseParams, showAllVars=True)
			# print "newVariants.alts: '%s'" % newVariants.alts
			variantTxt = chooser.oneOf(newVariants.alts, pure=True).txt
			startSeqPos = pre.rfind("[")
			if startSeqPos == -1:
				startSeqPos = 0
			# print "pre was: '%s'" % pre
			pre = pre[:startSeqPos] + variantTxt + pre[newCtrlSeqPos+1:]
			# print "pre now: '%s'" % pre
			# truncate again
			preBufferLen = 60
			pre = pre[-1*preBufferLen:]
			# print "post trunc, pre now: '%s'" % pre
	pre = cleanContext(pre)
	pre = macros.expand(pre, parseParams)
	return pre

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

	# remove macro definitions.
	pos = text.find("[MACRO")
	if pos is not -1:
		endDefPos = text.find("]", pos)
		endBodyPos = text.find("]", endDefPos+1)
		text = text[:pos-1] + text[endBodyPos+1:]

	return text


def cleanFinal(text, parseParams):
	# Remove doubled spaces (which won't be visible post-Latex and are therefore just a distraction). 
	text = re.sub(r"  +", " ", text)

	# Expand macros.
	text = macros.expand(text, parseParams)

	return text


def wrap(text, maxLineLength):
	output = ""
	for line in text.split('\n'):
		output += textwrap.fill(line, maxLineLength) + "\n"
	return output
