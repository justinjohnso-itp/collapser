# Abstraction of Twitter interface.

from twython import Twython
import fileio

creds = {}

def getLastTweet(account):
	global creds
	setCredentials()
	twitter = Twython(creds["APP_KEY"], creds["APP_SECRET"], creds["OAUTH_ACCESS_TOKEN"], creds["OAUTH_ACCESS_TOKEN_SECRET"])
	user_timeline = twitter.get_user_timeline(user_id=account)
	if len(user_timeline) > 0:
		lastTweet = user_timeline[0]
		return lastTweet["text"]

	# auth = twitter.get_authentication_tokens()

def setCredentials():
	global creds
	if "APP_KEY" not in creds:
		credsRaw = fileio.readInputFile("collapser/keys/twitter.keys")
		credsLines = credsRaw.split("\n")
		creds = {
			"APP_KEY": credsLines[0],
			"APP_SECRET": credsLines[1],
			"OAUTH_ACCESS_TOKEN": credsLines[2],
			"OAUTH_ACCESS_TOKEN_SECRET": credsLines[3]
		}
