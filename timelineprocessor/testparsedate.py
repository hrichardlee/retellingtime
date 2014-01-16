# -*- coding: UTF-8 -*-


from bs4 import BeautifulSoup
from parsedate import parse_date_html, TimelineDate
import unittest
import pdb
from pprint import pprint


class TestParseDate(unittest.TestCase):
	def test_pure_dates(self):
		self.assertEqual(parse_date_html("ca 1850 50"), (TimelineDate(1850, True), "50"))
		self.assertEqual(parse_date_html("ca 70,000 BC"), (TimelineDate(-70000, True), ""))
		self.assertEqual(parse_date_html("70,000 a.d."), (TimelineDate(70000), ""))
		self.assertEqual(parse_date_html("c.a. 1850"), (TimelineDate(1850, True), ""))
		self.assertEqual(parse_date_html("c. 1850 BC"), (TimelineDate(-1850, True), ""))
		self.assertEqual(parse_date_html("1850? b.c.e asdlkj"), (TimelineDate(-1850, True), "asdlkj"))
		self.assertEqual(parse_date_html("4 b.c.e c.e. c.e."), (TimelineDate(-4, False), "c.e. c.e."))
		self.assertEqual(parse_date_html("4 AD blah"), (TimelineDate(4, False), "blah"))
		self.assertEqual(parse_date_html("4 cblah"), (TimelineDate(4, False), "cblah"))
		self.assertEqual(parse_date_html("12 to 34 AD: blah"), (TimelineDate(12, False, 34, False), "blah"))
		self.assertEqual(parse_date_html("12 a.d. - 34 AD - blah"), (TimelineDate(12, False, 34, False), "blah"))
		self.assertEqual(parse_date_html(u"12   to   34:: blah"), (TimelineDate(12, False, 34, False), "blah"))
		self.assertEqual(parse_date_html(u"12? bc—34 A.D    blah"), (TimelineDate(-12, True, 34, False), "blah"))
		self.assertEqual(parse_date_html(u"12 bc –c. 34 bc blah"), (TimelineDate(-12, False, -34, True), "blah"))
		self.assertEqual(parse_date_html(u"12 -   34 bc blah"), (TimelineDate(-12, False, -34, False), "blah"))
		self.assertEqual(parse_date_html(u"lkjdr3f"), None)
		self.assertEqual(parse_date_html(u"900–929")[0].simple_year, 914)

	def test_yearsago(self):
		self.assertEqual(parse_date_html("12,345 years ago ago"), (TimelineDate(-12345), "ago"))
		self.assertEqual(parse_date_html("13,600 Ma"), (TimelineDate(-13600000000), ""))
		self.assertEqual(parse_date_html("13,600-13,500 Ma"), (TimelineDate(-13600000000, False, -13500000000, False), ""))
		self.assertEqual(parse_date_html("c. 0.79 Ma"), (TimelineDate(-790000, True), ""))
		self.assertEqual(parse_date_html("15 ±0.3 Ma"), (TimelineDate(-15000000, 300000), ""))
		# This case should be fixed so that it works
		# self.assertEqual(parse_date_html(".24 Ma"), (TimelineDate(-240000), ""))
		self.assertEqual(parse_date_html("25? Ma"), (TimelineDate(-25000000, True), ""))
		

	def test_html_parsing(self):
		h1 = '1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a>'
		r1 = '<a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a>'
		h2 = '<b>1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b>'
		r2 = '<b><a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b>'
		h3 = '<p><b>1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b></p>'
		r3 = '<p><b><a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b></p>'
		h4 = '<p><b>1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b>blergh</p>'
		r4 = '<p><b><a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b>blergh</p>'
		
		self.assertEqual(parse_date_html(h1), (TimelineDate(1890, False), r1))
		self.assertEqual(parse_date_html(h2), (TimelineDate(1890, False), r2))
		self.assertEqual(parse_date_html(h3), (TimelineDate(1890, False), r3))
		self.assertEqual(parse_date_html(h4), (TimelineDate(1890, False), r4))