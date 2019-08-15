# Manually confirm each use of variants.

import ctrlseq
import result
import re
import getch
import sys

import fileio

# We should have a series of text and CTRLBEGIN/END sequences.
def process(tokens, sourceText, parseParams):
	index = 0
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


def confirmCtrlSeq(ctrl_contents, sourceText, parseParams, ctrlEndPos):

	ws = re.compile(r"  +")
	preBufferLen = 60
	postBufferLen = 60
	maxCaretLen = 80

	variants = ctrlseq.renderAll(ctrl_contents, parseParams, showAllVars=True)

	ctrlStartPos = sourceText.rfind("[", 0, ctrlEndPos)
	if ctrlStartPos < preBufferLen:
		preBufferLen = ctrlStartPos
	if ctrlEndPos + postBufferLen > len(sourceText):
		postBufferLen = len(sourceText) - ctrlEndPos
	pre = sourceText[ctrlStartPos-preBufferLen:ctrlStartPos]
	pre = pre.replace("\n", "\\")
	post = sourceText[ctrlEndPos+1:ctrlEndPos+postBufferLen]
	post = post.replace("\n", "\\")
	originalCtrlSeq = sourceText[ctrlStartPos:ctrlEndPos+1]
	filename = result.find_filename(sourceText, ctrlStartPos)
	key = "%s:%s%s%s" % (filename, pre, originalCtrlSeq, post)
	if fileio.isKeyConfirmed(key) == False:
		lineNumber = result.find_line_number_for_file(sourceText, ctrlStartPos)
		lineColumn = result.find_column(sourceText, ctrlStartPos)
		print "\n\n"
		print "##################################################"
		print "VARIANT FOUND IN %s LINE %d COL %d: '%s'" % (filename, lineNumber, lineColumn, originalCtrlSeq)
		# print "KEY: '%s'" % key
		for v in variants.alts:
			variant = v.txt
			print '''************************************'''
			# print '''> "%s"\n''' % str(variant)[:80]
			rendered = "...%s%s%s..." % (pre, variant, post)
			rendered = ws.sub(" ", rendered)
			print rendered
			if len(str(variant)) < maxCaretLen:
				print (" " * (preBufferLen+3-1)) + ">" + (" " * (len(str(variant)))) + "<"
		print "************************************"

		sys.stdout.write("1) Confirm, 2) Skip, 3) Stop > ")
		choice = getch.getch()
		print choice + "\n"
		if choice == "1":
			print " >>> Confirmed."
			fileio.confirmKey(key)
		elif choice == "2":
			print " >>> Skipping."
		elif choice == "3":
			print " >>> Halting."
			sys.exit(0)


