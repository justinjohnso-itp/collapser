


import ply.lex as lex

# List of token names.   This is always required
tokens = (
   'CTRLBEGIN',
   'CTRLEND',
   'MACROBEGIN',
   'MACROEND',
   'DIVIDER',
   'TEXT'
)

# Regular expression rules for simple tokens
t_CTRLBEGIN    = r'\['
t_CTRLEND   = r'\]'
t_MACROBEGIN   = r'\{'
t_MACROEND  = r'\}'
t_DIVIDER = r'\|'


# A regular expression rule 
def t_TEXT(t):
    r'[A-Za-z0-9 \',\.\!]+'
    return t

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()


def run():
    # Test it out
    data = '''
    This is a bunch of text with [some values|with alternatives] inside.
    '''

    # Give the lexer some input
    lexer.input(data)

    # Tokenize
    for tok in lexer:
        print "%s   -- type:%s, value:%s, lineno:%s, lexpos:%s" % (tok, tok.type, tok.value, tok.lineno, tok.lexpos)