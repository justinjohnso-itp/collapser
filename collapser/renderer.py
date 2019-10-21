
import abc

class Renderer(object):
	__metaclass__ = abc.ABCMeta

	def __init__(self, collapsedText, params):
		self.collapsedText = collapsedText
		self.params = params

	# Main entry point: takes a collapsed file and writes an output file in the given format.
	@abc.abstractmethod
	def render(self):
		pass

	# Part 1: takes the collapsed file and turns it into a valid input file for the desired output format (i.e., collapsed text to LaTeX, Markdown, etc.). Generally only called by render.
	@abc.abstractmethod
	def makeStagedFile(self):
		pass

	# Part 2: Takes the staged input file and creates the desired output format (i.e. LaTeX to PDF, Markdown to HTML, etc)
	@abc.abstractmethod
	def makeOutputFile(self):
		pass


