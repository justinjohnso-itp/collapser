# coding=utf-8

import re
import chooser
from textblob import TextBlob

dpStats = {}
showTrace = True

# Thoughts:
# - "wordy" should only kick in if there's more than one word, or even maybe more than a couple words? (i.e. Ursela Le Guin vs Douglas Adams)

def resetStats():
	global dpStats
	dpStats = {"avoidbe": 0, "wordy": 0, "succinct": 0, "avoidfiller": 0, "depressive": 0, "subjective": 0, "objective": 0}

def showStats(vars):
	global dpStats
	print "*******************************************************"
	print "How many times set discourse variables changed text weight:"
	print dpStats
	# filteredStats = {k, v for k, v in dpStats.items() if vars.check(k) }
	# filtered = dict(filter(lambda i: vars.check(i[0]), dpStats.items()))
	# print filtered
	print "*******************************************************"

trace_output = ""
def trace(txt):
	global trace_output
	if showTrace:
		trace_output += "%s\n" % txt

def clear_trace():
	global trace_output
	trace_output = ""

def show_trace():
	global trace_output
	print trace_output

def getDiscoursePreferredVersion(alts, vars):
	# For each discourse variable set, rank each alt for desireability. Return something weighted for the highest-ranked options.
	# TODO only outside quoted dialogue.
	# TODO if we have one short and one long alternative, the longer one will tend to get penalized more, and less often chosen.
	global dpStats
	dpQuality = []
	tracker = dpStats["avoidbe"]
	clear_trace()
	trace("******** %s" % alts)
	if len(alts.alts) == 1:
		trace("/// YES OR NO ///")
	for pos, item in enumerate(alts.alts):
		dpQuality.append(0)

	# TODO: should these be scaled so they all have equal importance? If so how?

	for pos, item in enumerate(alts.alts):
		if vars.check("avoidbe"):
			numBeVerbs = getNumBeVerbsInText(item.txt)
			if numBeVerbs > 0:
				trace("(Penalizing '%s' b/c @avoidbe and found %d be verbs)" % (item.txt, numBeVerbs))
				dpStats["avoidbe"] += 1
				dpQuality[pos] -= 1

		if vars.check("wordy"):
			if len(item.txt) == len(alts.getLongest()) and len(item.txt) > 30:
				trace("(Rewarding '%s' b/c @wordy and this is longest)" % item.txt)
				dpStats["wordy"] += 1
				dpQuality[pos] += 1

		if vars.check("succinct"):
			if len(item.txt) == len(alts.getShortest()):
				trace("(Rewarding '%s' b/c @succinct and this is shortest)" % item.txt)
				dpStats["succinct"] += 1
				dpQuality[pos] += 1

		if vars.check("avoidfiller"):
			numArticles = getNumBoringWordsInText(item.txt)
			if numArticles > 0:
				trace("(Penalizing '%s' b/c @avoidfiller and found %d weak words)" % (item.txt, numArticles))
				dpStats["avoidfiller"] += 1
				dpQuality[pos] -= 1

		if vars.check("depressive") or vars.check("subjective") or vars.check("objective"):
			safetxt = unicode(item.txt, "utf-8").encode('ascii', 'replace')
			tb = TextBlob(safetxt)
			polarity = tb.sentiment.polarity
			subjectivity = tb.sentiment.subjectivity
			if polarity <= -0.5 and vars.check("depressive"):
				trace("(Rewarding '%s' b/c @depressive and low polarity %f)" % (item.txt, polarity))
				dpStats["depressive"] += 1
				dpQuality[pos] += 1
			if subjectivity > 0.3 and vars.check("subjective"):
				trace("(Rewarding '%s' b/c @subjective and subjectivity %f)" % (item.txt, subjectivity))
				dpStats["subjective"] += 1
				dpQuality[pos] += 1
			if subjectivity > 0.3 and vars.check("objective"):
				trace("(Penalizing '%s' b/c @objective and subjectivity %f)" % (item.txt, subjectivity))
				dpStats["objective"] += 1
				dpQuality[pos] -= 1


	# TODO improve stats so if everything ranked the same, it doesn't count as a hit.
	firstVal = dpQuality[0]
	allSame = True
	for pos, item in enumerate(alts.alts):
		if dpQuality[pos] != firstVal:
			allSame = False
			break
	bestRankedPositions = getHighestPositions(dpQuality)
	selectedPos = chooser.oneOf(bestRankedPositions)
	if not allSame:
		trace("Final rankings:")
		for pos, item in enumerate(alts.alts):
			trace("%d: '%s'" % (dpQuality[pos], item.txt))
		trace("Best positions: %s" % bestRankedPositions)
		trace("Picked '%s'" % alts.alts[selectedPos].txt)

	if dpStats["avoidbe"] > tracker:
		show_trace()

	return alts.alts[selectedPos].txt




# For an array of numbers, return an array with the position(s) of the highest values found (so if there are multiple equally high values, their positions will all be returned)
def getHighestPositions(arr):
	highestRank = None
	highestPositions = []
	for pos, item in enumerate(arr):
		if highestRank is None or item > highestRank:
			highestRank = item
			highestPositions = [pos]
		elif item == highestRank:
			highestPositions.append(pos)
	return highestPositions

beVerbsRegex = re.compile(r"\b(be|been|being|am|is|isn't|are|aren't|was|wasn't|were|weren't|i'm|he's|she's|it's|they're|you're|that's|there's|what's)\b", re.IGNORECASE)

def getNumBeVerbsInText(txt):
	# Fix smart quotes
	txt = txt.replace("‘", "'")
	txt = txt.replace("’", "'")
	return len(re.findall(beVerbsRegex, txt))

boringRegex = re.compile(r"\b(the|a|an|i|you|he|she|it|we|they|me|him|her|us|them|my|your|his|its|our|their|hers|ours|yours|theirs|well|something|thing|things|stuff|okay|ok|able|maybe|could|possibly|might)\b", re.IGNORECASE)

def getNumBoringWordsInText(txt):
	return len(re.findall(boringRegex, txt))


