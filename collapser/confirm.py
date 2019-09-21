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


# We should have a series of text and CTRLBEGIN/END sequences.
def process(tokens, sourceText, parseParams):

	parseParams.discourseVarChance = 0
	
	sequence = CtrlSeqSet()
	sequence.preprocessTokens(tokens)

	fileio.startConfirmKeys()
	for seq, endPos in sequence.ctrlSeqsFound:
		confirmCtrlSeq(seq, sequence, sourceText, parseParams, endPos)
		sequence.ctrlSeqPos += 1
	fileio.finishConfirmKeys()

class CtrlSeqSet:

	def __init__(self):
		self.ctrlSeqsFound = []
		self.ctrlSeqPos = 0

	def getPreviousCtrlSeq(self):
		if self.ctrlSeqPos <= 0:
			return None
		return self.ctrlSeqsFound[self.ctrlSeqPos-1]
	
	def getNextCtrlSeq(self):
		if self.ctrlSeqPos >= len(self.ctrlSeqsFound) - 1:
			return None
		return self.ctrlSeqsFound[self.ctrlSeqPos+1]

	def preprocessTokens(self, tokens):
		index = 0
		self.ctrlSeqsFound = []
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
				self.ctrlSeqsFound.append([ctrl_contents, token.lexpos])
			index += 1

def confirmCtrlSeq(ctrl_contents, sequence, sourceText, parseParams, ctrlEndPos):

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
			rendered = renderVariant(truncStart, v.txt, truncEnd, maxLineLength, sourceText, parseParams, ctrlStartPos, ctrlEndPos, sequence)
			print rendered
		print "************************************"

		choice = -1
		while choice is not "1" and choice is not "2" and choice is not "3" and choice is not "4":
			sys.stdout.write("\n1) Confirm, 2) Skip, 3) Regen, 4) Stop > ")
			choice = getch.getch()
			if choice == "1":
				print "1\n >>> Confirmed."
				fileio.confirmKey(key)
				return
			elif choice == "2":
				print "2\n >>> Skipping."
				return
			elif choice == "3":
				print "3\n >>> Regenerating."
				confirmCtrlSeq(ctrl_contents, sequence, sourceText, parseParams, ctrlEndPos)
				return
			elif choice == "4":
				print "3\n >>> Halting."
				fileio.finishConfirmKeys()
				sys.exit(0)


def makeKey(sourceText, filename, ctrlStartPos, ctrlEndPos, originalCtrlSeq):
	pre = getRawPre(sourceText, ctrlStartPos, ctrlEndPos)
	post = getRawPost(sourceText, ctrlEndPos)
	key = "%s:%s%s%s" % (filename, pre, originalCtrlSeq, post)
	key = re.sub(r'[\W_]', '', key) # remove non-alphanums
	return key


def renderVariant(truncStart, variant, truncEnd, maxLineLength, sourceText, parseParams, ctrlStartPos, ctrlEndPos, sequence):
	pre = getRenderedPre(sourceText, parseParams, ctrlStartPos, ctrlEndPos, sequence)
	post = getRenderedPost(sourceText, parseParams, ctrlEndPos, sequence)
	rendered = "%s%s%s%s%s" % (truncStart, pre, variant, post, truncEnd)
	rendered = cleanFinal(rendered, parseParams)
	wrapped = wrap(rendered, maxLineLength)
	# Figure out what line the variant starts on.
	prevNL = result.find_previous(wrapped, "\n", len(truncStart + pre))
	numSpaces = len(truncStart + pre) - prevNL
	spaces = " " * numSpaces
	endVariantPos = len(wrapped) - len(post) - len(truncEnd)
	nextNewLinePos = wrapped.find("\n", len(truncStart + pre + variant))
	if numSpaces + len(variant + post + truncEnd) < maxLineLength and post.find("\n") == -1:
		# Single line.
		numSpacesBetween = len(variant) - 2
		spacesBetween = " " * numSpacesBetween
		wrapped = wrapped + spaces + "^" + spacesBetween + "^\n"
	else:
		if prevNL == 0:
			wrapped = spaces + "v\n" + wrapped
		else:
			wrapped = wrapped[:prevNL-1] + "\n" + spaces + "v" + wrapped[prevNL-1:]
		endVariantPos = len(wrapped) - len(post) - len(truncEnd)
		nextNewLinePos = wrapped.find("\n", endVariantPos)
		lastNewLinePos = result.find_previous(wrapped, "\n", endVariantPos)
		numSpaces = endVariantPos - lastNewLinePos - 2
		spaces = " " * numSpaces
		wrapped = wrapped[:nextNewLinePos+1] + spaces + "^\n" + wrapped[nextNewLinePos+1:]	
	return wrapped


def getRawPre(sourceText, ctrlStartPos, ctrlEndPos):
	preBufferLen = 850
	if ctrlStartPos < preBufferLen:
		preBufferLen = ctrlStartPos
	pre = sourceText[ctrlStartPos-preBufferLen:ctrlStartPos]
	pre = cleanContext(pre)
	return pre[-60:]

def getRawPost(sourceText, ctrlEndPos):
	postBufferLen = 850
	if ctrlEndPos + postBufferLen > len(sourceText):
		postBufferLen = len(sourceText) - ctrlEndPos
	post = sourceText[ctrlEndPos+1:ctrlEndPos+postBufferLen]
	post = cleanContext(post)
	return post[:60]

def getRenderedPost(sourceText, parseParams, ctrlEndPos, sequence):
	post = getRawPost(sourceText, ctrlEndPos)
	newCtrlSeqPos = post.find("[")
	if newCtrlSeqPos >= 0:
		newCtrlSeq = sequence.getNextCtrlSeq()
		if newCtrlSeq is not None:
			newVariants = ctrlseq.renderAll(newCtrlSeq[0], parseParams, showAllVars=True)
			variantTxt = chooser.oneOf(newVariants.alts, pure=True).txt
			endSeqPos = post.find("]", newCtrlSeqPos)
			if endSeqPos == -1:
				endSeqPos = len(post)
			post = post[:newCtrlSeqPos] + variantTxt + post[endSeqPos+1:]
	post = cleanContext(post)
	post = macros.expand(post, parseParams, haltOnBadMacros=False)
	# truncate again
	postBufferLen = 60
	post = post[:postBufferLen]
	return post

def getRenderedPre(sourceText, parseParams, ctrlStartPos, ctrlEndPos, sequence):
	pre = getRawPre(sourceText, ctrlStartPos, ctrlEndPos)
	newCtrlSeqPos = pre.rfind("]")
	if newCtrlSeqPos >= 0:
		newCtrlSeq = sequence.getPreviousCtrlSeq()
		if newCtrlSeq is not None:
			newVariants = ctrlseq.renderAll(newCtrlSeq[0], parseParams, showAllVars=True)
			variantTxt = chooser.oneOf(newVariants.alts, pure=True).txt
			startSeqPos = pre.rfind("[")
			if startSeqPos == -1:
				startSeqPos = 0
			pre = pre[:startSeqPos] + variantTxt + pre[newCtrlSeqPos+1:]
	pre = cleanContext(pre)
	pre = macros.expand(pre, parseParams, haltOnBadMacros=False)
	# truncate again
	preBufferLen = 60
	pre = pre[-1*preBufferLen:]
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
	while pos is not -1:
		endDefPos = text.find("]", pos)
		if endDefPos is not -1:
			endBodyPos = text.find("]", endDefPos+1)
			if endBodyPos is not -1:
				text = text[:pos-1] + text[endBodyPos+1:]
		pos = text.find("[MACRO", pos+1)


	# remove DEFINEs.
	pos = text.find("[DEFINE")
	while pos is not -1:
		endDefPos = text.find("]", pos)
		if endDefPos is not -1:
			text = text[:pos-1] + text[endDefPos+1:]
		pos = text.find("[DEFINE", pos+1)

	return text


def cleanFinal(text, parseParams):
	# Remove doubled spaces (which won't be visible post-Latex and are therefore just a distraction). 
	text = re.sub(r"  +", " ", text)

	# Expand macros.
	text = macros.expand(text, parseParams, haltOnBadMacros=False)

	return text


def wrap(text, maxLineLength):
	output = ""
	for line in text.split('\n'):
		output += textwrap.fill(line, maxLineLength) + "\n"
	return output
