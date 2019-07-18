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


def lex(text):
    print "** LEXING **"
    print text
    lexer.input(text)
    for tok in lexer:
        print "type:%s, value:%s, lineno:%s, lexpos:%s" % (tok.type, tok.value, tok.lineno, tok.lexpos)

