# This handles taking converting a quant document into a single possibility.
# coding=utf-8




import quantlex
import quantparse
import re
import variables
import macros
import chooser


# Main entry point.
def go(fullText, selectedText, params, returnTokensOnly = False):

    result = quantlex.lex(fullText)
    if not result.isValid:
    	return result
    tokens = result.package

    # Calculate and pre-set variables for Longest/Shortest case.
    if params.chooseStrategy in ["longest", "shortest"]:
        params.setDefines = getDefinesForLongestShortest(tokens, params)

    variables.reset()
    macros.reset()        
    variables.handleDefs(tokens, params)
    macros.handleDefs(tokens, params)

    # Now do only the text we want to render.
    result = quantlex.lex(selectedText)
    if not result.isValid:
        return result
    tokens = result.package
    preppedTokens = variables.stripDefs(tokens, params)
    preppedTokens = macros.stripMacros(preppedTokens, params)
    if returnTokensOnly:
        return preppedTokens

    output = quantparse.parse(preppedTokens, selectedText, params)
    if not output.isValid:
        return output

    return output


def getDefinesForLongestShortest(tokens, parseParams):
    print "Calculating %s defines (ignoring seed)..." % parseParams.chooseStrategy
    bestDefines = []

    # Process all the DEFINEs in the code, with a copy of everything.
    variables.reset()
    macros.reset()
    tempTokens = list(tokens)
    tempTokens = variables.handleDefs(tempTokens, parseParams)
    tempTokens = macros.handleDefs(tempTokens, parseParams)
    parseParamsCopy = parseParams.copy()
    chooser.setSeed(chooser.number(100000))

    # Now for each option in a define group, see which one is best.
    groups = variables.__v.varGroups.keys()
    for groupname in groups:
        optsToTry = list(variables.__v.varGroups[groupname])

        # If just one option, we want to try it as True and False.
        if len(optsToTry) is 1:
            optsToTry.append("^" + optsToTry[0])

        bestPos = -1
        bestLen = -1
        secondBestLen = -1
        isShortest = parseParams.chooseStrategy == "shortest"
        if isShortest:
            secondBestLen = 999999999
            bestLen = 999999999
        for pos, key in enumerate(optsToTry):
            variables.setAllTo(False)

            if key[0] != "^":
                variables.__v.variables[key] = True

            thisLen = len(quantparse.handleParsing(tempTokens, parseParamsCopy))

            isBetter = False
            if isShortest:
                isBetter = thisLen < bestLen
            else:
                isBetter = thisLen > bestLen
            if isBetter:
                bestPos = pos
                secondBestLen = bestLen
                bestLen = thisLen
            elif (isShortest and thisLen < secondBestLen) or (not isShortest and thisLen > secondBestLen):
                secondBestLen = thisLen

        print "Best was %s (%d chars %s than next best)" % (optsToTry[bestPos], abs(bestLen - secondBestLen), "longer" if parseParams.chooseStrategy == "longest" else "shorter")
        bestDefines.append(optsToTry[bestPos])

    return bestDefines
