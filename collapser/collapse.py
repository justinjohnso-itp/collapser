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
        print result
    	return ""

    output = quantparse.parse(result.package, sourceText, params)
    if not output.isValid:
        print output
        return ""
        
    outputText = output.package

    return outputText


