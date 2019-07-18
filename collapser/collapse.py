# This handles taking converting a quant document into a single possibility.





# import calc
import quantparse






# Main entry point.
def go(sourceText):
	outputText = sourceText
	quantparse.run()
	return outputText
