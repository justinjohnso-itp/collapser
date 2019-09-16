# coding=utf-8

import re

beVerbsRegex = re.compile(r"\b(be|been|being|am|is|isn't|are|aren't|was|wasn't|were|weren't|i'm|he's|she's|it's|they're|you're|that's|there's|what's)\b")
smartQuoteRegex = re.compile(r"[‘’]")

def getDiscoursePreferredVersion(alts):
	# For each discourse variable set, rank each alt for desireability. Return something weighted for the highest-ranked options.
	# TODO only within quoted dialogue.
	dpQuality = []
	for pos, item in enumerate(alts):
		thisItem = re.sub(smartQuoteRegex, "'", item)  # ignore smart quotes
		if variables.set("avoidbe"):
			# Subtract one for each "be" verb.
			score = 1 - getNumBeVerbsInText(thisItem)
			dpQuality[pos] = score

def getNumBeVerbsInText(txt):
	return len(re.findall(beVerbsRegex, txt))