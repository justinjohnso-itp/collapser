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

	preBufferLen = 60
	postBufferLen = 60

	variants = ctrlseq.renderAll(ctrl_contents, parseParams, showAllVars=True)

	ctrlStartPos = sourceText.rfind("[", 0, ctrlEndPos)
	if ctrlStartPos < preBufferLen:
		preBufferLen = ctrlStartPos
	if ctrlEndPos + postBufferLen > len(sourceText):
		postBufferLen = len(sourceText) - ctrlEndPos
	pre = sourceText[ctrlStartPos-preBufferLen:ctrlStartPos]
	pre = cleanContext(pre)
	post = sourceText[ctrlEndPos+1:ctrlEndPos+postBufferLen]
	post = cleanContext(post)
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
			showVariant(v.txt, pre, post, preBufferLen, postBufferLen)
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

def showVariant(variant, pre, post, preLen, postLen):
	print '''************************************'''
	rendered = "...%s%s%s..." % (pre, variant, post)
	rendered = cleanFinal(rendered)
	print wrap(rendered)
	if len(str(variant)) < maxLineLength:
		print (" " * (preLen+3-1)) + ">" + (" " * (len(str(variant)))) + "<"


def cleanContext(text):
	# Strip comments.
	text = re.sub(r"\#.*\n", "\n", text)

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
