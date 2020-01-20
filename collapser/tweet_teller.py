# Standalone program that will read in an input file(s) of prepared Tweet-length contents, and output them spaced out over a given amount of time. 

import sys
import getopt

def showUsage():
	print """Usage: tweet_teller -i <inputs> -a <accounts> -d duration_in_minutes"""


def main():
	inputFiles = []
	inputTweetStorms = []
	accounts = []
	duration = -1

	opts, args = getopt.getopt(sys.argv[1:], "i:", "a:", "d:")
	if len(args) > 0:
		print "Unrecognized arguments: %s" % args
		sys.exit()
	for opt, arg in opts:
		if opt == "-i":
			inputFiles = arg.split(',')
		elif opt == "-a":
			accounts = arg.split(',')
		elif opt == "-d":
			try:
				duration = int(arg)
			except:
				print "Invalid -d(uration) parameter '%s': not an integer (should be a number of minutes)." % arg
				sys.exit()			

	if len(inputFiles) == 0:
		print "*** No input files specified. ***\n"
		showUsage()
		sys.exit()

	if len(accounts) != len(inputFiles):
		print "*** Found %d input files but %d accounts; these must correspond 1-to-1. ***" % (len(inputFiles), len(accounts))
		sys.exit()

	if duration <= 0:
		print "*** Duration %d must be > 0 minutes. ***" % duration
		sys.exit()

	for filename, pos in inputFiles:
		inputTweetStorms[pos] = readInputFile(filename)

	# TODO: Validate that each inputTweetStorm is in the expected format.

	launch(inputTweetStorms, accounts, duration)


def launch(inputTweetStorms, accounts, duration)
	longestTweetStorm = getLongestArray(inputTweetStorms)
	longestLen = len(longestTweetStorm)
	for x in enumerate(len(accounts)):
		print "For account @%s, will tweet data: '%s'" % (accounts[x], inputTweetStorms[x])
	print "********"
	print "Will tweet spaced out over %d minutes. There are %d tweets in longest array, so time between tweets will be %d seconds." % (duration, longestLen, (duration * 60) / longestLen)

def getLongestArray(arrOfArrs):
	# STUB
	return arrOfArrs[0]


