# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import re
from htmlsplitter import HtmlSplitter
from nltk import parse_cfg
from nltk.parse import BottomUpChartParser
import itertools


class TimelineDate:
	"""Represents either a year or a range of years. simple_year returns the
	best single number approximation of the time of the event
	"""

	def __init__(self, start_year,
		start_year_approx = False, end_year = None, end_year_approx = False):

		self.start_year = start_year
		self.start_year_approx = start_year_approx
		self.end_year = end_year
		self.end_year_approx = end_year_approx

		if end_year:
			self.simple_year = (end_year - start_year) / 2
		else:
			self.simple_year = start_year

	@classmethod
	def span_from_years(cls, a, b):
		return TimelineDate(a.start_year, a.start_year_approx,
			b.start_year, b.start_year_approx)

	def __eq__(self, other):
		return self.__dict__ == other.__dict__

	def __repr__(self):
		return "TimelineDate(%r, %r, %r, %r)" % \
			(self.start_year, self.start_year_approx, self.end_year, self.end_year_approx)


_date_regex = re.compile(ur'^(to|years|yrs|ago|[\dbcead\.\?\-–— ])+')

def parse_date_text(text):
	"""Parses a date from some text, returns (TimelineDate, index) where
	text[:index] is the text determined to be the date. If no date can be
	found, returns None. Assumes that date is at the beginning of the string
	with no superfluous characters.
	"""
	date_grammar = parse_cfg(u"""
		S -> DATE
		DATE -> R | YBC | YAD
		
		YBC -> YNE osp BC | YNQ osp BC
		YAD -> YNE osp AD | YNQ osp AD | YNE | YNQ

		YNE -> n | n n | n n n | n n n n | n n n n n
		YNQ -> YNE q | CA osp YNE
		CA -> c a | c
		YN -> YNE | YNQ

		BC -> b c | b c e
		AD -> a d | c e

		TO -> osp dash osp | sp to sp
		R -> YBC TO YBC | YN TO YBC | YBC TO YAD | YAD TO YAD

		b -> 'b' | 'b' x
		c -> 'c' | 'c' x
		e -> 'e' | 'e' x
		a -> 'a' | 'a' x
		d -> 'd' | 'd' x
		x -> '.'

		q -> '?'
		dash -> '-' | '–' | '—'
		to -> 't' 'o'
		n -> '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9'
		sp -> sp ' ' | ' '
		osp -> sp | 
		years -> 'y' 'e' 'a' 'r' 's' | 'y' 'r' 's' | 'y' 'r' 's' x
		ago -> 'a' 'g' 'o'
		""")
	date_parser = BottomUpChartParser(date_grammar)

	date_text = text.lower()
	m = _date_regex.search(date_text)
	if not m: return None
	date_text = m.group().strip()
	parse = None

	while True:
		parse = date_parser.parse(date_text)
		if parse:
			break
		else:
			# this is a pretty big hack. Really need the parser to expand the
			# matches as far as possible and return that
			if len(date_text) <= 1: return None
			m = _date_regex.search(date_text[:-2])
			if not m: return None
			date_text = m.group().strip()
	
	# these are all very closely tied to date_grammar
	def yne(yne):
		return int("".join(yne.leaves()))
	def ynq(ynq):
		return [yne(n) for n in ynq if n.node == "YNE"][0]
	def yn(yn):
		"""Returns (year, approx?)"""
		if yn[0].node == "YNE": return TimelineDate(yne(yn[0]), False)
		elif yn[0].node == "YNQ": return TimelineDate(ynq(yn[0]), True)
	def year(year):
		"""Assumes year is YBC or YAD. Returns (year, approx?) where BC years
		are negative"""
		if year[0].node == "YNE": (num, approx) = (yne(year[0]), False)
		elif year[0].node == "YNQ": (num, approx) = (ynq(year[0]), True)

		if year.node == "YBC": num = -num

		return TimelineDate(num, approx)
	def r(r):
		if r[0].node == "YN":
			first = yn(r[0])
			first = TimelineDate(-first.start_year, first.start_year_approx)
		else:
			first = year(r[0])
		return TimelineDate.span_from_years(first, year(r[2]))
	def date(date):
		if date[0].node == "R":
			return r(date[0])
		else:
			return year(date[0])

	return (date(parse[0]), len(date_text))


def parse_date_html(html_string):
	"""Takes a string that contains html, and returns (date, content) as a
	tuple. For now, date is an int that represents the year. Negative numbers
	are B.C. and positive are A.D. years. If there is no date that can be
	parsed, returns None.
	"""

	html_splitter = HtmlSplitter(html_string)
	s = html_splitter.text_string

	content_offset = 0

	# strip out all non-letter/digit characters from the beginning
	m = re.search('^[^\d\w]+', s)
	if m:
		s = s[m.end():]
		content_offset += m.end()
	if not s:
		return None

	# get the date
	extract = parse_date_text(s)
	if not extract:
		return None
	(date, date_index) = extract
	content_offset += date_index

	# strip out any transition characters between the date and the content
	m = re.search(u'^[\s\-–—:\.]+', s[content_offset:])
	if m:
		content_offset += m.end()

	content = "" if content_offset >= len(s) \
		else html_splitter.get_span(content_offset, len(s))

	return (date, content)