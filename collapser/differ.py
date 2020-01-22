
import difflib
import itertools
import sys

def getTwoLeastSimilar(texts):

	# Find lowest similarity.
	# Similarity 1.0 means identical.
	# 0.0 means totally different (unlikely in practice). 

	if len(texts) <= 2:
		print "Error: differ.getTwoLeastSimilar was only sent %d texts; expected more." % len(texts)
		sys.exit()

	lowestSimilarityScore = 1.0
	leastSimilarPair = [-1, 1]

	for pair in itertools.combinations(range(len(texts)), 2):
		text1 = texts[pair[0]]
		text2 = texts[pair[1]]
		# print "About to compare text len %d with text len %d. %s %s" % (len(text1), len(text2), text1[:1000], text2[:1000])
		text1 = text1[:5000]
		text2 = text2[:5000]
		sm = difflib.SequenceMatcher(lambda x: x == " ", text1, text2)
		similarity = sm.ratio()
		print "%s: Similarity is %f" % (pair, round(similarity, 3))
		if similarity < lowestSimilarityScore:
			print " --> lowest so far."
			lowestSimilarityScore = similarity
			leastSimilarPair = pair

	if lowestSimilarityScore >= 0.999:
		print "Error: lowestSimilarityScore was too close 1.0 indicating texts were not generated differently."
		sys.exit()

	print "Best match was pair %s with similarity %f" % (leastSimilarPair, round(lowestSimilarityScore, 3))

	return leastSimilarPair

