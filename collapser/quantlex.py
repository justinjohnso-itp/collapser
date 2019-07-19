# file:///Users/aaron/projects/stories/subcutanean/Collapser/collapser/origply/doc/ply.html#ply_nn2

import ply.lex as lex

inCtrlSequence = False

__flaggedBad = False
__errorLineNumber = -1
__errorLineText = ""

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
	global __errorLineNumber
	global __errorLineText
	if inCtrlSequence:
		print("Illegal nested control sequence: '%s'" % t.value)
		__flaggedBad = True
		__errorLineNumber = 10
		__errorLineText = t.value
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







# Build the lexer
lexer = lex.lex()


class LexerResult:

	def __init__(self):
		self.tokens = []
		self.isValid = True
		self.errorLineNumber = -1
		self.errorLineText = ""


def lex(text):
	lexer.input(text)
	result = LexerResult()
	while True:
		__flaggedBad = False
		tok = lexer.token()
		if __flaggedBad:
			result.isValid = False
			result.errorLineNumber = __errorLineNumber
			result.errorLineText = __errorLineText
			break
		if not tok: 
			break      # No more input
		result.tokens.append(tok)
	return result


