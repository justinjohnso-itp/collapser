# Manually confirm each use of variants.

import ctrlseq
import result
import re

# We should have a series of text and CTRLBEGIN/END sequences.
def process(tokens, sourceText, parseParams):
	index = 0
	ws = re.compile(r"\s\s+")
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
			
			variants = ctrlseq.renderAll(ctrl_contents, parseParams, showAllVars=True)

			ctrlEndPos = token.lexpos
			ctrlStartPos = sourceText.rfind("[", 0, ctrlEndPos)
			preBufferLen = 60
			postBufferLen = 60
			if ctrlStartPos < preBufferLen:
				preBufferLen = ctrlStartPos
			if ctrlEndPos + postBufferLen > len(sourceText):
				postBufferLen = len(sourceText) - ctrlEndPos
			pre = sourceText[ctrlStartPos-preBufferLen:ctrlStartPos]
			pre = pre.replace("\n", "\\")
			post = sourceText[ctrlEndPos+1:ctrlEndPos+postBufferLen]
			post = post.replace("\n", "\\")
			originalCtrlSeq = sourceText[ctrlStartPos:ctrlEndPos+1]
			key = "%s%s%s" % (pre, originalCtrlSeq, post)
			lineNumber = result.find_line_number(sourceText, ctrlStartPos)
			lineColumn = result.find_column(sourceText, ctrlStartPos)
			print "\n\n"
			print "##################################################"
			print "VARIANT FOUND AT LINE %d COL %d: '%s'" % (lineNumber, lineColumn, originalCtrlSeq)
			# print "KEY: '%s'" % key
			for variant in variants.alts:
				print "************************************"
				print '''"%s"''' % str(variant)[:80]
				rendered = "...%s%s%s..." % (pre, variant, post)
				rendered = ws.sub(" ", rendered)
				print rendered
				print (" " * (preBufferLen+3-1)) + ">" + (" " * (len(str(variant)))) + "<"
			print "************************************"


		index += 1
