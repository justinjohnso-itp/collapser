# coding=utf-8

import re

def getDiscoursePreferredVersion(alts, vars):
	# For each discourse variable set, rank each alt for desireability. Return something weighted for the highest-ranked options.
	# TODO only within quoted dialogue.
	dpQuality = []
	for pos, item in enumerate(alts):
		dpQuality[pos] = 0

	for pos, item in enumerate(alts):
		if vars.check("avoidbe"):
			dpQuality[pos] -= getNumBeVerbsInText(item)

	bestRankedPos = getHighestPosition(dpQuality)





def getHighestPosition(arr):
	highestRank = -1000
	highestPos = -1
	for pos, item in enumerate(arr):
		if item > highestRank:
			highestRank = item
			highestPos = pos
	return highestPos

beVerbsRegex = re.compile(r"\b(be|been|being|am|is|isn't|are|aren't|was|wasn't|were|weren't|i'm|he's|she's|it's|they're|you're|that's|there's|what's)\b", re.IGNORECASE)

def getNumBeVerbsInText(txt):
	# Fix smart quotes
	txt = txt.replace("‘", "'")
	txt = txt.replace("’", "'")
	return len(re.findall(beVerbsRegex, txt))