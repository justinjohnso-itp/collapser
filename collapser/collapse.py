# This handles taking converting a quant document into a single possibility.





import quantlex
import quantparse





# Main entry point.
def go(sourceText):

    sampleData = '''
    This is a bunch of text with [some values] inside.

    Shazam.'''

    sourceText = sampleData

    result = quantlex.lex(sourceText)
    if not result.isValid:
    	print "Lexer found invalid file: %s, %s" % (result.errorLineNumber, result.errorLineText)
    	return ""

    output = quantparse.parse(sourceText)

    print output

    outputText = sourceText
    return outputText
