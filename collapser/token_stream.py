
import result


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


class TokenStream:

	def __init__(self, tokens):
		self.pos = 0
		self.tokens = tokens

	def reset(self):
		self.pos = 0

	def next(self):
		if self.pos >= len(self.tokens):
			return None
		tok = self.tokens[self.pos]
		if tok.type == "TEXT":
			self.pos += 1
			return tok.value
		if tok.type == "CTRLBEGIN":
			ctrl_contents = []
			self.pos += 1
			tok = self.tokens[self.pos]
			while tok.type != "CTRLEND":
				ctrl_contents.append(tok)
				self.pos += 1
				tok = self.tokens[self.pos]
			self.pos += 1
			return ctrl_contents
		badResult = result.Result(result.PARSE_RESULT)
		badResult.flagBad("Unexpected token type found '%s'" % tok.type, "", tok.lexpos)
		raise result.ParseException(badResult)


