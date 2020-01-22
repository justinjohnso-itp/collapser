
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

def getFilesFromManifest(manifest):
	# We expect this to be a list of filenames, one per line.
	# Ignore any line that begins with "#"
	fileList = []
	lines = manifest.split('\n')
	for line in lines:
		if len(line) == 0 or line[0] == "#" or line.strip() == "":
			continue
		fileList.append(line)
	return fileList

def loadManifestFromFileList(path, fileList):
	# Concatenate the contents of a list of files, with an identifier comment dividing the chunks.
	contents = []
	for file in fileList:
		fileWithPath = path + file
		# print " > Reading '%s'" % fileWithPath
		fileContents = readInputFile(fileWithPath)
		contents.append(getFileId(file) + fileContents)
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
__kfpath = "confirms/"
__newconfirms = {}
__kfkey = ""

def startConfirmKeys(fileSetKey):
	global __keyfile
	global __confirms
	global __kfpath
	global __kfkey
	kfname = __kfpath + fileSetKey
	__kfkey = fileSetKey
	if os.path.exists(kfname):
		file = readInputFile(kfname)
		try:
			__confirms = pickle.loads(file)
			print "Loaded confirms from %s" % kfname
		except IOError as e:
			print "Couldn't load confirms from %s: %s" % (kfname, e)
			sys.exit()
	else:
		__confirms = {}

def confirmKey(key):
	global __newconfirms
	__newconfirms[key] = True

def reconfirmAll():
	global __newconfirms
	for key in __confirms:
		confirmKey(key)

def finishConfirmKeys():
	global __kfpath
	global __newconfirms
	global __kfkey
	kfname = __kfpath + __kfkey
	try:
		writeOutputFile(kfname, pickle.dumps(__newconfirms))
	except IOError as e:
		print "Couldn't save confirms to %s: %s" % (kfname, e)




def isKeyConfirmed(key):
	global __confirms
	global __newconfirms
	return key in __confirms and __confirms[key] == True


