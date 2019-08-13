# Manually confirm each use of variants.

import ctrlseq

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
			
			variants = ctrlseq.renderAll(ctrl_contents, parseParams)

			ctrlEndPos = token.lexpos
			ctrlStartPos = sourceText.rfind("[", 0, ctrlEndPos)
			preBufferLen = 60
			postBufferLen = 60
			if ctrlStartPos < preBufferLen:
				preBufferLen = ctrlStartPos
			if ctrlEndPos + postBufferLen > len(sourceText):
				postBufferLen = len(sourceText) - ctrlEndPos
			pre = sourceText[ctrlStartPos-preBufferLen:ctrlStartPos]
			post = sourceText[ctrlEndPos+1:ctrlEndPos+postBufferLen]
			originalCtrlSeq = sourceText[ctrlStartPos:ctrlEndPos+1]
			key = "%s%s%s" % (pre, originalCtrlSeq, post)
			print "\n\n"
			print "####################################"
			print "VARIANT FOUND AT POS %d: '%s'" % (token.lexpos, originalCtrlSeq)
			print "KEY: '%s'" % key
			for variant in variants.alts:
				print "************************************"
				print '''"%s"''' % variant
				print "...%s%s%s..." % (pre, variant, post)
				print (" " * (preBufferLen+3-1)) + ">" + (" " * (len(str(variant)))) + "<"
			print "************************************"


		index += 1
