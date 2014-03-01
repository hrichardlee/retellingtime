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
import warnings

import pdb


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
		evs = wikipediaprocess._string_blocks_to_events(stringblocksone)
		self.p(evs)
		self.assertEqual(len(evs), 3)
	def testTwo(self):
		evs = wikipediaprocess._string_blocks_to_events(stringblockstwo)
		self.p(evs)
		self.assertEqual(len(evs), 1)
	def testThree(self):
		article = BeautifulSoup(html_particlephysics)
		evs = wikipediaprocess._string_blocks_to_events(wikipediaprocess._html_to_string_blocks(article))
		self.p(evs)
		self.assertEqual(len(evs), 31)
	def testFour(self):
		article = BeautifulSoup(html_modernhist)
		evs = wikipediaprocess._string_blocks_to_events(wikipediaprocess._html_to_string_blocks(article))
		self.p(evs)
		self.assertEqual(len(evs), 113)


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


class TestWpPageToEvents(unittest.TestCase):
	def test_one(self):
		self.validate_pages([
			'Timeline of natural history',
			'Timeline of human prehistory',
			'Timeline of ancient history',
		])
		self.validate_pages([
			'Timeline of modern history',
		], separate = True)
	def failing(self):
		self.validate_pages([
			'Timeline of the Middle Ages',
			'Timeline of early modern history',
			'Timeline of country and capital changes',
			'Timeline of European exploration',
		])

	def print_event(self, event):
		print('%d: %s: %s' % (event['date'], event['date_string'], event['content'][:20]))

	def validate_page(self, title, separate = False):
		# beautifulSoup warns about parsing strings like ". blah" because it
		# thinks it looks like a filename. We can safely ignore these warnings
		warnings.filterwarnings('ignore', module='bs4')

		print('---Validating ' + title + '---')

		raw_events = wikipediaprocess._wp_page_to_events_raw(title, separate)


		if len(raw_events) < 3:
			print('fewer than 3 events:')
			for e in raw_events:
				self.print_event(e)
		else:
			print('first and last events:')
			self.print_event(raw_events[0])
			self.print_event(raw_events[-1])

		for e in [e for e in raw_events if len(e['content']) < 5]:
			print ('short event:')
			self.print_event(e)

		# look for out of order events
		for i, (curre, nexte) in enumerate(zip(raw_events[:-1], raw_events[1:])):
			if curre['date'] > nexte['date']:
				print('out of order events:')
				if (i == 0):
					print('---')
				else:
					self.print_event(raw_events[i-1])
				self.print_event(curre)
				self.print_event(nexte)
				print('')

	def validate_pages(self, titles, separate = False):
		for t in titles:
			self.validate_page(t, separate)


@unittest.skip("skipping perf tests")
class TestPerf(unittest.TestCase):
	def testTimeModernHistory(self):
		cProfile.runctx('wikipediaprocess.wp_page_to_json("Timeline_of_modern_history")', globals(), locals())
	def testTimeModernHistorySeparate(self):
		cProfile.runctx('wikipediaprocess.wp_page_to_json("Timeline_of_modern_history", separate = True)', globals(), locals())

if __name__ == '__main__':
	unittest.main()
