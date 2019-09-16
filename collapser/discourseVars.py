# coding=utf-8

import re
import chooser

def getDiscoursePreferredVersion(alts, vars):
	# For each discourse variable set, rank each alt for desireability. Return something weighted for the highest-ranked options.
	# TODO only within quoted dialogue.
	dpQuality = []
	for pos, item in enumerate(alts):
		dpQuality[pos] = 0

	for pos, item in enumerate(alts):
		if vars.check("avoidbe"):
			dpQuality[pos] -= getNumBeVerbsInText(item)

	bestRankedPositions = getHighestPositions(dpQuality)
	selectedPos = chooser.oneOf(bestRankedPositions)

	return alts.alts[selectedPos]




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