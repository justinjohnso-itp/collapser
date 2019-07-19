# file:///Users/aaron/projects/stories/subcutanean/Collapser/collapser/origply/doc/ply.html#ply_nn2

import ply.lex as lex

inCtrlSequence = False

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
	if inCtrlSequence:
		print("Illegal nested control sequence: '%s'" % t.value)
		# t.lexer.skip(1)
		return False
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


def lex(text):
    print "** LEXING **"
    print text
    lexer.input(text)
    for tok in lexer:
        print "type:%s, value:%s, lineno:%s, lexpos:%s" % (tok.type, tok.value, tok.lineno, tok.lexpos)

