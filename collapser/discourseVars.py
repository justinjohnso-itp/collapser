# coding=utf-8

import re
import chooser

def getDiscoursePreferredVersion(alts, vars):
	# For each discourse variable set, rank each alt for desireability. Return something weighted for the highest-ranked options.
	# TODO only outside quoted dialogue.
	# TODO if we have one short and one long alternative, the longer one will tend to get penalized more, and less often chosen.
	dpQuality = []
	print "******** %s" % alts
	for pos, item in enumerate(alts.alts):
		dpQuality.append(0)

	for pos, item in enumerate(alts.alts):
		if vars.check("avoidbe"):
			numBeVerbs = getNumBeVerbsInText(item.txt)
			if numBeVerbs > 0:
				print "(Penalizing '%s' b/c @avoidbe and found %d be verbs)" % (item.txt, numBeVerbs)
				dpQuality[pos] -= numBeVerbs

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