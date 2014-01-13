# -*- coding: UTF-8 -*-


from bs4 import BeautifulSoup
import wikipediaprocess
import unittest
import pdb
from pprint import pprint
from htmlsplitter import HtmlSplitter


class TestHtmlSplitter(unittest.TestCase):
	def setUp(self):
		self.data = '0abc4<p><b><a>14defg21</a></b>30hijk37</p>42mnop49'
		#            0---4---------5-----12--------13----20----21----28

	def test_ranges(self):
		splitter = HtmlSplitter(self.data)
		top_level_ranges = splitter._top_level_ranges
		self.assertEqual(
			[r["range"] for r in top_level_ranges],
			[(0, 5), (5, 21), (21, 29)])
		self.assertEqual(
			[r["range"] for r in splitter._get_applicable_ranges(
				top_level_ranges,
				0, 5)],
			[(0, 5)])
		self.assertEqual(
			[r["range"] for r in splitter._get_applicable_ranges(
				top_level_ranges,
				22, 29)],
			[(21, 29)])
		self.assertEqual(
			[r["range"] for r in splitter._get_applicable_ranges(
				top_level_ranges,
				3, 7)],
			[(0, 5), (5, 21)])

	def test_span1(self):
		splitter = HtmlSplitter(self.data)

		self.assertEqual(unicode(splitter.get_span(0, 5)),
			u"0abc4")
		self.assertEqual(unicode(splitter.get_span(5, 8)),
			u"<p><b><a>14d</a></b></p>")
		self.assertEqual(unicode(splitter.get_span(0, 9)),
			u"0abc4<p><b><a>14de</a></b></p>")
		self.assertEqual(unicode(splitter.get_span(2, 24)),
			u"bc4<p><b><a>14defg21</a></b>30hijk37</p>42m")

	def test_span2(self):
		splitter = HtmlSplitter("abcdefghijkl")
		self.assertEqual(unicode(splitter.get_span(2, 5)),
			u"cde")
		self.assertEqual(unicode(splitter.get_span(5, 12)),
			u"fghijkl")
		self.assertEqual(unicode(splitter.get_span(5, 13)),
			u"fghijkl")

	def test_span3(self):
		splitter = HtmlSplitter('<p class="blah">abcdefghijkl</p>')
		self.assertEqual(unicode(splitter.get_span(2, 5)),
			u'<p class="blah">cde</p>')
		self.assertEqual(unicode(splitter.get_span(5, 12)),
			u'<p class="blah">fghijkl</p>')


	def test_span4(self):
		splitter = HtmlSplitter('<p class="blah">abc<br/>def</p>ghi<br/>jkl<br/>')

		top_level_ranges = splitter._top_level_ranges
		self.assertEqual(
			[r["range"] for r in top_level_ranges],
			[(0, 6), (6, 9), (9, 9), (9, 12), (12, 12)])
		self.assertEqual(unicode(splitter.get_span(2, 5)),
			u'<p class="blah">c<br/>de</p>')
		self.assertEqual(unicode(splitter.get_span(3, 4)),
			u'<p class="blah">d</p>')
		self.assertEqual(unicode(splitter.get_span(5, 12)),
			u'<p class="blah">f</p>ghi<br/>jkl')