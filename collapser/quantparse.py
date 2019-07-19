
# Array of chunks. Each chunk is either text or a control sequence. A control sequence might have metadata and also a payload, which is an array of textons that each can have their own metadata. 



from quantlex import tokens


# We have a series of tokens for a control sequence, everything between (and excluding) the square brackets. Each token has .type and .value.
def renderControlSequence(tokens):
	# return "(control sequence with %d tokens)" % len(tokens)

	if len(tokens) == 0:
		return ""
	if len(tokens) == 1 and tokens[0].type == "TEXT":
		return tokens[0].value

	return "(couldn't render %s:'%s')" % (tokens[0].type, tokens[0].value)



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
				ctrl_contents.append(token)
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
