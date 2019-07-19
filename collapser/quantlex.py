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
t_DIVIDER = r'\|'
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
	__lexState["inCtrlSequence"] = False
	return t

# Error handling rule
def t_error(t):
	print("Illegal character '%s'" % t.value[0])
	t.lexer.skip(1)


# Compute stuff about the current lex position.
def find_column(input, token):
    line_start = input.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1

def find_line(input, token):
	return input[:token.lexpos].count('\n') + 1

def find_line_text(input, token):
	line_start = input.rfind('\n', 0, token.lexpos) + 1
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
	while True:
		__lexState["flaggedBad"] = False
		tok = lexer.token()
		if __lexState["flaggedBad"]:
			result.isValid = False
			result.errorLineNumber = find_line(text, tok)
			result.errorColumn = find_column(text, tok)
			result.errorLineText = find_line_text(text, tok)
			result.errorMessage = __lexState["errorMessage"]
			break
		if not tok: 
			break      # No more input
		result.tokens.append(tok)
	return result


