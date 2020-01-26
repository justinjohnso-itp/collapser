# Standalone program that will read in an input file(s) of prepared Tweet-length contents, and output them spaced out over a given amount of time. 

import sys
import getopt
import fileio
import threading
import time

def showUsage():
	print """Usage: tweet_teller -i <inputs> -a <accounts> -d duration_in_minutes"""

MAX_TWEET_CHARS = 280

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
		for item in arr:
			if len(item) > MAX_TWEET_CHARS:
				print "*** Error: a tweet in this tweetstorm exceeded %d characters, was %d instead: '%s'" % (MAX_TWEET_CHARS, len(item), item)
				sys.exit()
		inputTweetStorms.append(arr)

	# TODO: Validate that each inputTweetStorm is in the expected format.

	launch(inputTweetStorms, accounts, duration)


def launch(inputTweetStorms, accounts, duration):
	# inputTweetStorm is an array of tweetstorms, each of which is an array of tweets.

	for pos in range(0, len(accounts)):
		setupTweetStorm(accounts[pos], inputTweetStorms[pos], duration)


def setupTweetStorm(account, tweetStorm, duration):
	timeInSecondsBetweenTweets = (duration * 60) / len(tweetStorm)
	print "For account @%s, will do %d tweets over %d minutes, with %d seconds between tweets." % (account, len(tweetStorm), duration, timeInSecondsBetweenTweets)
	threading.Thread(target=tweetTick, args=(account, tweetStorm, 0, timeInSecondsBetweenTweets)).start()


def tweetTick(account, tweetStorm, pos, delayInSeconds):
	tweet(account, tweetStorm[pos])
	time.sleep(delayInSeconds)
	pos += 1
	if pos < len(tweetStorm):
		tweetTick(account, tweetStorm, pos, delayInSeconds)

def tweet(account, tweet):
	tweetToConsole(account, tweet)
	tweetToFiles(account, tweet)



def tweetToConsole(account, tweet):
	print "** @%s: '%s'" % (account, tweet)

def tweetToFiles(account, tweet):
	fileio.append("work/at-%s.dat" % account, "\n\n@%s: '%s'" % (account, tweet))


main()
