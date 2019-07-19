# file:///Users/aaron/projects/stories/subcutanean/Collapser/collapser/origply/doc/ply.html#ply_nn2

import ply.lex as lex

inCtrlSequence = False

__flaggedBad = False
__errorMessage = ""

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
	global inCtrlSequence
	global __flaggedBad
	global __errorMessage
	if inCtrlSequence:
		__flaggedBad = True
		__errorMessage = "Illegal nested control sequence"
		pass
	inCtrlSequence = True
	return t

def t_CTRLEND(t):
	r'\]'
	global inCtrlSequence
	inCtrlSequence = False
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
	lexer.input(text)
	result = LexerResult()
	global __flaggedBad
	global inCtrlSequence
	inCtrlSequence = False
	while True:
		__flaggedBad = False
		tok = lexer.token()
		if __flaggedBad:
			result.isValid = False
			result.errorLineNumber = find_line(text, tok)
			result.errorColumn = find_column(text, tok)
			result.errorLineText = find_line_text(text, tok)
			result.errorMessage = __errorMessage
			break
		if not tok: 
			break      # No more input
		result.tokens.append(tok)
	return result


