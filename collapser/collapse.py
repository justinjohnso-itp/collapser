# This handles taking converting a quant document into a single possibility.
# coding=utf-8




import quantlex
import quantparse
import re
import variables
import macros


# Main entry point.
def go(sourceText, params):

    # sampleData = '''[MACRO alpha][@zetta>Use {beta} macro.][MACRO beta][@yotta>this is yotta|not yotta][DEFINE ^@zetta][DEFINE @yotta]{alpha}'''
    # sourceText = sampleData

    result = quantlex.lex(sourceText)
    if not result.isValid:
    	return result

    tokens = result.package

    # Calculate and pre-set variables for Longest/Shortest case.
    if params.chooseStrategy in ["longest", "shortest"]:
        params.setDefines = quantparse.getDefinesForLongestShortest(tokens, params)

    variables.reset()
    macros.reset()
    preppedTokens = quantparse.handleVariablesAndMacros(tokens, sourceText, params)
    output = quantparse.parse(preppedTokens, sourceText, params)
    if not output.isValid:
        return output

    return output

