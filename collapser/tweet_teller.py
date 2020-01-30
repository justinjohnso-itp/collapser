# Standalone program that will read in an input file(s) of prepared Tweet-length contents, and output them spaced out over a given amount of time. 

import fileio
import chooser
import twitter

import sys
import getopt
import threading
import time

def showUsage():
	print """
Tweet Teller
Usage: tweet_teller -i <inputs> -a <accounts> -d duration_in_minutes
                    --test     Pull the latest tweet from @subcutanean
"""

MAX_TWEET_CHARS = 280
TWITTER_RATE_LIMIT = 300

def main():
	inputFiles = []
	inputTweetStorms = []
	accounts = []
	duration = -1

	opts, args = getopt.getopt(sys.argv[1:], "i:a:d:", ["help", "test"])
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
		elif opt == "--test":
			testIt()
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
	print "TweetTeller"
	print "Ctrl-Z to halt all threads."

	# Validate
	totals = []
	for pos in range(0, len(accounts)):
		totals.append(len(inputTweetStorms[pos]))
	if sum(totals) > TWITTER_RATE_LIMIT:
		print "*** Error: input tweetstorms have lengths %s but that is a total of %d tweets, and the rate limit is %d, so this is too many to do in one performance." % (totals, sum(totals), TWITTER_RATE_LIMIT)
		sys.exit()
	print "Preparing %d tweets across %d files..." % (sum(totals), len(inputTweetStorms))

	# Go
	for pos in range(0, len(accounts)):
		setupTweetStorm(accounts[pos], inputTweetStorms[pos], duration)


tweetThreads = []

def setupTweetStorm(account, tweetStorm, duration):
	global tweet_threads
	timeInSecondsBetweenTweets = float(duration * 60) / float(len(tweetStorm))
	if timeInSecondsBetweenTweets < 10:
		print "To space %s tweets out over %s minutes would require %s seconds between tweets; this is below our minimum value of 10, so halting." % (len(tweetStorm), duration, timeInSecondsBetweenTweets)
		sys.exit()
	if timeInSecondsBetweenTweets > 120:
		print "To space %s tweets out over %s minutes would require %s seconds between tweets; this is higher than our predetermined threshold, so halting." % (len(tweetStorm), duration, timeInSecondsBetweenTweets)
		sys.exit()
	timeInSecondsBetweenTweets = int(timeInSecondsBetweenTweets)

	print "For account @%s, will do %d tweets over %d minutes, with %d seconds between tweets." % (account, len(tweetStorm), duration, timeInSecondsBetweenTweets)
	thread = threading.Thread(target=tweetTickQueue, args=(account, tweetStorm, 0, timeInSecondsBetweenTweets))
	thread.do_run = True
	thread.start()
	tweetThreads.append(thread)


def tweetTickQueue(account, tweetStorm, pos, delayInSeconds):
	# Just a bit of a wait so all the startup messages clump together on the console.
	time.sleep(0.1)
	tweetTick(account, tweetStorm, pos, delayInSeconds)

def tweetTick(account, tweetStorm, pos, delayInSeconds):
	thread = threading.current_thread()
	if not thread.do_run:
		print "*** Halting thread for @%s." % account
		return
	tweet(account, tweetStorm[pos])
	time.sleep(delayInSeconds)
	pos += 1
	if pos < len(tweetStorm):
		tweetTick(account, tweetStorm, pos, delayInSeconds)

def tweet(account, tweet):

	try:
		# Turn on any or all of these.
		# tweetToTwitter(account, tweet)
		tweetToConsole(account, tweet)
		# tweetToConsoleWithOccasionalErrors(account, tweet)
		tweetToFiles(account, tweet)

	# https://twython.readthedocs.io/en/latest/api.html#exceptions

	# except twython.TwythonAuthError as e:
	# 	print e
	# 	stopTweetThreads()
	# except twython.TwythonRateLimitError as e:
	# 	print e
	# 	stopTweetThreads()
	# except twython.TwythonError as e:
	# 	print e
	# 	stopTweetThreads()
	except Exception as e:
		print "\n*** EXCEPTION: %s" % e
		stopTweetThreads()


def stopTweetThreads():
	global tweetThreads
	print "*** Stopping all tweet threads."
	for thread in tweetThreads:
		print "***   Setting %s do_run to False." % thread
		thread.do_run = False



def tweetToConsole(account, tweet):
	print "> @%s: '%s'" % (account, tweet)

def tweetToConsoleWithOccasionalErrors(account, tweet):
	if chooser.percent(85):
		tweetToConsole(account, tweet)
	else:
		raise Exception("Test of an Exception for account @%s." % account) 

def tweetToFiles(account, tweet):
	fileio.append("work/at-%s.dat" % account, "\n\n@%s: '%s'" % (account, tweet))

def tweetToTwitter(account, tweet):
	tweetToConsole(account, tweet)
	twitter.tweet(account, tweet)




def testIt():
	# print twitter.verifyCredentials("subcutanean2160")
	print twitter.getLastTweet("subcutanean9999")
	# print twitter.tweet("subcutanean9999", "its another test message")



main()
