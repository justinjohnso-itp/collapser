
import quantparse

macros = {}
sticky_macro_originals = {}
sticky_macro_rendered = {}

def reset():
	global macros
	global sticky_macro_originals
	global sticky_macro_rendered
	macros = {}
	sticky_macro_originals = {}
	sticky_macro_rendered = {}

def isMacro(key):
	global macros
	global sticky_macro_originals
	return key in macros or key in sticky_macro_originals

def addMacro(isSticky, key, body):
	global macros
	global sticky_macro_originals
	if isSticky:
		sticky_macro_originals[key] = body
	else:
		macros[key] = body

def renderMacro(key, params):
	global macros
	global sticky_macro_originals
	global sticky_macro_rendered
	if key in sticky_macro_rendered:
		return sticky_macro_rendered[key]
	elif key in sticky_macro_originals:
		thingToRender = sticky_macro_originals[key]
		result = quantparse.renderControlSequence(thingToRender, params)
		sticky_macro_rendered[key] = result
		return result
	elif key in macros:
		thingToRender = macros[key]
		result = quantparse.renderControlSequence(thingToRender, params)
		return result
	else:		
		return None

def handleDefs(tokens, params):
	output = []
	index = 0
	while index < len(tokens):
		token = tokens[index]
		if token.type != "CTRLBEGIN":
			output.append(token)
			index += 1
			continue
		index += 1
		token = tokens[index]
		if token.type != "MACRO":
			output.append(tokens[index-1])
			output.append(token)
			index += 1
			continue
		isSticky = token.value == "STICKY_MACRO"
		index += 1
		token = tokens[index]
		assert token.type == "TEXT"
		if isMacro(token.value):
			raise ValueError("Macro '@%s' is defined twice." % token.value)
		macroKey = token.value
		if index+3 > len(tokens) or tokens[index+1].type != "CTRLEND" or tokens[index+2].type != "CTRLBEGIN":
			raise ValueError("Macro '@%s' must be immediately followed by a control sequence." % macroKey)
		index += 3
		token = tokens[index]
		macroBody = []
		while token.type != "CTRLEND":
			macroBody.append(token)
			index += 1
			token = tokens[index]

		addMacro(isSticky, macroKey, macroBody)
		index += 1 # skip over final CTRLEND

	return output

def expand(text, params):
	mStart = '''{'''
	mEnd = '''}'''
	if text.find(mStart + mEnd) != -1:
		raise ValueError("Can't have empty macro sequence {}")
	startPos = text.find(mStart)
	while startPos != -1:
		endPos = text.find(mEnd, startPos+1)
		key = text[startPos+1:endPos]
		rendered = renderMacro(key, params)
		if rendered == None:
			raise ValueError("Unrecognized macro {%s}" % key)
		text = text[:startPos] + rendered + text[endPos+1:]
		# print "s: %d, e: %d, exp: %s, ren: %s, text: '%s'" % (startPos, endPos, exp, rendered, text)
		oldStartPos = startPos
		startPos = text.find(mStart, startPos)
		if oldStartPos == startPos:
			raise ValueError("Can't resolve macro sequence starting '%s'...; breaking" % text[startPos:startPos+20])

	return text
