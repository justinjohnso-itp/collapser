
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

	def flagBad(self, msg, text, startPos):
		self.isValid = False
		self.errorMessage = msg
		self.errorLineNumber = find_line_number(text, startPos)
		self.errorColumn = find_column(text, startPos)
		self.errorLineText = find_line_text(text, startPos)

	def showError(self):
		# Only show one line's worth of line
		if self.errorColumn > 80:
			self.errorLineText = self.errorLineText[-80:]
			self.errorColumn = self.errorColumn - (len(self.errorLineText) - len(self.errorLineText))

		caret = (" " * (self.errorColumn-1+2)) + "^"
		typeName = self.getPrintedTypeName().capitalize()
		return "%s found a problem on line %d column %d: %s\n> %s\n%s" % (typeName, self.errorLineNumber, self.errorColumn, self.errorMessage, self.errorLineText, caret)

	def getPrintedTypeName(self):
		if self.resultType == LEX_RESULT:
			return "lexer"
		elif self.resultType == PARSE_RESULT:
			return "parser"
		return "unknown result"

	def __str__(self):
		if self.isValid == False:
			return self.showError()
		else:
			output = ""
			for item in self.package:
				output += item + ", "
			return output


# Compute stuff about the current position.
def find_column(input, pos):
    line_start = input.rfind('\n', 0, pos) + 1
    return (pos - line_start) + 1

def find_line_number(input, pos):
	return input[:pos].count('\n') + 1

def find_previous(input, txt, pos):
	return input.rfind(txt, 0, pos) + 1

def find_line_text(input, pos):
	line_start = find_previous(input, '\n', pos)
	line_end = input.find('\n', line_start)
	return input[line_start:line_end]

