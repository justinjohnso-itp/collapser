
import random


def number(highest):
	return random.randint(1,highest)

def oneOf(item):
	return random.choice(item)

__iterators = {}
def iter(key):
	global __iterators
	if key not in __iterators:
		__iterators[key] = 0
	__iterators[key] += 1
	return __iterators[key]

def percent(odds):
	return random.randint(1,100) <= odds

def setSeed(num):
	random.seed(num)

def unSeed():
	random.seed()

# Alts is an array of quantparse.Item, each of which has a "txt" and "prob". Prob is the percent chance that option will be chosen.
def distributedPick(alts):
	pick = random.randint(1,100)
	measure = 0
	for item in alts:
		if item.prob is None:
			# Case of [X or|^]
			return item.txt
		measure += item.prob
		if pick <= measure:
			return item.txt

	# If we've run out of numbers but we're still here, it means we had empty space, i.e. [60>alpha|20>beta] which means the remaining probability space prints nothing.
	return ""