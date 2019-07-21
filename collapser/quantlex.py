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
   'COMMENT'
)

# Regular expression rules for simple tokens
t_MACROBEGIN   = r'\{'
t_MACROEND  = r'\}'
t_AUTHOR = r'\^'
t_ALWAYS = r'\~'

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
			apBeforeInvalid = tok.type != "TEXT" and tok.type != "DIVIDER" and prevTok.type in onlyAllowedAtStart
			if apAfterText or apBeforeInvalid:
				result.isValid = False
				result.errorLineNumber = find_line_number(text, tok.lexpos)
				result.errorColumn = find_column(text, tok.lexpos)
				result.errorLineText = find_line_text(text, tok.lexpos)
				result.errorMessage = "%s can only come at the start of a text" % tok.type
				break

		result.tokens.append(tok)
		prevTok = tok
	return result


