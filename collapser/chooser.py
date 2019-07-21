
import random



def oneOf(listOfTexts):
	return random.choice(listOfTexts)

def percent(odds):
	return random.randint(1,100) <= odds

def setSeed(num):
	random.seed(num)