
LEX_RESULT = 10
PARSE_RESULT = 11

class Result:
	def __init__(self, resultType):
		self.resultType = resultType
		self.tokens = []
		self.isValid = True
		self.errorLineNumber = -1
		self.errorColumn = -1
		self.errorLineText = ""
		self.errorMessage = ""

	def __str__(self):
		if self.isValid == False:
			return "INVALID: Line %d Col %d %s (%s)" % (self.errorLineNumber, self.errorColumn, self.errorMessage, self.errorLineText)
		else:
			output = ""
			for token in self.tokens:
				output += token + ", "
			return output
