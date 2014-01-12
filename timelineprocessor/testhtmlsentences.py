# -*- coding: UTF-8 -*-


from bs4 import BeautifulSoup
import wikipediaprocess
import unittest
import pdb
from pprint import pprint

# hello there <p><b>1890 <a>Stop sign</a></b>blah</p>blah
# hello there 1890 Stop signblahblah
class TestHtmlSent(unittest.TestCase):
	def testOne(self):
		data = '<p><b>1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop signs are here. And then we will fight.</a></b></p>'
		htmlSpans = wikipediaprocess.getHtmlSpans(data)
		pprint(htmlSpans)
		self.assertEqual(6, wikipediaprocess.adjustIndex(0, htmlSpans))
		self.assertEqual(9, wikipediaprocess.adjustIndex(3, htmlSpans))
		self.assertEqual(10, wikipediaprocess.adjustIndex(4, htmlSpans))
		self.assertEqual(55, wikipediaprocess.adjustIndex(5, htmlSpans))
		self.assertEqual(56, wikipediaprocess.adjustIndex(6, htmlSpans))
		pprint(wikipediaprocess.separate(data))
	def testTwo(self):
		data = 'hello ther. <p><b>1890 <a>Stop sign</a></b>blah</p>blah.'
		htmlSpans = wikipediaprocess.getHtmlSpans(data)
		pprint(htmlSpans)
		self.assertEqual(0, wikipediaprocess.adjustIndex(0, htmlSpans))
		self.assertEqual(3, wikipediaprocess.adjustIndex(3, htmlSpans))
		self.assertEqual(43, wikipediaprocess.adjustIndex(26, htmlSpans))
		self.assertEqual(44, wikipediaprocess.adjustIndex(27, htmlSpans))
		self.assertEqual(51, wikipediaprocess.adjustIndex(30, htmlSpans))
		self.assertEqual(54, wikipediaprocess.adjustIndex(33, htmlSpans))
		pprint(wikipediaprocess.separate(data))