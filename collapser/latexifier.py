
# This handles converting a collapsed text into a properly formated Latex file.

# We're looking for curly-brace things like {chapter|2} and replacing them with the appropriate latex. Also more basic things like *bold*.

import re

template_chapter = ['''

\\clearpage 

\\begin{ChapterStart}
\\vspace*{2\\nbs} 
\\ChapterTitle{\\decoglyph{l8694} ''', ''' \\decoglyph{l11057}} 
\\end{ChapterStart}

''']



# Main entry point.
def go(sourceText):
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
		print contents
		code = contents[0]
		repl = ""
		if code == "epigraph":
			pass
		elif code == "section_break":
			pass
		elif code == "chapter":
			chapNum = contents[1]
			repl = template_chapter[0] + chapNum + template_chapter[1]
			print repl
			pass
		elif code == "part":
			pass
		elif code == "verse":
			pass
		elif code == "verse_inline":
			pass
		elif code == "pp":
			pass

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


