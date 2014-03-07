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

	def test_three(self):
		html = BeautifulSoup(htmlthree)
		strings = wikipediaprocess._html_to_string_blocks(html)
		self.assertEqual(strings, stringblocksthree)


class TestStringBlocksToEvents(unittest.TestCase):
	def p(self, data):
		pprint([str(x['date']) + ':::' + x['content'][:60] for x in data])
	def test_one(self):
		evs = wikipediaprocess._string_blocks_to_events(stringblocksone)
		self.p(evs)
		self.assertEqual(len(evs), 6)
	def test_two(self):
		evs = wikipediaprocess._string_blocks_to_events(stringblockstwo)
		self.p(evs)
		self.assertEqual(len(evs), 1)
	def test_three(self):
		article = BeautifulSoup(html_particlephysics)
		evs = wikipediaprocess._string_blocks_to_events(wikipediaprocess._html_to_string_blocks(article))
		self.p(evs)
		self.assertEqual(len(evs), 31)
	def test_four(self):
		article = BeautifulSoup(html_modernhist)
		evs = wikipediaprocess._string_blocks_to_events(wikipediaprocess._html_to_string_blocks(article))
		self.p(evs)
		self.assertEqual(len(evs), 122)
	def test_combine(self):
		article = BeautifulSoup(html_iraqwar)
		evs = wikipediaprocess._string_blocks_to_events(wikipediaprocess._html_to_string_blocks(article))
		self.p(evs)
		self.assertEqual(len(evs), 5)


class TestAddImportanceToEvents(unittest.TestCase):
	def test_group_list_by_count(self):
		pprint(list(wikipediaprocess._group_list_by_count([1, 2, 3, 4, 5, 6, 7], [2, 3, 0, 1])))
	def test_bulk_importance(self):
		pprint(wikipediaprocess._bulk_importance(pageTitles))
	def test_one(self):
		x = copy.deepcopy(events)
		wikipediaprocess._add_importance_to_events(x)
		pprint(x)


class TestSeparate(unittest.TestCase):
	def test_one(self):
		evs = wikipediaprocess._separate_events(combinedEvents)
		pprint(evs)
		self.assertEqual(len(evs), 32)
		for e in evs[0:12]:
			self.assertEqual(e['date'], 2010)
		for e in evs[12:25]:
			self.assertEqual(e['date'], 2011)
		for e in evs[25:32]:
			self.assertEqual(e['date'], 2012)			


class TestWpPageToEvents(unittest.TestCase):
	def test_one(self):
		self.validate_pages([
			'Timeline of natural history',
			'Timeline of human prehistory',
			'Timeline of ancient history',
		])
		pdb.set_trace()
		self.validate_pages([
			'Timeline of modern history',
		], p = { 'separate': True })
	def test_two(self):
		self.validate_pages(['Timeline of the Middle Ages'])

		self.validate_pages([
			'16th century',
			'17th century',
			'18th century',
			'19th century'
		], p = { 'single_section': 'events' })
	def test_three(self):
		self.validate_pages([
			'Timeline of country and capital changes',
			'Timeline of European exploration',
		])
	def test_four(self):
		self.validate_pages([
			'Timeline of the Weimar Republic'
		])

	def print_event(self, event):
		print('%d: %s: %s' % (event['date'], event['date_string'], BeautifulSoup(event['content']).get_text()[:50]))

	def validate_pages(self, titles, p = None):
		# beautifulSoup warns about parsing strings like '. blah' because it
		# thinks it looks like a filename. We can safely ignore these warnings
		warnings.filterwarnings('ignore', module='bs4')
		for t in titles:
			print('---Validating ' + t + '---')
			raw_events = wikipediaprocess.wp_page_to_events_raw(t, p)
			(first_and_last, errors, fewer_than_threshold) = wikipediaprocess.get_errors(raw_events, 4)
			if fewer_than_threshold:
				print('Fewer than threshold:')
			print first_and_last
			if errors:
				print('Errors:')
				print errors


@unittest.skip('skipping perf tests')
class TestPerf(unittest.TestCase):
	def test_time_modern_history(self):
		cProfile.runctx('wikipediaprocess.wp_page_to_json("Timeline_of_modern_history")', globals(), locals())
	def test_time_modern_history_separate(self):
		cProfile.runctx('wikipediaprocess.wp_page_to_json("Timeline_of_modern_history", separate = True)', globals(), locals())

if __name__ == '__main__':
	unittest.main()
