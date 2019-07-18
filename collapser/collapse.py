# This handles taking converting a quant document into a single possibility.





import quantlex
import quantparse





# Main entry point.
def go(sourceText):

    sampleData = '''
    This is a bunch of text with [some values] inside.

    Shazam.'''

    sourceText = sampleData

    quantlex.lex(sourceText)
    output = quantparse.parse(sourceText)

    print output

    outputText = sourceText
    return outputText
