
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

__seedfilename = "seednum.dat"
__generation = 0

def getNextSeedFromFile():
	global __seedfilename
	global __generation
	seedRaw = readInputFile(__seedfilename)
	# We expect this to be a 4-digit integer.
	try:
		seed = int(seedRaw)
	except:
		print "Couldn't read '%s' contents as int: found '%s'." % (__seedfilename, seedRaw)
		sys.exit()

	seed += 1
	if seed > 9999:
		print "Exceeded available seed range for generation '%d'; halting." % __generation
		sys.exit()

	writeOutputFile(__seedfilename, "%d" % seed)
	print "(Iterated from file, generation %d, seed %d)" % (__generation, seed)
	return (__generation * 10000) + seed




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
		print "Couldn't save confirms to %s: %s" % (__kfname, e)

def confirmKey(key):
	global __newconfirms
	__newconfirms[key] = True

def isKeyConfirmed(key):
	global __confirms
	global __newconfirms
	if key in __confirms and __confirms[key] == True:
		confirmKey(key)
		return True
	return False


