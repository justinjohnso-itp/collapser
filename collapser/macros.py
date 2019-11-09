
import ctrlseq
import result

# TODO: Doesn't seem to be checking that StickyMacro isn't defined twice?
# TODO: Sticky Macros aren't honoring author prefered mark. See test_author_preferred_sticky_macro

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
			result = ctrlseq.render(thingToRender, params)
			self.sticky_macro_rendered[key] = result
			return result
		elif key in self.macros:
			thingToRender = self.macros[key]
			result = ctrlseq.render(thingToRender, params)
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
			badResult = result.Result(result.PARSE_RESULT)
			badResult.flagBad("Macro '%s' is defined twice." % token.value, params.originalText, token.lexpos)
			raise result.ParseException(badResult)
		macroKey = token.value
		if index+3 > len(tokens) or tokens[index+1].type != "CTRLEND" or tokens[index+2].type != "CTRLBEGIN":
			badResult = result.Result(result.PARSE_RESULT)
			badResult.flagBad("Macro '%s' must be immediately followed by a control sequence." % macroKey, params.originalText, token.lexpos)
			raise result.ParseException(badResult)
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

formatting_codes = ["section_break", "chapter", "part", "end_part_page", "verse", "verse_inline", "epigraph", "pp", "i", "vspace"]

def expand(text, params, haltOnBadMacros=True):
	mStart = '''{'''
	mEnd = '''}'''
	MAX_MACRO_DEPTH = 6
	global __m
	emptyPos = text.find(mStart + mEnd)
	if emptyPos != -1:
		badResult = result.Result(result.PARSE_RESULT)
		badResult.flagBad("Can't have empty macro sequence {}", params.originalText, emptyPos)
		raise result.ParseException(badResult)
	startPos = text.find(mStart)
	renderHadMoreMacrosCtr = 0
	while startPos != -1:
		# Get macro name
		endPos = text.find(mEnd, startPos+1)
		key = text[startPos+1:endPos]

		# Expand the macro
		rendered = __m.render(key, params)

		# If unrecognized, see if it's a formatting code; fail otherwise.
		if rendered == None:
			parts = key.split('/')
			if parts[0] in formatting_codes:
				startPos = text.find(mStart, startPos+1)
				continue
			if haltOnBadMacros:
				badResult = result.Result(result.PARSE_RESULT)
				badResult.flagBad("Unrecognized macro {%s}" % key, text, startPos)
				raise result.ParseException(badResult)
			startPos = text.find(mStart, startPos+1)
			continue

		# If the expansion itself contains macros, check for recursion then set the start position for the next loop iteration.
		if rendered.find(mStart) >= 0:
			renderHadMoreMacrosCtr += 1
		else:
			renderHadMoreMacrosCtr = 0
		if renderHadMoreMacrosCtr > MAX_MACRO_DEPTH:
			badResult = result.Result(result.PARSE_RESULT)
			badResult.flagBad("Possibly recursive macro loop near here", text[startPos:startPos+20], startPos)
			raise result.ParseException(badResult)

		text = text[:startPos] + rendered + text[endPos+1:]
		oldStartPos = startPos
		startPos = text.find(mStart, startPos)

	return text
