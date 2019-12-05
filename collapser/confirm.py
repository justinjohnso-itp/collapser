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


# We should have a series of text and CTRLBEGIN/END sequences.
# This is called from quantparse.parse
def process(fileSetKey, tokens, sourceText, parseParams):
	parseParams.discourseVarChance = 0
	MAX_PER_SESSION = 5
	
	sequenceList = SequenceList(tokens)

	fileio.startConfirmKeys(fileSetKey)
	ctr = 0
	for seq, endPos in sequenceList.sequences:
		# Return -1 to halt, 0 if already confirmed, 1 if successfully confirmed, 2 if skipped. 
		result = confirmCtrlSeq(seq, sequenceList, sourceText, parseParams, endPos)
		sequenceList.pos += 1
		if result == -1:
			break
		if result == 1 or result == 2:
			ctr += 1
		if ctr >= MAX_PER_SESSION:
			break	
	fileio.finishConfirmKeys()


class SequenceList:

	def __init__(self, tokens):
		self.sequences = []
		self.pos = 0
		self.preprocessTokens(tokens)

	def previous(self):
		if self.pos <= 0:
			return None
		return self.sequences[self.pos-1]
	
	def next(self):
		if self.pos >= len(self.sequences) - 1:
			return None
		return self.sequences[self.pos+1]

	def preprocessTokens(self, tokens):
		index = 0
		self.sequences = []
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
				self.sequences.append([ctrl_contents, token.lexpos])
			index += 1

def confirmCtrlSeq(ctrl_contents, sequenceList, sourceText, parseParams, ctrlEndPos):

	# Return -1 to halt, 0 if already confirmed, 1 if successfully confirmed, 2 if skipped, 3 if requesting regeneration.

	maxLineLength = 80
	variants = ctrlseq.renderAll(ctrl_contents, parseParams, showAllVars=True)
	ctrlStartPos = sourceText.rfind("[", 0, ctrlEndPos)
	filename = result.find_filename(sourceText, ctrlStartPos)
	originalCtrlSeq = sourceText[ctrlStartPos:ctrlEndPos+1]
	key = makeKey(sourceText, filename, ctrlStartPos, ctrlEndPos, originalCtrlSeq)
	truncStart = "..."
	truncEnd = "..."
	if fileio.isKeyConfirmed(key) == True:
		return 0

	lineNumber = result.find_line_number_for_file(sourceText, ctrlStartPos)
	lineColumn = result.find_column(sourceText, ctrlStartPos)
	print "\n\n"
	print "#################################################################"
	print "VARIANT FOUND IN %s LINE %d COL %d:\n%s" % (filename, lineNumber, lineColumn, originalCtrlSeq)
	print "#################################################################"
	for v in variants.alts:
		print '''************************************'''
		pre = getRenderedPre(sourceText, parseParams, ctrlStartPos, ctrlEndPos, sequenceList)
		post = getRenderedPost(sourceText, parseParams, ctrlEndPos, sequenceList)
		rendered = renderVariant(truncStart, pre, v.txt, post, truncEnd, maxLineLength, parseParams)
		print rendered
	print "************************************"

	choice = -1
	while choice is not "1" and choice is not "2" and choice is not "3" and choice is not "4" and choice is not "5":
		sys.stdout.write("\n1) Confirm, 2) Skip, 3) Regen, 4) Done Confirming, 5) Quit > ")
		choice = getch.getch()
		if choice == "1":
			print "1\n >>> Confirmed."
			fileio.confirmKey(key)
			return 1
		elif choice == "2":
			print "2\n >>> Skipping."
			return 2
		elif choice == "3":
			print "3\n >>> Regenerating."
			confirmCtrlSeq(ctrl_contents, sequenceList, sourceText, parseParams, ctrlEndPos)
			return 3
		elif choice == "4":
			print "4\n >>> Done Confirming."
			fileio.finishConfirmKeys()
			return -1
		elif choice == "5":
			print "5\n >>> Quit."
			fileio.finishConfirmKeys()
			sys.exit(0)


def makeKey(sourceText, filename, ctrlStartPos, ctrlEndPos, originalCtrlSeq):
	pre = getRawPre(sourceText, ctrlStartPos, ctrlEndPos)
	post = getRawPost(sourceText, ctrlEndPos)
	key = "%s:%s%s%s" % (filename, pre, originalCtrlSeq, post)
	key = re.sub(r'[\W_]', '', key) # remove non-alphanums
	return key


def renderVariant(truncStart, pre, variant, post, truncEnd, maxLineLength,  parseParams):

	# Expand macros.
	variant = macros.expand(variant, parseParams, haltOnBadMacros=False)

	# Don't show very long excerpts in their entirety.
	if len(variant) > maxLineLength * 5:
		startTruncPos = variant.rfind(" ", 0, maxLineLength * 2)
		endTruncPos = variant.find(" ", len(variant) - (maxLineLength * 2), len(variant))
		variant = variant[:startTruncPos] + ".... ... ...." + variant[endTruncPos:]

	# Get the variant in context.
	rendered = "%s%s%s%s%s" % (truncStart, pre, variant, post, truncEnd)
	rendered = cleanFinal(rendered, parseParams)
	wrapped = wrap(rendered, maxLineLength)

	# Draw the carets highlighting the variant's position.
	prevNL = result.find_previous(wrapped, "\n", len(truncStart + pre))
	numSpaces = len(truncStart + pre) - prevNL
	spaces = " " * numSpaces
	if numSpaces + len(variant + post + truncEnd) < maxLineLength and post.find("\n") == -1:
		# Single line.
		numSpacesBetween = len(variant) - 2
		spacesBetween = " " * numSpacesBetween
		wrapped = wrapped + spaces + "^" + spacesBetween + "^\n"
	else:
		# Multi-line.
		# Above
		if prevNL == 0:
			wrapped = spaces + "v\n" + wrapped
		else:
			wrapped = wrapped[:prevNL-1] + "\n" + spaces + "v" + wrapped[prevNL-1:]
		# Below
		endVariantPos = len(wrapped) - len(post) - len(truncEnd)
		nextNewLinePos = wrapped.find("\n", endVariantPos)
		lastNewLinePos = result.find_previous(wrapped, "\n", endVariantPos)
		numSpaces = endVariantPos - lastNewLinePos - 2
		spaces = " " * numSpaces
		wrapped = wrapped[:nextNewLinePos+1] + spaces + "^\n" + wrapped[nextNewLinePos+1:]	
	return wrapped

DEFAULT_BUFFER_LEN = 850
def getRawPre(sourceText, ctrlStartPos, ctrlEndPos, preBufferLen = DEFAULT_BUFFER_LEN):
	if ctrlStartPos < preBufferLen:
		preBufferLen = ctrlStartPos
	pre = sourceText[ctrlStartPos-preBufferLen:ctrlStartPos]
	pre = cleanContext(pre)
	return pre[-60:]

def getRawPost(sourceText, ctrlEndPos, postBufferLen = DEFAULT_BUFFER_LEN):
	if ctrlEndPos + postBufferLen > len(sourceText):
		postBufferLen = len(sourceText) - ctrlEndPos
	post = sourceText[ctrlEndPos+1:ctrlEndPos+postBufferLen]
	post = cleanContext(post)
	return post[:60]

def getRenderedPre(sourceText, parseParams, ctrlStartPos, ctrlEndPos, sequenceList, bufferLen = DEFAULT_BUFFER_LEN):
	pre = getRawPre(sourceText, ctrlStartPos, ctrlEndPos, bufferLen)
	prevCtrlSeqEndPos = pre.rfind("]")
	if prevCtrlSeqEndPos >= 0:
		prevCtrlSeq = sequenceList.previous()
		if prevCtrlSeq is not None:
			prevVariants = ctrlseq.renderAll(prevCtrlSeq[0], parseParams, showAllVars=True)
			variantTxt = chooser.oneOf(prevVariants.alts, pure=True).txt
			prevCtrlSeqStartPos = pre.rfind("[")
			if prevCtrlSeqStartPos == -1:
				prevCtrlSeqStartPos = 0
			pre = pre[:prevCtrlSeqStartPos] + variantTxt + pre[prevCtrlSeqEndPos+1:]
	pre = cleanContext(pre)
	pre = macros.expand(pre, parseParams, haltOnBadMacros=False)
	# truncate again
	preBufferLen = 60
	pre = pre[-1*preBufferLen:]
	return pre

def getRenderedPost(sourceText, parseParams, ctrlEndPos, sequenceList, bufferLen = DEFAULT_BUFFER_LEN):
	post = getRawPost(sourceText, ctrlEndPos, bufferLen)
	nextCtrlSeqStartPos = post.find("[")
	if nextCtrlSeqStartPos >= 0:
		nextCtrlSeq = sequenceList.next()
		if nextCtrlSeq is not None:
			nextVariants = ctrlseq.renderAll(nextCtrlSeq[0], parseParams, showAllVars=True)
			variantTxt = chooser.oneOf(nextVariants.alts, pure=True).txt
			nextCtrlSeqEndPos = post.find("]", nextCtrlSeqStartPos)
			if nextCtrlSeqEndPos == -1:
				nextCtrlSeqEndPos = len(post)
			post = post[:nextCtrlSeqStartPos] + variantTxt + post[nextCtrlSeqEndPos+1:]
	post = cleanContext(post)
	post = macros.expand(post, parseParams, haltOnBadMacros=False)
	# truncate again
	postBufferLen = 60
	post = post[:postBufferLen]
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

	# remove macro definitions.
	pos = text.find("[MACRO")
	while pos is not -1:
		endDefPos = text.find("]", pos)
		if endDefPos == -1:
			# Couldn't find end of MACRO definition
			text = text[:pos]
			break
		endBodyPos = text.find("]", endDefPos+1)
		if endBodyPos == -1:
			# Couldn't find end of MACRO body
			text = text[:pos]
			break
		text = text[:pos-1] + text[endBodyPos+1:]
		pos = text.find("[MACRO")

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
