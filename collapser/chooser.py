
import random



def oneOf(listOfTexts):
	return random.choice(listOfTexts)


def setSeed(num):
	random.seed(num)