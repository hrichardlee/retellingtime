# -*- coding: UTF-8 -*-

import wikipedia
from testwikidata import *
import wikipediaprocess
import copy
from bs4 import BeautifulSoup
import unittest
import json
from pprint import pprint
import cProfile

import pdb

class TestFindDate(unittest.TestCase):
	def setUp(self):
		self.nolayer = '1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a>'
		self.onelayer = '<b>1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b>'
		self.twolayers = '<p><b>1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b></p>'
		self.threelayers = '<p><b>1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b>blergh</p>'
		self.remainder = '<a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a>'
		self.remainderthreelayers = '<a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a>blergh'

	def test_html_parsing(self):
		(x, y) = wikipediaprocess.getFirstTextNode(BeautifulSoup(self.onelayer))
		self.assertEqual(x, '1890 ')
		self.assertEqual(y, self.remainder)
		(x, y) = wikipediaprocess._find_date(self.onelayer)
		self.assertEqual(x, 1890)
		self.assertEqual(y, self.remainder)

		(x, y) = wikipediaprocess.getFirstTextNode(BeautifulSoup(self.nolayer))
		self.assertEqual(x, '1890 ')
		self.assertEqual(y, self.remainder)
		(x, y) = wikipediaprocess._find_date(self.nolayer)
		self.assertEqual(x, 1890)
		self.assertEqual(y, self.remainder)

		(x, y) = wikipediaprocess.getFirstTextNode(BeautifulSoup(self.twolayers))
		self.assertEqual(x, '1890 ')
		self.assertEqual(y, self.remainder)
		(x, y) = wikipediaprocess._find_date(self.twolayers)
		self.assertEqual(x, 1890)
		self.assertEqual(y, self.remainder)

		(x, y) = wikipediaprocess.getFirstTextNode(BeautifulSoup(self.threelayers))
		self.assertEqual(x, '1890 ')
		self.assertEqual(y, self.remainderthreelayers)
		(x, y) = wikipediaprocess._find_date(self.threelayers)
		self.assertEqual(x, 1890)
		self.assertEqual(y, self.remainderthreelayers)

class TestHtmlToStringBlocks(unittest.TestCase):
	def test_one(self):
		html = BeautifulSoup(htmlone)
		strings = wikipediaprocess._html_to_string_blocks(html)
		self.assertEqual(strings, stringblocksone)

	def test_two(self):
		html = BeautifulSoup(htmltwo)
		strings = wikipediaprocess._html_to_string_blocks(html)
		self.assertEqual(strings, stringblockstwo)

class TestStringBlocksToEvents(unittest.TestCase):
	def p(self, data):
		pprint([str(x["date"]) + ":::" + x["content"][:60] for x in data])
	def testOne(self):
		self.p(wikipediaprocess._string_blocks_to_events(stringblocksone))
	def testTwo(self):
		article = BeautifulSoup(html_particlephysics)
		self.p(wikipediaprocess._string_blocks_to_events(wikipediaprocess._html_to_string_blocks(article)))
	def testThree(self):
		article = BeautifulSoup(html_modernhist)
		self.p(wikipediaprocess._string_blocks_to_events(wikipediaprocess._html_to_string_blocks(article)))


class TestAddImportanceToEvents(unittest.TestCase):
	def test_group_list_by_count(self):
		pprint(list(wikipediaprocess._group_list_by_count([1, 2, 3, 4, 5, 6, 7], [2, 3, 0, 1])))
	def test_bulk_importance(self):
		pprint(wikipediaprocess._bulk_importance(pageTitles))
	def testOne(self):
		x = copy.deepcopy(events)
		wikipediaprocess._add_importance_to_events(x)
		pprint(x)


class TestSeparate(unittest.TestCase):
	def testOne(self):
		pprint(wikipediaprocess._separate_events(combinedEvents))


class TestWpPageToJson(unittest.TestCase):
	def test_particle_physics(self):
		pprint(wikipediaprocess.wp_page_to_json("timeline of particle physics"))
	def test_modern_hist(self):
		pprint(wikipediaprocess.wp_page_to_json("Timeline_of_modern_history"))
	def test_modern_hist_sep(self):
		pprint(wikipediaprocess.wp_page_to_json("Timeline_of_modern_history", separate = True))
	def test_ancient_hist(self):
		pprint(wikipediaprocess.wp_page_to_json("Timeline_of_ancient_history"))


@unittest.skip("skipping perf tests")
class TestPerf(unittest.TestCase):
	def testTimeModernHistory(self):
		cProfile.runctx('wikipediaprocess.wp_page_to_json("Timeline_of_modern_history")', globals(), locals())
	def testTimeModernHistorySeparate(self):
		cProfile.runctx('wikipediaprocess.wp_page_to_json("Timeline_of_modern_history", separate = True)', globals(), locals())

if __name__ == '__main__':
	unittest.main()
