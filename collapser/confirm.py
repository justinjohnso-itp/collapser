# Manually confirm each use of variants.

import ctrlseq

# We should have a series of text and CTRLBEGIN/END sequences.
def process(tokens, parseParams):
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
			print "variants: %s" % variants

			print "Variant found at pos %d: '%s'" % (token.lexpos, ctrl_contents)
			for variant in variants.alts:
				print "***************************************************"
				# print "...%s%s%s..." % (variant)
			print "***************************************************\n"


		index += 1
