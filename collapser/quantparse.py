

import ply.yacc as yacc

from quantlex import tokens

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




def parse(text):
    print "** PARSING **"
    parser = yacc.yacc()
    result = parser.parse(text)
    print result
    return output;
