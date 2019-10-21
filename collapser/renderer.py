
import abc

class Renderer(object):
	__metaclass__ = abc.ABCMeta

	def __init__(self, collapsedText, params):
		self.collapsedText = collapsedText
		self.params = params

	@abc.abstractmethod
	def render(self, fileId):
		pass

	@abc.abstractmethod
	def makeStagedFile(self, fileId):
		pass

	@abc.abstractmethod
	def makeOutputFile(self, fileId):
		pass


