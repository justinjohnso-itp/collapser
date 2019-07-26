# file:///Users/aaron/projects/stories/subcutanean/Collapser/collapser/origply/doc/ply.html#ply_nn2

import ply.lex as lex

__lexState = { "inCtrlSequence": False, "flaggedBad": False, "errorMessage": "" }

def resetLexState():
	__lexState["inCtrlSequence"] = False
	__lexState["flaggedBad"] = False
	__lexState["errorMessage"] = ""

# List of token names.   This is always required
tokens = (
   'CTRLBEGIN',
   'CTRLEND',
   'MACROBEGIN',
   'MACROEND',
   'DIVIDER',
   'AUTHOR',
   'ALWAYS',
   'TEXT',
   'NUMBER',
   'COMMENT',
   'DEFINE',
   'VARIABLE',
   'ERROR_LONE_GT',
   'ERROR_LONE_VAR'
)

# Regular expression rules for simple tokens
t_MACROBEGIN   = r'\{'
t_MACROEND  = r'\}'
t_AUTHOR = r'\^'
t_ALWAYS = r'\~'

def t_VARIABLE(t):
	r'@[A-Za-z_\-][A-Za-z_\-0-9]*'
	t.value = t.value[1:]
	return t

def t_ERROR_LONE_VAR(t):
	r'@'
	__lexState["flaggedBad"] = True
	__lexState["errorMessage"] = "Variable op @ appeared but what came after was not recognized as a variable"
	pass

def t_NUMBER(t):
	r'[0-9]{1,2}\>'
	t.value = int(t.value[:-1])
	return t

def t_BAD_NUMBER(t):
	r'100'
	__lexState["flaggedBad"] = True
	__lexState["errorMessage"] = "Don't use NUMBER 100, just do the thing."
	pass

def t_ERROR_LONE_GT(t):
	r'\>'
	__lexState["flaggedBad"] = True
	__lexState["errorMessage"] = "Number op > appeared in unexpected spot"
	pass

def t_DEFINE(t):
	r'DEFINE\s*'
	global __lexState
	__lexState["inDefine"] = True
	return t

def t_TEXT(t):
	r'[^\[\]\{\}\|\>\@\^\#\~]+'
	return t

def t_COMMENT(t):
	r'\#.*\n?'
	pass # No return value. Token discarded

def t_CTRLBEGIN(t):
	r'\['
	global __lexState
	if __lexState["inCtrlSequence"]:
		__lexState["flaggedBad"] = True
		__lexState["errorMessage"] = "Illegal nested control sequence"
		pass
	__lexState["inCtrlSequence"] = True
	return t

def t_CTRLEND(t):
	r'\]'
	global __lexState
	if not __lexState["inCtrlSequence"]:
		__lexState["flaggedBad"] = True
		__lexState["errorMessage"] = "Unmatched closing control sequence character"
		pass
	__lexState["inCtrlSequence"] = False
	__lexState["inDefine"] = False
	return t

def t_DIVIDER(t):
	r'\|'
	global __lexState
	if not __lexState["inCtrlSequence"]:
		__lexState["flaggedBad"] = True
		__lexState["errorMessage"] = "Divider symbol found outside [ ]"
		pass
	return t


# Error handling rule
def t_error(t):
	print("Illegal character '%s'" % t.value[0])
	t.lexer.skip(1)


# Compute stuff about the current lex position.
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

# Build the lexer
lexer = lex.lex()


class LexerResult:

	def __init__(self):
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

def lex(text):
	resetLexState()
	lexer.input(text)
	result = LexerResult()
	prevTok = -1
	while True:
		__lexState["flaggedBad"] = False
		tok = lexer.token()
		if __lexState["flaggedBad"]:
			result.isValid = False
			result.errorLineNumber = find_line_number(text, tok.lexpos)
			result.errorColumn = find_column(text, tok.lexpos)
			result.errorLineText = find_line_text(text, tok.lexpos)
			result.errorMessage = __lexState["errorMessage"]
			break
		if not tok: 
			if __lexState["inCtrlSequence"]:
				posOfCtrlStart = find_previous(text, '[', len(text)-1) - 1
				result.isValid = False
				result.errorLineNumber = find_line_number(text, posOfCtrlStart)
				result.errorColumn = find_column(text, posOfCtrlStart)
				result.errorLineText = find_line_text(text, posOfCtrlStart)
				result.errorMessage = "No ending control sequence character"
			break      # No more input
		if prevTok is not -1:
			onlyAllowedAtStart = ["AUTHOR", "ALWAYS"]
			apAfterText = tok.type in onlyAllowedAtStart and prevTok.type == "TEXT"
			apBeforeInvalid = tok.type != "TEXT" and tok.type != "DIVIDER" and tok.type != "VARIABLE" and prevTok.type in onlyAllowedAtStart
			if apAfterText or apBeforeInvalid:
				result.isValid = False
				result.errorLineNumber = find_line_number(text, tok.lexpos)
				result.errorColumn = find_column(text, tok.lexpos)
				result.errorLineText = find_line_text(text, tok.lexpos)
				result.errorMessage = "%s can only come at the start of a text" % tok.type
				break
		if tok.type == "DEFINE" and ( prevTok is -1 or prevTok.type != "CTRLBEGIN" ):
			result.isValid = False
			result.errorLineNumber = find_line_number(text, tok.lexpos)
			result.errorColumn = find_column(text, tok.lexpos)
			result.errorLineText = find_line_text(text, tok.lexpos)
			result.errorMessage = "DEFINE can only appear at the start of a control sequence."
			break;
		if tok.type == "VARIABLE" and ( prevTok is -1 or prevTok.type not in ["DEFINE", "AUTHOR", "NUMBER"] ):
			result.isValid = False
			result.errorLineNumber = find_line_number(text, tok.lexpos)
			result.errorColumn = find_column(text, tok.lexpos)
			result.errorLineText = find_line_text(text, tok.lexpos)
			result.errorMessage = "Found a @variable but these can only come immediately after a DEFINE."
			break;
		if prevTok is not -1:
			if prevTok.type == "DEFINE" and tok.type not in ["VARIABLE", "AUTHOR", "NUMBER"]:
				result.isValid = False
				result.errorLineNumber = find_line_number(text, prevTok.lexpos)
				result.errorColumn = find_column(text, prevTok.lexpos)
				result.errorLineText = find_line_text(text, prevTok.lexpos)
				result.errorMessage = "DEFINE must be followed by a variable name, as in [DEFINE @var]."
				break;
		if prevTok is not -1:
			if tok.type == "DIVIDER" and prevTok.type == "NUMBER" and __lexState["inDefine"]:
				result.isValid = False
				result.errorLineNumber = find_line_number(text, tok.lexpos)
				result.errorColumn = find_column(text, tok.lexpos)
				result.errorLineText = find_line_text(text, tok.lexpos)
				result.errorMessage = "A divider can't immediately follow a number within a define."
				break;



		result.tokens.append(tok)
		prevTok = tok
	return result


