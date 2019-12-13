
import result


# Abstraction over an array of parsed tokens, which will be text or control sequences.

class TokenStream:

	def __init__(self, tokens, returnCtrlSeqWithWrapping):
		self.reset()
		self.returnCtrlSeqWithWrapping = returnCtrlSeqWithWrapping
		self.tokens = tokens

	def reset(self):
		self.pos = 0
		self.lastLexPos = -1

	def wasText(self):
		if self.pos == 0:
			return False
		return self.tokens[self.pos-1].type == "TEXT"

	def next(self):
		if self.pos >= len(self.tokens):
			return None
		tok = self.tokens[self.pos]
		if tok.type == "TEXT":
			self.pos += 1
			return [tok]
		if tok.type == "CTRLBEGIN":
			ctrl_contents = []
			if self.returnCtrlSeqWithWrapping:
				ctrl_contents.append(tok)
			self.pos += 1
			tok = self.tokens[self.pos]
			while tok.type != "CTRLEND":
				ctrl_contents.append(tok)
				self.pos += 1
				tok = self.tokens[self.pos]
			self.lastLexPos = tok.lexpos
			if self.returnCtrlSeqWithWrapping:
				ctrl_contents.append(tok)
			self.pos += 1
			return ctrl_contents
		badResult = result.Result(result.PARSE_RESULT)
		badResult.flagBad("Unexpected token type found '%s'" % tok.type, "", tok.lexpos)
		raise result.ParseException(badResult)


# Abstraction over an array of parsed tokens when we only care about the control sequences, including the ability to get the ones before and after the current one we're considering.

class SequenceStream:

	def __init__(self, tokens):
		self.reset()
		self.sequences = []
		self.parseCtrlSeqs(tokens)

	def parseCtrlSeqs(self, tokens):
		ts = TokenStream(tokens, returnCtrlSeqWithWrapping = True)
		nextToken = ts.next()
		while nextToken is not None:
			if not ts.wasText():
				nextToken = nextToken[1:len(nextToken)-1]
				self.sequences.append([nextToken, ts.lastLexPos])
			nextToken = ts.next()

	def reset(self):
		self.pos = 0

	def preceding(self):
		if self.pos <= 0:
			return [None, None]
		return self.sequences[self.pos-1]
	
	def next(self):
		if self.pos >= len(self.sequences):
			return [None, None]
		nextSeq = self.sequences[self.pos]
		self.pos += 1
		return nextSeq

	def following(self):
		if self.pos >= len(self.sequences) - 1:
			return [None, None]
		return self.sequences[self.pos+1]


