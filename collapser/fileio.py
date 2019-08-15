
import sys

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