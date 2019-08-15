
import sys
import pickle
import os.path

def readInputFile(inputFile):
	fileContents = ""
	with open(inputFile, "r") as fileObject:
		return fileObject.read()
	print "Can't read '%s'." % inputFile
	sys.exit()


def writeOutputFile(outputFile, outputText):
	with open(outputFile, "w") as fileObject:
		fileObject.write(outputText)
		print "\nWrote to '%s'.\n" % outputFile


def loadManifest(path, manifest):
	# We expect this to be a list of filenames, one per line.
	# Ignore any line that begins with "#"
	# We should return an array of texts, the contents of the files in order.
	contents = []
	lines = manifest.split('\n')
	for line in lines:
		if len(line) == 0 or line[0] == "#" or line.strip() == "":
			continue
		print " > Reading '%s'" % line
		file = readInputFile(path + line)
		contents.append(getFileId(line) + file)
	return contents

def getFileId(fn):
	return "\n\n%% file %s\n\n" % fn


__keyfile = None
__confirms = {}
__kfname = "confirms.dat"
__newconfirms = {}

def startConfirmKeys():
	global __keyfile
	global __confirms
	global __kfname
	if os.path.exists(__kfname):
		file = readInputFile(__kfname)
		try:
			__confirms = pickle.loads(file)
			print "Loaded confirms from %s" % __kfname
			print __confirms
		except IOError as e:
			print "Couldn't load confirms from %s: %s" % (__kfname, e)
			sys.exit()
	else:
		__confirms = {}

def finishConfirmKeys():
	global __kfname
	global __newconfirms
	try:
		writeOutputFile(__kfname, pickle.dumps(__newconfirms))
	except IOError as e:
		print "Could save confirms to %s: %s" % (__kfname, e)

def confirmKey(key):
	global __newconfirms
	__newconfirms[key] = True

def isKeyConfirmed(key):
	global __confirms
	global __newconfirms
	print "key in confirms? %s" % (key in __confirms)
	if key in __confirms and __confirms[key] == True:
		confirmKey(key)
		return True
	return False


