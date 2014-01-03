import wikipedia
import start
from bs4 import BeautifulSoup
import unittest
import json

class TestStart(unittest.TestCase):
	def setUp(self):
		self.tlPage = wikipedia.page('Timeline of particle physics')
		self.textSoup = BeautifulSoup(self.tlPage.html())

	def testExtractTimeline(self):
		data = start.extractTimeline(self.tlPage)
		print data
		with open('particlephysics.json', 'w') as f:
			f.write(json.dumps(data))

if __name__ == '__main__':
	unittest.main()