# coding=utf-8

# This handles converting a collapsed text into a properly formated Latex file.

# We're looking for curly-brace things like {chapter|2} and replacing them with the appropriate latex. 

import re
import result

# Main entry point.
def go(sourceText, templates, seed, doFront):
	workFile = specialFixes(sourceText)
	workFile = renderControlSeqs(workFile)
	postConversionSanityCheck(workFile)
	output = latexWrapper(workFile, templates, seed, doFront)	
	return output


# Handle any tweaks to the rendered text before we begin the latex conversion.
def specialFixes(text):
	# Strip file identifiers (used by the lexer and parser to know what source file a given line comes from, so useful error messages can be printed).
	text = re.sub(r"\% file (.*)\n", "", text)

	# Ensure verses don't break across pages.
	# {verse/A looking-glass held above this stream...}
	text = re.sub(r"{verse/(.*)}", r"{verse/\g<1> \\nowidow }", text)

	# Ensure no widows right before chapter breaks.
	text = re.sub(r"([\n\s]*){chapter/", r" \\nowidow \g<1>{chapter/", text)

	# Ensure no orphans right after section breaks.
	text = re.sub(r"{section_break}(\n*)(.*)\n", r"{section_break}\g<1>\g<2> \\noclub \n", text)

	# Use proper latex elipses
	text = re.sub(r"\.\.\. ", r"\ldots\ ", text)
	text = re.sub(r"… ", r"\ldots\ ", text)

	return text


# Render all control sequences in appropriate latex
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
			# Hack to get "\mainmatter" to appear in right spot for opening chapter (otherwise page 1 is on the blank page preceeding and inner/outer positioning is wrong.)
			optMainMatter = ""
			if partNum == "PART ONE":
				optMainMatter = "\\mainmatter"
			repl = template_part[0] + optMainMatter + template_part[1] + partNum + template_part[2] + partTitle + template_part[3] + epigraph + template_part[4] + source + template_part[5]
		elif code == "epigraph":
			epigraph = contents[1]
			source = contents[2]
			repl = template_epigraph[0] + epigraph + template_epigraph[1] + source + template_epigraph[2]
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


# Raise errors if anything unexpected is found in the converted output.
def postConversionSanityCheck(text):
	# Look for unexpected characters etc. here
	# Note: can't use find_line_number_for_file etc. b/c those markers have been stripped.
	pos = text.find('_')
	if pos is not -1:
		raise ValueError("Found invalid underscore '_' character on line %d:\n%s" % (result.find_line_number(text, pos), result.find_line_text(text, pos)) )
	
	pos = text.find('''"''')
	if pos is not -1:
		raise ValueError("Found dumb quote character on line %d; use “ ” \n%s" % (result.find_line_number_for_file(text, pos), result.find_line_text(text, pos)) )

	return


# Wrap the converted latex in appropriate header/footers.
def latexWrapper(text, templates, seed, includeFrontMatter):
	output = templates["begin"]
	if includeFrontMatter:
		output += templates["frontMatter"]
	output += templates["postFrontMatter"]
	output += text
	output += templates["end"]

	if seed < 9999:
		seed = "0%d" % seed

	# Insert the seed number where it appeared in front matter.
	msg = "This copy was generated from seed #%s and is the only copy generated from that seed." % seed
	if seed == -1:
		seed = "01893"
		msg = "This run of Advance Reader Copies have all been generated from seed #%s." % seed
	output = output.replace("SEED_TEXT", msg)
	output = output.replace("SEED_NUMBER", "%s" % seed)



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
\\thispagestyle{empty}
''', '''
\\begin{ChapterStart}
\\vspace*{4\\nbs} 
\\ChapterTitle{''', '''} 
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

template_epigraph = ['''
\\begin{adjustwidth}{3em}{3em}
\\begin{parascale}[0.88]
''', '''\\\\
\\par
\\noindent \\textit{''', '''}
\\end{parascale}
\\end{adjustwidth}
\\vspace*{2\\nbs} 
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






