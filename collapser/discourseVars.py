# coding=utf-8

import re
import chooser
from textblob import TextBlob

dpStats = {}

def resetStats():
	global dpStats
	dpStats = {"avoidbe": 0, "wordy": 0, "succinct": 0, "avoidfiller": 0, "depressive": 0, "subjective": 0, "objective": 0}

def showStats():
	global dpStats
	print "*******************************************************"
	print "How many times discourse variables changed text weight:"
	print dpStats
	print "*******************************************************"

def getDiscoursePreferredVersion(alts, vars):
	# For each discourse variable set, rank each alt for desireability. Return something weighted for the highest-ranked options.
	# TODO only outside quoted dialogue.
	# TODO if we have one short and one long alternative, the longer one will tend to get penalized more, and less often chosen.
	global dpStats
	dpQuality = []
	print "******** %s" % alts
	if len(alts.alts) == 1:
		print "/// YES OR NO ///"
	for pos, item in enumerate(alts.alts):
		dpQuality.append(0)

	# TODO: should these be scaled so they all have equal importance? If so how?

	for pos, item in enumerate(alts.alts):
		if vars.check("avoidbe"):
			numBeVerbs = getNumBeVerbsInText(item.txt)
			if numBeVerbs > 0:
				print "(Penalizing '%s' b/c @avoidbe and found %d be verbs)" % (item.txt, numBeVerbs)
				dpStats["avoidbe"] += 1
				dpQuality[pos] -= 1

		if vars.check("wordy"):
			if len(item.txt) == len(alts.getLongest()):
				print "(Rewarding '%s' b/c @wordy and this is longest)" % item.txt
				dpStats["wordy"] += 1
				dpQuality[pos] += 1

		if vars.check("succinct"):
			if len(item.txt) == len(alts.getShortest()):
				print "(Rewarding '%s' b/c @succinct and this is shortest)" % item.txt
				dpStats["succinct"] += 1
				dpQuality[pos] += 1

		if vars.check("avoidfiller"):
			numArticles = getNumBoringWordsInText(item.txt)
			if numArticles > 0:
				print "(Penalizing '%s' b/c @avoidfiller and found %d weak words)" % (item.txt, numArticles)
				dpStats["avoidfiller"] += 1
				dpQuality[pos] -= 1

		if vars.check("depressive") or vars.check("subjective") or vars.check("objective"):
			safetxt = unicode(item.txt, "utf-8").encode('ascii', 'replace')
			tb = TextBlob(safetxt)
			polarity = tb.sentiment.polarity
			subjectivity = tb.sentiment.subjectivity
			if polarity <= -0.5 and vars.check("depressive"):
				print "Rewarding '%s' b/c @depressive and low polarity %f" % (item.txt, polarity)
				dpStats["depressive"] += 1
				dpQuality[pos] += 1
			if subjectivity > 0.3 and vars.check("subjective"):
				print "Rewarding '%s' b/c @subjective and subjectivity %f" % (item.txt, subjectivity)
				dpStats["subjective"] += 1
				dpQuality[pos] += 1
			if subjectivity > 0.3 and vars.check("objective"):
				print "Penalizing '%s' b/c @objective and subjectivity %f" % (item.txt, subjectivity)
				dpStats["objective"] += 1
				dpQuality[pos] -= 1


	# TODO improve stats so if everything ranked the same, it doesn't count as a hit.
	print "Final rankings:"
	for pos, item in enumerate(alts.alts):
		print "%d: '%s'" % (dpQuality[pos], item.txt)
	bestRankedPositions = getHighestPositions(dpQuality)
	print "Best positions: %s" % bestRankedPositions
	selectedPos = chooser.oneOf(bestRankedPositions)
	print "Picked '%s'" % alts.alts[selectedPos].txt

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

boringRegex = re.compile(r"\b(the|a|an|i|you|he|she|it|we|they|me|him|her|us|them|my|your|his|its|our|their|hers|ours|yours|theirs|well|something|thing|things|stuff|okay|ok|able)\b", re.IGNORECASE)

def getNumBoringWordsInText(txt):
	return len(re.findall(boringRegex, txt))


