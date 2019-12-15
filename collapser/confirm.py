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
import token_stream

import fileio


# We should have a series of text and CTRLBEGIN/END sequences.
# This is called from quantparse.parse
def process(fileSetKey, onlyShow, tokens, sourceText, parseParams):
	global SESSION_CTR
	parseParams.discourseVarChance = 0
	abortFlag = False
	SESSION_CTR = 0
	
	fileio.startConfirmKeys(fileSetKey)

	# If we're just rendering an excerpt, keep all the current confirm keys.
	if len(onlyShow) > 0:
		fileio.reconfirmAll()

	sequenceList = token_stream.SequenceStream(tokens)
	nxt = sequenceList.next()
	while nxt is not None:
		nextCtrlSeq = nxt[0]
		endPos = nxt[1]
		# Return 1 if newly confirmed, 0 otherwise; or -1 to abort further execution.
		result = confirmCtrlSeq(nextCtrlSeq, sequenceList, sourceText, parseParams, endPos)
		if result == 1:
			SESSION_CTR += 1
		if result == -1:
			abortFlag = True
		nxt = sequenceList.next()
	fileio.finishConfirmKeys()
	if abortFlag:
		sys.exit()



MAX_PER_SESSION = 5
SESSION_CTR = 0

def confirmCtrlSeq(ctrl_contents, sequenceList, sourceText, parseParams, ctrlEndPos):
	global MAX_PER_SESSION
	global SESSION_CTR

	# Return 1 if newly confirmed, 0 otherwise; or -1 to abort further execution.

	ctrlStartPos = sourceText.rfind("[", 0, ctrlEndPos)
	filename = result.find_filename(sourceText, ctrlStartPos)
	originalCtrlSeq = sourceText[ctrlStartPos:ctrlEndPos+1]
	key = makeKey(sourceText, filename, ctrlStartPos, ctrlEndPos, originalCtrlSeq)
	if fileio.isKeyConfirmed(key) == True:
		fileio.confirmKey(key)
		return 0

	if SESSION_CTR > MAX_PER_SESSION:
		return 2

	lineNumber = result.find_line_number_for_file(sourceText, ctrlStartPos)
	lineColumn = result.find_column(sourceText, ctrlStartPos)
	print "\n\n"
	print "#################################################################"
	print "VARIANT FOUND IN %s LINE %d COL %d:\n%s" % (filename, lineNumber, lineColumn, originalCtrlSeq)
	print "#################################################################"
	variants = ctrlseq.renderAll(ctrl_contents, parseParams, showAllVars=True)
	for v in variants.alts:
		print '''************************************'''
		print getContextualizedRenderedVariant(sourceText, parseParams, ctrlStartPos, ctrlEndPos, sequenceList, v)
	print "************************************"
	return askUserAboutVariant(key, ctrl_contents, sequenceList, sourceText, parseParams, ctrlEndPos)


def makeKey(sourceText, filename, ctrlStartPos, ctrlEndPos, originalCtrlSeq):
	KEY_PADDING_LEN = 60
	pre = getCharsBefore(sourceText, ctrlStartPos, KEY_PADDING_LEN)
	post = getCharsAfter(sourceText, ctrlEndPos, KEY_PADDING_LEN)
	key = "%s:%s%s%s" % (filename, pre, originalCtrlSeq, post)
	key = re.sub(r'[\W_]', '', key) # remove non-alphanums
	return key

DEFAULT_BUFFER_LEN = 850
def getContextualizedRenderedVariant(sourceText, parseParams, ctrlStartPos, ctrlEndPos, sequenceList, variant, bufferLen = DEFAULT_BUFFER_LEN, truncStart = "...", truncEnd = "...", maxLineLength = 80):
	vTxt = variant.txt
	fromVar = variant.fromVariable
	oldSetDefines = parseParams.setDefines
	parseParams.setDefines = [fromVar]
	pre = getRenderedPre(sourceText, parseParams, ctrlStartPos, sequenceList.preceding(), bufferLen)
	post = getRenderedPost(sourceText, parseParams, ctrlEndPos, sequenceList.following(), bufferLen)
	rendered = renderVariant(truncStart, pre, vTxt, post, truncEnd, maxLineLength, parseParams)
	parseParams.setDefines = oldSetDefines
	return rendered


def renderVariant(truncStart, pre, variant, post, truncEnd, maxLineLength,  parseParams):

	# Expand macros.
	variant = macros.expand(variant, parseParams, isPartialText = True)

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

def getCharsBefore(text, pos, count):
	if pos < count:
		count = pos
	return text[pos-count:pos]

def getCharsAfter(text, pos, count):
	if pos + count > len(text):
		count = len(text) - pos
	return text[pos+1:pos+count]

def renderNearbyBit(ctrlSequence, snippet, parseParams, ctrlSeqStartPos, ctrlSeqEndPos):
	if ctrlSequence is None:
		return snippet
	variants = ctrlseq.renderAll(ctrlSequence[0], parseParams, showAllVars=True)
	variantTxt = variants.getByFromVariable(parseParams.setDefines)
	return snippet[:ctrlSeqStartPos] + variantTxt + snippet[ctrlSeqEndPos+1:]

def cleanAndExpandBit(snippet, parseParams, isBefore):
	snippet = cleanContext(snippet)
	snippet = macros.expand(snippet, parseParams, isPartialText = True)	
	bufferLen = 60
	return snippet[-1*bufferLen:] if isBefore else snippet[:bufferLen]

def getRenderedPre(sourceText, parseParams, ctrlStartPos, prevCtrlSeq, bufferLen = DEFAULT_BUFFER_LEN):
	pre = getCharsBefore(sourceText, ctrlStartPos, bufferLen)
	prevEndPos = pre.rfind("]")
	if prevEndPos >= 0:
		prevStartPos = pre.rfind("[")
		if prevStartPos == -1:
			prevStartPos = 0
		pre = renderNearbyBit(prevCtrlSeq, pre, parseParams, prevStartPos, prevEndPos)
	return cleanAndExpandBit(pre, parseParams, True)

def getRenderedPost(sourceText, parseParams, ctrlEndPos, nextCtrlSeq, bufferLen = DEFAULT_BUFFER_LEN):
	post = getCharsAfter(sourceText, ctrlEndPos, bufferLen)
	nextStartPos = post.find("[")
	if nextStartPos >= 0:
		nextEndPos = post.find("]", nextStartPos)
		if nextEndPos == -1:
			nextEndPos = len(post)
		post = renderNearbyBit(nextCtrlSeq, post, parseParams, nextStartPos, nextEndPos)
	return cleanAndExpandBit(post, parseParams, False)

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
			newText = ""
			if pos > 0:
				newText += text[:pos-1]
			newText += text[endDefPos+1:]
			text = newText
		pos = text.find("[DEFINE", pos+1)

	return text


def cleanFinal(text, parseParams):
	# Remove doubled spaces (which won't be visible post-Latex and are therefore just a distraction). 
	text = re.sub(r"  +", " ", text)

	# Expand macros.
	text = macros.expand(text, parseParams, isPartialText = True)

	return text


def wrap(text, maxLineLength):
	output = ""
	for line in text.split('\n'):
		output += textwrap.fill(line, maxLineLength) + "\n"
	return output


def askUserAboutVariant(key, ctrl_contents, sequenceList, sourceText, parseParams, ctrlEndPos):
	global MAX_PER_SESSION
	global SESSION_CTR
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
			return 0
		elif choice == "3":
			print "3\n >>> Regenerating."
			res = confirmCtrlSeq(ctrl_contents, sequenceList, sourceText, parseParams, ctrlEndPos)
			return res
		elif choice == "4":
			print "4\n >>> Done Confirming."
			SESSION_CTR = MAX_PER_SESSION + 1
			return 0
		elif choice == "5":
			print "5\n >>> Quit."
			SESSION_CTR = MAX_PER_SESSION + 1
			return -1

