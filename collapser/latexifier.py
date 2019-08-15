
# This handles converting a collapsed text into a properly formated Latex file.

# We're looking for curly-brace things like {chapter|2} and replacing them with the appropriate latex. Also more basic things like *bold*.

import re


# Main entry point.
def go(sourceText):
	output = specialFixes(sourceText)
	output = renderControlSeqs(output)
	return output



template_chapter = ['''

\\clearpage 

\\begin{ChapterStart}
\\vspace*{2\\nbs} 
\\ChapterTitle{\\decoglyph{l8694} ''', ''' \\decoglyph{l11057}} 
\\end{ChapterStart}

''']

template_part = ['''

\\cleartorecto

\\begin{ChapterStart}
\\vspace*{4\\nbs} 
\\ChapterTitle{PART ''', '''} 
\\vspace*{2\\nbs} 
\\ChapterTitle{''', '''} 
\\end{ChapterStart}

\\vspace*{4\\nbs} 
\\begin{adjustwidth}{3em}{3em}
\\begin{parascale}[0.88]
''', '''\\\\
\\par
\\noindent \\textit{''', '''}
\\end{parascale}
\\end{adjustwidth}

\\cleartorecto

''']

template_section_break = '''

\\scenebreak

'''

template_pp = '''

'''

template_i = ['''\\textit{''', '''}''']

template_verse = ['''

\\vspace{1\\nbs}
\\begin{adjustwidth}{3em}{} 
\\textit{''', '''}
\\end{adjustwidth}
\\vspace{1\\nbs}

''']

template_verse_inline = ['''\\begin{adjustwidth}{3em}{} 
\\textit{''', '''}
\\end{adjustwidth}
\\noindent ''']

template_vspace = ['''

\\vspace*{''', '''\\nbs}

'''] 

def renderControlSeqs(sourceText):
	rendered = []
	pos = 0


	formatStartPos = sourceText.find("{", pos)
	while formatStartPos is not -1:
		rendered.append(sourceText[pos:formatStartPos])
		formatEndPos = sourceText.find("}", formatStartPos)
		if formatEndPos is -1:
			raise ValueError("Found { without closing brace.")
		codeSeq = sourceText[formatStartPos:formatEndPos+1]
		contents = codeSeq[1:-1].split('/')
		code = contents[0]
		repl = ""

		if code == "part":
			partNum = contents[1]
			partTitle = contents[2]
			epigraph = contents[3]
			source = contents[4]
			repl = template_part[0] + partNum + template_part[1] + partTitle + template_part[2] + epigraph + template_part[3] + source + template_part[4]
		elif code == "chapter":
			chapNum = contents[1]
			repl = template_chapter[0] + chapNum + template_chapter[1]
		elif code == "section_break":
			repl = template_section_break
		elif code == "verse":
			text = contents[1]
			repl = template_verse[0] + text + template_verse[1]
		elif code == "verse_inline":
			text = contents[1]
			repl = template_verse_inline[0] + text + template_verse_inline[1]
		elif code == "pp":
			repl = template_pp
		elif code == "i":
			text = contents[1]
			repl = template_i[0] + text + template_i[1]
		elif code == "vspace":
			text = contents[1]
			repl = template_vspace[0] + text + template_vspace[1]

		elif code == "test":
			repl = "<<TEST_STANDALONE>>"
		elif code == "test_param":
			repl = "<<TEST_PARAMS>>" + contents[1] + "<<END>>"

		else:
			raise ValueError("Unrecognized command '%s' in control sequence '%s'" % (code, codeSeq)) 

		rendered.append(repl)
		pos = formatEndPos+1
		formatStartPos = sourceText.find("{", pos)

	rendered.append(sourceText[pos:len(sourceText)])

	return ''.join(rendered)	



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


