# This handles taking converting a quant document into a single possibility.
# coding=utf-8




import quantlex
import quantparse
import re


# Main entry point.
def go(sourceText, params):

    # sampleData = '''[MACRO alpha][@zetta>Use {beta} macro.][MACRO beta][@yotta>this is yotta|not yotta][DEFINE ^@zetta][DEFINE @yotta]{alpha}'''
    # sourceText = sampleData

    result = quantlex.lex(sourceText)
    if not result.isValid:
    	caret = (" " * (result.errorColumn-1+2)) + "^"
    	print "Lexer found a problem on line %d column %d: %s\n> %s\n%s" % (result.errorLineNumber, result.errorColumn, result.errorMessage, result.errorLineText, caret)
    	return ""

    output = quantparse.parse(result.tokens, params)

    output = specialFixes(output)

    return output



def specialFixes(text):
    # Ensure verses don't break across pages.
    # {verse/A looking-glass held above this stream...}
    text = re.sub(r"{verse/(.*)}", r"{verse/\g<1> \\nowidow }", text)
    
    text = re.sub(r"([\n\s]*){chapter/", r" \\nowidow \g<1>{chapter/", text)
    
    return text