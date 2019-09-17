# coding=utf-8

import re
import chooser

dpStats = {}

def resetStats():
	global dpStats
	dpStats = {"avoidbe": 0, "wordy": 0, "succinct": 0}

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

	for pos, item in enumerate(alts.alts):
		if vars.check("avoidbe"):
			numBeVerbs = getNumBeVerbsInText(item.txt)
			if numBeVerbs > 0:
				print "(Penalizing '%s' b/c @avoidbe and found %d be verbs)" % (item.txt, numBeVerbs)
				dpStats["avoidbe"] += 1
				dpQuality[pos] -= numBeVerbs

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