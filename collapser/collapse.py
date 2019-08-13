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

    outputText = specialFixes(outputText)

    return outputText



def specialFixes(text):
    # Ensure verses don't break across pages.
    # {verse/A looking-glass held above this stream...}
    text = re.sub(r"{verse/(.*)}", r"{verse/\g<1> \\nowidow }", text)
    
    # Ensure no widows right before chapter breaks.
    text = re.sub(r"([\n\s]*){chapter/", r" \\nowidow \g<1>{chapter/", text)
    
    # Ensure no orphans right after section breaks.
    text = re.sub(r"{section_break}(\n*)(.*)\n", r"{section_break}\g<1>\g<2> \\noclub \n", text)

    # Use proper latex elipses
    text = re.sub(r"\.\.\. ", r"\ldots\ ", text)


    return text