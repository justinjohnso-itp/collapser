
import quantparse

class Macros:
	def __init__(self):
		self.macros = {}
		self.sticky_macro_originals = {}
		self.sticky_macro_rendered = {}

	def isMacro(self, key):
		return key in self.macros or key in self.sticky_macro_originals

	def define(self, isSticky, key, body):
		if isSticky:
			self.sticky_macro_originals[key] = body
		else:
			self.macros[key] = body

	def render(self, key, params):
		if key in self.sticky_macro_rendered:
			return self.sticky_macro_rendered[key]
		elif key in self.sticky_macro_originals:
			thingToRender = self.sticky_macro_originals[key]
			result = quantparse.renderControlSequence(thingToRender, params)
			self.sticky_macro_rendered[key] = result
			return result
		elif key in self.macros:
			thingToRender = self.macros[key]
			result = quantparse.renderControlSequence(thingToRender, params)
			return result
		else:		
			return None



__m = Macros()

def reset():
	global __m
	__m = Macros()

def isMacro(key):
	global __m
	return __m.isMacro(key)

def handleDefs(tokens, params):
	output = []
	index = 0
	global __m
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
		if __m.isMacro(token.value):
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

		__m.define(isSticky, macroKey, macroBody)
		index += 1 # skip over final CTRLEND

	return output

def expand(text, params):
	mStart = '''{'''
	mEnd = '''}'''
	global __m
	if text.find(mStart + mEnd) != -1:
		raise ValueError("Can't have empty macro sequence {}")
	startPos = text.find(mStart)
	while startPos != -1:
		endPos = text.find(mEnd, startPos+1)
		key = text[startPos+1:endPos]
		rendered = __m.render(key, params)
		if rendered == None:
			# raise ValueError("Unrecognized macro {%s}" % key)
			print "Unrecognized macro {%s}" % key
			startPos = text.find(mStart, startPos+1)
			continue
		text = text[:startPos] + rendered + text[endPos+1:]
		# print "s: %d, e: %d, exp: %s, ren: %s, text: '%s'" % (startPos, endPos, exp, rendered, text)
		oldStartPos = startPos
		startPos = text.find(mStart, startPos)
		if oldStartPos == startPos:
			raise ValueError("Can't resolve macro sequence starting '%s'...; breaking" % text[startPos:startPos+20])

	return text
