
# file:///Users/aaron/projects/stories/subcutanean/Collapser/collapser/origply/doc/ply.html#ply_nn2

import ply.lex as lex

# List of token names.   This is always required
tokens = (
   'CTRLBEGIN',
   'CTRLEND',
   'MACROBEGIN',
   'MACROEND',
   'DIVIDER',
   'TEXT',
   'COMMENT'
)

# Regular expression rules for simple tokens
t_CTRLBEGIN    = r'\['
t_CTRLEND   = r'\]'
t_MACROBEGIN   = r'\{'
t_MACROEND  = r'\}'
t_DIVIDER = r'\|'


# A regular expression rule 
def t_TEXT(t):
    r'[A-Za-z0-9\n\s\',\.\!]+'
    return t

def t_COMMENT(t):
    r'\#.*'
    pass
    # No return value. Token discarded

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()





import ply.yacc as yacc

output = ""

def p_story(p):
	'''story :
		| story unit'''
	pass

def p_unit(p):
	'''unit : normal_text
		| control_sequence'''
	pass

def p_control_sequence(p):
	'control_sequence : CTRLBEGIN TEXT CTRLEND'
	print "Found control sequence"
	global output
	output += "(%s)" % p[2]

def p_normal_text(p):
	'normal_text : TEXT'
	print "Found normal text"
	global output
	output += p[1]

# Error rule for syntax errors
def p_error(p):
	if p:
	    print "Syntax error in input! %s" % p
	else:
		print "End of File!"

# Build the parser
parser = yacc.yacc()




def run():
    # Test it out
    data = '''
    This is a bunch of text with [some values] inside.

    Shazam.'''

    print """
    Data: "%s"
    """ % data

    # Give the lexer some input
    print "** LEXING **"
    lexer.input(data)

    # Tokenize
    for tok in lexer:
        print "type:%s, value:%s, lineno:%s, lexpos:%s" % (tok.type, tok.value, tok.lineno, tok.lexpos)

    print "** PARSING **"
    result = parser.parse(data)
    print result

    print "Output: '%s'" % output
