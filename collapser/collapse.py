# This handles taking converting a quant document into a single possibility.
# coding=utf-8




import quantlex
import quantparse





# Main entry point.
def go(sourceText):

    # sampleData = '''[MACRO alpha][@zetta>Use {beta} macro.][MACRO beta][@yotta>this is yotta|not yotta][DEFINE ^@zetta][DEFINE @yotta]{alpha}'''
    # sourceText = sampleData

    result = quantlex.lex(sourceText)
    if not result.isValid:
    	caret = (" " * (result.errorColumn-1+2)) + "^"
    	print "Lexer found a problem on line %d column %d: %s\n> %s\n%s" % (result.errorLineNumber, result.errorColumn, result.errorMessage, result.errorLineText, caret)
    	return ""

    params = quantparse.ParseParams(preferenceForAuthorsVersion = 20, useAuthorPreferred = False)
    output = quantparse.parse(result.tokens, params)

    # print output

    return output
