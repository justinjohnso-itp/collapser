
LEX_RESULT = 10
PARSE_RESULT = 11

class Result:
	def __init__(self, resultType):
		self.resultType = resultType
		self.package = []
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
			for item in self.package:
				output += item + ", "
			return output
