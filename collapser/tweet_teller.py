# Standalone program that will read in an input file(s) of prepared Tweet-length contents, and output them spaced out over a given amount of time. 

import sys
import getopt
import fileio

def showUsage():
	print """Usage: tweet_teller -i <inputs> -a <accounts> -d duration_in_minutes"""


def main():
	inputFiles = []
	inputTweetStorms = []
	accounts = []
	duration = -1

	opts, args = getopt.getopt(sys.argv[1:], "i:a:d:", ["help"])
	if len(args) > 0:
		print "Unrecognized arguments: %s" % args
		showUsage()
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
		elif opt == "--help":
			showUsage()
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

	for filename in inputFiles:
		data = fileio.readInputFile(filename)
		arr = fileio.deserialize(data)
		inputTweetStorms.append(arr)

	# TODO: Validate that each inputTweetStorm is in the expected format.

	launch(inputTweetStorms, accounts, duration)


def launch(inputTweetStorms, accounts, duration):
	# inputTweetStorm is an array of tweetstorms, each of which is an array of tweets.
	longestLen = len(getLongestArray(inputTweetStorms))
	for pos in range(0,len(accounts)):
		print "For account @%s, will do %d tweets." % (accounts[pos], len(inputTweetStorms[pos]))
	print "********"
	print "Will tweet spaced out over %d minutes. There are %d tweets in longest array, so time between tweets will be %d seconds." % (duration, longestLen, (duration * 60) / longestLen)

def getLongestArray(arrOfArrs):
	longestArr = []
	longestLen = -1
	for arr in arrOfArrs:
		if len(arr) > longestLen:
			longestLen = len(arr)
			longestArr = arr
	return longestArr


main()
