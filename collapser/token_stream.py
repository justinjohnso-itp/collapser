


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