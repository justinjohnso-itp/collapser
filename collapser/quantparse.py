
# Array of chunks. Each chunk is either text or a control sequence. A control sequence might have metadata and also a payload, which is an array of textons that each can have their own metadata. 



from quantlex import tokens


def renderControlSequence(tokens):
	return "(control sequence with %d tokens)" % len(tokens)

# The lexer should have guaranteed that we have a series of TEXT tokens interspersed with sequences of others nested between CTRLBEGIN and CTRLEND with no issues with nesting or incomplete tags. 
def process(tokens):
	output = []
	index = 0
	while index < len(tokens):
		token = tokens[index]
		rendered = ""
		if token.type == "TEXT":
			print "Found TEXT: '%s'" % token.value
			rendered = token.value
		elif token.type == "CTRLBEGIN":
			print "Found CTRLBEGIN: '%s'" % token.value
			ctrl_contents = []
			index += 1
			token = tokens[index]
			while token.type != "CTRLEND":
				print ", %s: %s" % (token.type, token.value)
				ctrl_contents.append(token.value)
				index += 1
				token = tokens[index]
			rendered = renderControlSequence(ctrl_contents)

		output.append(rendered)
		
		index += 1

	return output


def parse(tokens):
    print "** PARSING **"
    renderedChunks = process(tokens)
    finalString = ''.join(renderedChunks)
    return finalString
