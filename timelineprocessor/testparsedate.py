# -*- coding: UTF-8 -*-


from bs4 import BeautifulSoup
from parsedate import parse_date_html, TimelineDate
import parsedate
import unittest
import pdb
from pprint import pprint


class TestPossibleTexts(unittest.TestCase):
	def test_one(self):
		pprint(list(parsedate._possible_texts(u'1845 a.d. century ago')))
		pprint(list(parsedate._possible_texts(u'1845 march blah')))
		pprint(list(parsedate._possible_texts(u'1845 ma: march')))
		pprint(list(parsedate._possible_texts(u'2nd century b.c.')))
		pprint(list(parsedate._possible_texts(u'1967 - 12th street massacre')))


class TestParseDate(unittest.TestCase):
	def helper(self, data):
		for row in data:
			self.assertEqual(parse_date_html(row[0]), row[1])

	def test_misc(self):
		self.helper((
			(u'',								None),
			(u'  ',								None),
			(u'<p></p>',						None),
			(u'<p>  </p>',						None),
			(u'lkjdr3f',						None),
			(u'1967 - 12th street massacre',	(TimelineDate(1967, False),	u'1967', u'12th street massacre'))
		))

		self.assertEqual(parse_date_html(u'900–929')[0].simple_year,	900)


	def test_pure_dates(self):
		self.helper((
			(u'1245',				(TimelineDate(1245, False),		u'1245',			u'')),
			(u' 1245 ',				(TimelineDate(1245, False),		u'1245',			u'')),
			(u' 1245 hello',		(TimelineDate(1245, False),		u'1245',			u'hello')),
			(u'ca 1850 50',			(TimelineDate(1850, True),		u'ca 1850',			u'50')),
			(u'ca 70,000 BC',		(TimelineDate(-70000, True),	u'ca 70,000 BC',	u'')),
			(u'70,000 a.d.',		(TimelineDate(70000),			u'70,000 a.d.',		u'')),
			(u'c.a. 1850',			(TimelineDate(1850, True),		u'c.a. 1850',		u'')),
			(u'c. 1850 BC',			(TimelineDate(-1850, True),		u'c. 1850 BC',		u'')),
			(u'about 1850 BC',		(TimelineDate(-1850, True),		u'about 1850 BC',	u'')),
			(u'1850? b.c.e asdlkj',	(TimelineDate(-1850, True),		u'1850? b.c.e',		u'asdlkj')),
			(u'4 b.c.e c.e. c.e.',	(TimelineDate(-4, False),		u'4 b.c.e',			u'c.e. c.e.')),
			(u'4 AD blah',			(TimelineDate(4, False),		u'4 AD',			u'blah')),
			(u'4 cblah',			(TimelineDate(4, False),		u'4',				u'cblah')),
			(u'20 Mastodon',		(TimelineDate(20, False),		u'20',				u'Mastodon')),
		))


	def test_ranges(self):
		self.helper((
			(u'12 to 34 AD: blah',		(TimelineDate(12, False, 34, False),	u'12 to 34 AD',		u'blah')),
			(u'12 a.d. - 34 AD - blah',	(TimelineDate(12, False, 34, False),	u'12 a.d. - 34 AD',	u'blah')),
			(u'12   to   34:: blah',	(TimelineDate(12, False, 34, False),	u'12   to   34',	u'blah')),
			(u'12? bc—34 A.D    blah',	(TimelineDate(-12, True, 34, False),	u'12? bc—34 A.D',	u'blah')),
			(u'86 bc –c. 34 bc blah',	(TimelineDate(-86, False, -34, True),	u'86 bc –c. 34 bc',	u'blah')),
			(u'86 -   34 bc blah',		(TimelineDate(-86, False, -34, False),	u'86 -   34 bc',	u'blah')),
			(u'1819-23 blah',			(TimelineDate(1819, False, 1823, False),u'1819-23',			u'blah')),
		))


	def test_periods(self):
		self.helper((
			(u'2nd century b.c.',						(TimelineDate(-200, False, -100, False),	u'2nd century b.c.'							,u'')),
			(u'3rd century a.d.',						(TimelineDate(200, False, 300, False),		u'3rd century a.d.'							,u'')),
			(u'c. 2nd millenium b.c.',					(TimelineDate(-2000, True, -1000, True),	u'c. 2nd millenium b.c.'					,u'')),
			(u'16th century',							(TimelineDate(1500, False, 1600, False),	u'16th century'								,u'')),
			(u'22nd century',							(TimelineDate(2100, False, 2200, False),	u'22nd century'								,u'')),
			(u'c. 2nd millenium',						(TimelineDate(1000, True, 2000, True),		u'c. 2nd millenium'							,u'')),
			(u'8th to 19th century',					(TimelineDate(700, False, 1900, False),		u'8th to 19th century'						,u'')),
			(u'8th century to 19th century',			(TimelineDate(700, False, 1900, False),		u'8th century to 19th century'				,u'')),
			(u'8th century B.C. to 19th century A.D.',	(TimelineDate(-800, False, 1900, False),	u'8th century B.C. to 19th century A.D.'	,u'')),
			(u'12th to 3rd century b.c.',				(TimelineDate(-1200, False, -200, False),	u'12th to 3rd century b.c.'					,u'')),
			(u'12th century b.c. to 3rd century b.c.',	(TimelineDate(-1200, False, -200, False),	u'12th century b.c. to 3rd century b.c.'	,u'')),
		))


	def test_yearsago(self):
		self.helper((
			(u'12,345 years ago ago',	(TimelineDate(-12345),										u'12,345 years ago',u'ago')),
			(u'13,600 Ma',				(TimelineDate(-13600000000),								u'13,600 Ma',		u'')),
			(u'13,600-13,500 Ma',		(TimelineDate(-13600000000, False, -13500000000, False),	u'13,600-13,500 Ma',u'')),
			(u'c. 0.79 Ma',				(TimelineDate(-790000, True),								u'c. 0.79 Ma',		u'')),
			(u'15 ±0.3 Ma',				(TimelineDate(-15000000, 300000),							u'15 ±0.3 Ma',		u'')),
			(u'541 ±\xa00.3 Ma',		(TimelineDate(-541000000, 300000),							u'541 ±\xa00.3 Ma',	u'')),
			(u'25? Ma',					(TimelineDate(-25000000, True),								u'25? Ma',			u'')),
		))

		# This case should be fixed so that it works
		# ('.24 Ma', (TimelineDate(-240000), ''))
		

	def test_monthday(self):
		self.helper((
			(u'December 3 1980',			(TimelineDate(1980, month = 12, day = 3),	u'December 3 1980',	u'')),
			(u'June 30, 1923',				(TimelineDate(1923, month = 6, day = 30),	u'June 30, 1923',	u'')),
			(u'December 1980',				(TimelineDate(1980, month = 12),			u'December 1980',	u'')),
			(u'December',					(TimelineDate(month = 12),					u'December',		u'')),
			(u'23 March 1933 Adolf Hitler',	(TimelineDate(1933, month = 3, day = 23),	u'23 March 1933',	u'Adolf Hitler')),

			# these test the ambiguous resolution code
			(u'23 March blah',				(TimelineDate(month = 3, day = 23),			u'23 March',		u'blah')),
			(u'December 3',					(TimelineDate(month = 12, day = 3),			u'December 3',		u'')),
			# this should maybe just assume that 23 is part of the content, no?
			(u'3 December 23',				(TimelineDate(23, month = 12, day = 3),		u'3 December 23',	u'')),
		))

		# this will be problematic, but hopefully should not occur too often (month/day added to years between 0 and 31 AD without AD appelation)
		# '3 December 3'


	def test_html_parsing(self):
		h1 = u'1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a>'
		d1 = u'1890'
		r1 = u'<a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a>'

		h2 = u'<b>1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b>'
		d2 = u'<b>1890</b>'
		r2 = u'<b><a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b>'

		h3 = u'<p><b>1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b></p>'
		d3 = u'<p><b>1890</b></p>'
		r3 = u'<p><b><a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b></p>'

		h4 = u'<p><b>1890 <a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b>blergh</p>'
		d4 = u'<p><b>1890</b></p>'
		r4 = u'<p><b><a href="/wiki/Stop_sign" title="Stop sign">Stop sign</a></b>blergh</p>'
		
		self.assertEqual(parse_date_html(h1), (TimelineDate(1890, False), d1, r1))
		self.assertEqual(parse_date_html(h2), (TimelineDate(1890, False), d2, r2))
		self.assertEqual(parse_date_html(h3), (TimelineDate(1890, False), d3, r3))
		self.assertEqual(parse_date_html(h4), (TimelineDate(1890, False), d4, r4))

	def test_real_life(self):
		d1 = u"""<li>613 BC, July – A <a href="/wiki/Comet" title="Comet">Comet</a>, possibly <a href="/wiki/Comet_Halley" title="Comet Halley" class="mw-redirect">Comet Halley</a>, is recorded in <a href="/wiki/Spring_and_Autumn_Annals" title="Spring and Autumn Annals">Spring and Autumn Annals</a> by the Chinese</li>"""
		self.assertEqual(parse_date_html(d1)[0], TimelineDate(-613))