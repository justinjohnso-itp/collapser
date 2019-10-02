
import shlex
import subprocess
import re
import sys

def runCommand(command, paramString, shell=False):
	if shell:
		cmdArray = "%s %s" % (command, paramString)
	else:
		cmdArray = shlex.split(paramString)
		cmdArray.insert(0, command)

	result = {
		"success": False,
		"output": ""
	}

	try:
		output = subprocess.check_output(cmdArray, stderr=subprocess.STDOUT, shell=shell)
		result["success"] = True
		result["output"] = output
	except subprocess.CalledProcessError as e:
		result["success"] = False
		result["output"] = e.output

	return result


# Note: This requires pdftk, and specifically the version here updated for newer MacOS: https://stackoverflow.com/questions/39750883/pdftk-hanging-on-macos-sierra

def countPages(pdfPath):
	result = runCommand("pdftk", "%s dump_data | grep NumberOfPages" % pdfPath, shell=True)
	if not result["success"]:
		print "*** Couldn't get stats on output PDF; aborting."
		sys.exit()
	# == "NumberOfPages: 18"
	pagesResult = re.search(r"NumberOfPages: ([0-9]+)", result["output"])
	numPDFPages = int(pagesResult.groups()[0])
	return numPDFPages


# This also required pdftk, plus a blankpages.pdf with a large number of empty pages of the same size as the rest of the book.
def addBlankPages(inputPDF, outputPDF, numBlankPages):
	result = runCommand("pdftk", "A=%s B=extras/blankpages.pdf cat A B1-%s output %s" % (inputPDF, numBlankPages, outputPDF))
	if not result["success"]:
		print "*** Couldn't generate padded PDF. %s" % result["output"]
		sys.exit()

