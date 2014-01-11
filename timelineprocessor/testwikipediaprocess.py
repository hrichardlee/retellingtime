# -*- coding: UTF-8 -*-

import wikipedia
from testdata import *
import wikipediaprocess
from bs4 import BeautifulSoup
import unittest
import json
from pprint import pprint



class TestwpPageToJson(unittest.TestCase):
	def testOne(self):
		pprint(wikipediaprocess.wpPageToJson("timeline of particle physics"))

class TestStringBlocksToEvents(unittest.TestCase):
	def p(self, data):
		pprint([str(x["date"]) + ":::" + x["content"][:60] for x in data])
	def testOne(self):
		self.p(wikipediaprocess.stringBlocksToEvents(stringblocksone))
	def testTwo(self):
		article = BeautifulSoup(html_particlephysics)
		self.p(wikipediaprocess.stringBlocksToEvents(wikipediaprocess.htmlToStringBlocks(article)))
	def testThree(self):
		article = BeautifulSoup(html_modernhist)
		self.p(wikipediaprocess.stringBlocksToEvents(wikipediaprocess.htmlToStringBlocks(article)))

class TesthtmlToStringBlocks(unittest.TestCase):
	def testOne(self):
		html = BeautifulSoup(htmlone)
		strings = wikipediaprocess.htmlToStringBlocks(html)
		self.assertEqual(strings, stringblocksone)

	def testTwo(self):
		html = BeautifulSoup(htmltwo)
		strings = wikipediaprocess.htmlToStringBlocks(html)
		self.assertEqual(strings, stringblockstwo)

class TestFindDate(unittest.TestCase):
	def setUp(self):
		self.nolayer = '1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a>'
		self.onelayer = '<b>1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b>'
		self.twolayers = '<p><b>1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b></p>'
		self.threelayers = '<p><b>1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b>blergh</p>'
		self.remainder = '<a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a>'
		self.remainderthreelayers = '<a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a>blergh'

	def testOne(self):
		(x, y) = wikipediaprocess.getFirstTextNode(BeautifulSoup(self.onelayer))
		self.assertEqual(x, '1890 ')
		self.assertEqual(y, self.remainder)
		(x, y) = wikipediaprocess.findDate(self.onelayer)
		self.assertEqual(x, 1890)
		self.assertEqual(y, self.remainder)
	def testTwo(self):
		(x, y) = wikipediaprocess.getFirstTextNode(BeautifulSoup(self.nolayer))
		self.assertEqual(x, '1890 ')
		self.assertEqual(y, self.remainder)
		(x, y) = wikipediaprocess.findDate(self.nolayer)
		self.assertEqual(x, 1890)
		self.assertEqual(y, self.remainder)
	def testThree(self):
		(x, y) = wikipediaprocess.getFirstTextNode(BeautifulSoup(self.twolayers))
		self.assertEqual(x, '1890 ')
		self.assertEqual(y, self.remainder)
		(x, y) = wikipediaprocess.findDate(self.twolayers)
		self.assertEqual(x, 1890)
		self.assertEqual(y, self.remainder)
	def testFour(self):
		(x, y) = wikipediaprocess.getFirstTextNode(BeautifulSoup(self.threelayers))
		self.assertEqual(x, '1890 ')
		self.assertEqual(y, self.remainderthreelayers)
		(x, y) = wikipediaprocess.findDate(self.threelayers)
		self.assertEqual(x, 1890)
		self.assertEqual(y, self.remainderthreelayers)

if __name__ == '__main__':
	unittest.main()
