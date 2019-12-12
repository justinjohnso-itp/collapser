
import result


# Abstraction over an array of parsed tokens, which will be text or control sequences.

class TokenStream:

	# TODO When I'm less tired, I think we can probably refactor out the returnRawTokens complication.
	def __init__(self, tokens, returnRawTokens = False):
		self.reset()
		self.returnRawTokens = returnRawTokens
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
			return [tok] if self.returnRawTokens else tok.value
		if tok.type == "CTRLBEGIN":
			ctrl_contents = []
			if self.returnRawTokens:
				ctrl_contents.append(tok)
			self.pos += 1
			tok = self.tokens[self.pos]
			while tok.type != "CTRLEND":
				ctrl_contents.append(tok)
				self.pos += 1
				tok = self.tokens[self.pos]
			self.lastLexPos = tok.lexpos
			if self.returnRawTokens:
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
		ts = TokenStream(tokens)
		nextToken = ts.next()
		while nextToken is not None:
			if not ts.wasText():
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


