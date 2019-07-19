# This handles taking converting a quant document into a single possibility.





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

    output = quantparse.parse(result.tokens)

    print output

    outputText = sourceText
    return outputText
