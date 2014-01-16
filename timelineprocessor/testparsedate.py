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
		self.assertEqual(parse_date_html(u"86 bc –c. 34 bc blah"), (TimelineDate(-86, False, -34, True), "blah"))
		self.assertEqual(parse_date_html(u"86 -   34 bc blah"), (TimelineDate(-86, False, -34, False), "blah"))
		self.assertEqual(parse_date_html(u"lkjdr3f"), None)
		self.assertEqual(parse_date_html(u"900–929")[0].simple_year, 900)

	def test_periods(self):
		self.assertEqual(parse_date_html(u"2nd century b.c."), (TimelineDate(-200, False, -100, False), ""))
		self.assertEqual(parse_date_html(u"3rd century a.d."), (TimelineDate(200, False, 300, False), ""))
		self.assertEqual(parse_date_html(u"c. 2nd millenium b.c."), (TimelineDate(-2000, True, -1000, True), ""))
		self.assertEqual(parse_date_html(u"16th century"), (TimelineDate(1500, False, 1600, False), ""))
		self.assertEqual(parse_date_html(u"22nd century"), (TimelineDate(2100, False, 2200, False), ""))
		self.assertEqual(parse_date_html(u"c. 2nd millenium"), (TimelineDate(1000, True, 2000, True), ""))
		self.assertEqual(parse_date_html(u"8th to 19th century"), (TimelineDate(700, False, 1900, False), ""))
		self.assertEqual(parse_date_html(u"8th century to 19th century"), (TimelineDate(700, False, 1900, False), ""))
		self.assertEqual(parse_date_html(u"8th century B.C. to 19th century A.D."), (TimelineDate(-800, False, 1900, False), ""))
		self.assertEqual(parse_date_html(u"12th to 3rd century b.c."), (TimelineDate(-1200, False, -200, False), ""))
		self.assertEqual(parse_date_html(u"12th century b.c. to 3rd century b.c."), (TimelineDate(-1200, False, -200, False), ""))

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