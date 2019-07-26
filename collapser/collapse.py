# This handles taking converting a quant document into a single possibility.
# coding=utf-8




import quantlex
import quantparse





# Main entry point.
def go(sourceText):

    sampleData = '''This is text with [some values] inside.'''

    sourceText = sampleData

    print "*** LEXING ***"
    result = quantlex.lex(sourceText)
    if not result.isValid:
    	caret = (" " * (result.errorColumn-1+2)) + "^"
    	print "Lexer found a problem on line %d column %d: %s\n> %s\n%s" % (result.errorLineNumber, result.errorColumn, result.errorMessage, result.errorLineText, caret)
    	return ""

    params = quantparse.ParseParams(preferenceForAuthorsVersion = 0)
    output = quantparse.parse(result.tokens, params)

    print output

    outputText = sourceText
    return outputText
