# -*- coding: UTF-8 -*-


from bs4 import BeautifulSoup
from parsedate import parse_date_html, TimelineDate, TimePoint
import parsedate
import warnings
import unittest
import pdb
from pprint import pprint


class TestCombine(unittest.TestCase):
	def test_one(self):
		print(TimePoint.combine(TimePoint(1920, 4), TimePoint(None, 5, 3)))
		print(TimePoint.combine(TimePoint(1920), TimePoint(None, 4)))
		print(TimelineDate.combine(TimelineDate(TimePoint(1920, 8)), TimelineDate(TimePoint(4))))


class TestPossibleTexts(unittest.TestCase):
	def test_one(self):
		pprint(list(parsedate._possible_texts(u'1845 a.d. century ago')))
		pprint(list(parsedate._possible_texts(u'1845 march blah')))
		pprint(list(parsedate._possible_texts(u'1845 ma: march')))
		pprint(list(parsedate._possible_texts(u'2nd century b.c.')))
		pprint(list(parsedate._possible_texts(u'1967 - 12th street massacre')))


class TestParseDate(unittest.TestCase):
	def helper(self, data):
		warnings.filterwarnings('ignore', module='bs4')
		for row in data:
			self.assertEqual(parse_date_html(row[0]), row[1])

	def test_misc(self):
		self.helper((
			(u'',								None),
			(u'  ',								None),
			(u'<p></p>',						None),
			(u'<p>  </p>',						None),
			(u'lkjdr3f',						None),
			(u'1967 - 12th street massacre',	(TimelineDate(TimePoint(1967, year_approx = False)),	u'1967', u'12th street massacre')),
		))

		self.assertEqual(parse_date_html(u'900–929')[0].simple_year(),	900)


	def test_pure_dates(self):
		self.helper((
			(u'1245',				(TimelineDate(TimePoint(1245)),							u'1245',			u'')),
			(u'AD1245',				(TimelineDate(TimePoint(1245)),							u'AD1245',			u'')),
			(u' 1245 ',				(TimelineDate(TimePoint(1245)),							u'1245',			u'')),
			(u' 1245 hello',		(TimelineDate(TimePoint(1245)),							u'1245',			u'hello')),
			(u'ca 1850 50',			(TimelineDate(TimePoint(1850, year_approx = True)),		u'ca 1850',			u'50')),
			(u'ca 70,000 BC',		(TimelineDate(TimePoint(-70000, year_approx = True)),	u'ca 70,000 BC',	u'')),
			(u'70,000 a.d.',		(TimelineDate(TimePoint(70000)),						u'70,000 a.d.',		u'')),
			(u'c.a. 1850',			(TimelineDate(TimePoint(1850, year_approx = True)),		u'c.a. 1850',		u'')),
			(u'c. 1850 BC',			(TimelineDate(TimePoint(-1850, year_approx = True)),	u'c. 1850 BC',		u'')),
			(u'about 1850 BC',		(TimelineDate(TimePoint(-1850, year_approx = True)),	u'about 1850 BC',	u'')),
			(u'1850? b.c.e asdlkj',	(TimelineDate(TimePoint(-1850, year_approx = True)),	u'1850? b.c.e',		u'asdlkj')),
			(u'4 b.c.e c.e. c.e.',	(TimelineDate(TimePoint(-4)),							u'4 b.c.e',			u'c.e. c.e.')),
			(u'4 AD blah',			(TimelineDate(TimePoint(4)),							u'4 AD',			u'blah')),
			(u'4 cblah',			(TimelineDate(TimePoint(4)),							u'4',				u'cblah')),
			(u'20 Mastodon',		(TimelineDate(TimePoint(20)),							u'20',				u'Mastodon')),
		))


	def test_ranges(self):
		self.helper((
			(u'12 to 34 AD: blah',		(TimelineDate(TimePoint(12),						TimePoint(34)),							u'12 to 34 AD',		u'blah')),
			(u'12 a.d. - 34 AD - blah',	(TimelineDate(TimePoint(12),						TimePoint(34)),							u'12 a.d. - 34 AD',	u'blah')),
			(u'12   to   34:: blah',	(TimelineDate(TimePoint(12),						TimePoint(34)),							u'12   to   34',	u'blah')),
			(u'12? bc—34 A.D    blah',	(TimelineDate(TimePoint(-12, year_approx = True),	TimePoint(34)),							u'12? bc—34 A.D',	u'blah')),
			(u'86 bc –c. 34 bc blah',	(TimelineDate(TimePoint(-86),						TimePoint(-34, year_approx = True)),	u'86 bc –c. 34 bc',	u'blah')),
			(u'86 -   34 bc blah',		(TimelineDate(TimePoint(-86),						TimePoint(-34)),						u'86 -   34 bc',	u'blah')),
			(u'1819-23 blah',			(TimelineDate(TimePoint(1819),						TimePoint(1823)),						u'1819-23',			u'blah')),
		))


	def test_periods(self):
		self.helper((
			(u'2nd century b.c.',						(TimelineDate(TimePoint(-200),						TimePoint(-100)),						u'2nd century b.c.'							,u'')),
			(u'3rd century a.d.',						(TimelineDate(TimePoint(200),						TimePoint(300)),						u'3rd century a.d.'							,u'')),
			(u'c. 2nd millenium b.c.',					(TimelineDate(TimePoint(-2000, year_approx = True),	TimePoint(-1000, year_approx = True)),	u'c. 2nd millenium b.c.'					,u'')),
			(u'16th century',							(TimelineDate(TimePoint(1500),						TimePoint(1600)),						u'16th century'								,u'')),
			(u'22nd century',							(TimelineDate(TimePoint(2100),						TimePoint(2200)),						u'22nd century'								,u'')),
			(u'c. 2nd millenium',						(TimelineDate(TimePoint(1000, year_approx = True),	TimePoint(2000, year_approx = True)),	u'c. 2nd millenium'							,u'')),
			(u'8th to 19th century',					(TimelineDate(TimePoint(700),						TimePoint(1900)),						u'8th to 19th century'						,u'')),
			(u'8th century to 19th century',			(TimelineDate(TimePoint(700),						TimePoint(1900)),						u'8th century to 19th century'				,u'')),
			(u'8th century B.C. to 19th century A.D.',	(TimelineDate(TimePoint(-800),						TimePoint(1900)),						u'8th century B.C. to 19th century A.D.'	,u'')),
			(u'12th to 3rd century b.c.',				(TimelineDate(TimePoint(-1200),						TimePoint(-200)),						u'12th to 3rd century b.c.'					,u'')),
			(u'12th century b.c. to 3rd century b.c.',	(TimelineDate(TimePoint(-1200),						TimePoint(-200)),						u'12th century b.c. to 3rd century b.c.'	,u'')),
		))


	def test_yearsago(self):
		self.helper((
			(u'12,345 years ago ago',	(TimelineDate(TimePoint(-12345)),								u'12,345 years ago',u'ago')),
			(u'12,345 BP',				(TimelineDate(TimePoint(-12345)),								u'12,345 BP',		u'')),
			(u'13,600-13,500 BP',		(TimelineDate(TimePoint(-13600), TimePoint(-13500)),			u'13,600-13,500 BP',u'')),
			(u'20 ka',					(TimelineDate(TimePoint(-20000)),								u'20 ka',			u'')),
			(u'13-8 ka',				(TimelineDate(TimePoint(-13000), TimePoint(-8000)),				u'13-8 ka',u'')),
			(u'13,600 Ma',				(TimelineDate(TimePoint(-13600000000)),							u'13,600 Ma',		u'')),
			(u'13,600-13,500 Ma',		(TimelineDate(TimePoint(-13600000000), TimePoint(-13500000000)),u'13,600-13,500 Ma',u'')),
			(u'c. 0.79 Ma',				(TimelineDate(TimePoint(-790000, year_approx = True)),			u'c. 0.79 Ma',		u'')),
			(u'15 ±0.3 Ma',				(TimelineDate(TimePoint(-15000000, year_approx = 300000)),		u'15 ±0.3 Ma',		u'')),
			(u'541 ±\xa00.3 Ma',		(TimelineDate(TimePoint(-541000000, year_approx = 300000)),		u'541 ±\xa00.3 Ma',	u'')),
			(u'25? Ma',					(TimelineDate(TimePoint(-25000000, year_approx = True)),		u'25? Ma',			u'')),
		))

		# This case should be fixed so that it works
		# ('.24 Ma', (TimelineDate(-240000), ''))
		

	def test_monthday(self):
		self.helper((
			(u'December 3 1980',			(TimelineDate(TimePoint(1980, 12, 3)),			u'December 3 1980',	u'')),
			(u'June 30, 1923',				(TimelineDate(TimePoint(1923, 6, 30)),			u'June 30, 1923',	u'')),
			(u'December 1980',				(TimelineDate(TimePoint(1980, 12)),				u'December 1980',	u'')),
			(u'December',					(TimelineDate(TimePoint(month = 12)),			u'December',		u'')),
			(u'23 March 1933 Adolf Hitler',	(TimelineDate(TimePoint(1933, 3, 23)),			u'23 March 1933',	u'Adolf Hitler')),

			# these test the ambiguous resolution code
			(u'23 March blah',				(TimelineDate(TimePoint(month = 3, day = 23)),	u'23 March',		u'blah')),
			(u'December 3',					(TimelineDate(TimePoint(month = 12, day = 3)),	u'December 3',		u'')),

			# this decision is made arbitrarily by the parser. we're just not going to worry about it
			# (u'3 December 23',				(TimelineDate(3, month = 12, day = 23)),		u'3 December 23',	u'')),
		))

	def test_monthday_ranges(self):
		self.helper((
			(u'16 June - 9 July 1932 blah',	(TimelineDate(TimePoint(1932, 6, 16),	TimePoint(1932, 7, 9)),	u'16 June - 9 July 1932', u'blah')),
			(u'16 June - 9 July, 1932',		(TimelineDate(TimePoint(1932, 6, 16),	TimePoint(1932, 7, 9)),	u'16 June - 9 July, 1932', u'')),
			(u'16 June - July 9 1932',		(TimelineDate(TimePoint(1932, 6, 16),	TimePoint(1932, 7, 9)),	u'16 June - July 9 1932', u'')),
			(u'June 16 - July 9 27',		(TimelineDate(TimePoint(None, 6, 16),		TimePoint(None, 7, 9)),	u'June 16 - July 9', u'27')),
			(u'June - 9 July 1932',			(TimelineDate(TimePoint(1932, 6),		TimePoint(1932, 7, 9)),	u'June - 9 July 1932', u'')),
			(u'16 June - July 1932',		(TimelineDate(TimePoint(1932, 6, 16),	TimePoint(1932, 7)),	u'16 June - July 1932', u'')),
			(u'June - July 1932',			(TimelineDate(TimePoint(1932, 6),		TimePoint(1932, 7)),	u'June - July 1932', u'')),
			(u'6 - 8 July 1932',			(TimelineDate(TimePoint(1932, 7, 6),	TimePoint(1932, 7, 8)),	u'6 - 8 July 1932', u'')),
			(u'June 6 - 8, 1932',			(TimelineDate(TimePoint(1932, 6, 6),	TimePoint(1932, 6, 8)),	u'June 6 - 8, 1932', u'')),
			(u'Nov. 15 - 173 prisoners',	(TimelineDate(TimePoint(None, 11, 15)),							u'Nov. 15', u'173 prisoners')),
		))
		


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
		
		self.assertEqual(parse_date_html(h1), (TimelineDate(TimePoint(1890)), d1, r1))
		self.assertEqual(parse_date_html(h2), (TimelineDate(TimePoint(1890)), d2, r2))
		self.assertEqual(parse_date_html(h3), (TimelineDate(TimePoint(1890)), d3, r3))
		self.assertEqual(parse_date_html(h4), (TimelineDate(TimePoint(1890)), d4, r4))

	def test_real_life(self):
		d1 = u"""<li>613 BC, July – A <a href="/wiki/Comet" title="Comet">Comet</a>, possibly <a href="/wiki/Comet_Halley" title="Comet Halley" class="mw-redirect">Comet Halley</a>, is recorded in <a href="/wiki/Spring_and_Autumn_Annals" title="Spring and Autumn Annals">Spring and Autumn Annals</a> by the Chinese</li>"""
		self.assertEqual(parse_date_html(d1)[0], TimelineDate(TimePoint(-613)))