# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import re
from htmlsplitter import HtmlSplitter
from nltk import parse_cfg
from nltk.parse import BottomUpChartParser
import itertools
import operator

import pdb


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
			# self.simple_year = (end_year - start_year) / 2 + start_year
			self.simple_year = start_year
		else:
			self.simple_year = start_year

	@classmethod
	def span_from_years(cls, a, b):
		return TimelineDate(a.start_year, a.start_year_approx,
			b.start_year, b.start_year_approx)

	@classmethod
	def span_from_dates(cls, a, b):
		years = [(y, a) for y, a in \
					[(a.start_year, a.start_year_approx),
					(a.end_year, a.end_year_approx),
					(b.start_year, b.start_year_approx),
					(b.end_year, b.end_year_approx)] \
				if y is not None]
		# in case of overlap, tighter approx should be taken
		min_year, min_approx = min(years, key=operator.itemgetter(0))
		max_year, max_approx = max(years, key=operator.itemgetter(0))
		return TimelineDate(min_year, min_approx, max_year, max_approx)

	def __neg__(self):
		return TimelineDate(-self.start_year,
			self.start_year_approx,
			-self.end_year if self.end_year else None,
			self.end_year_approx)

	def _basic_math(self, other, f):
		return TimelineDate(f(self.start_year, other),
			f(self.start_year_approx, other) if not isinstance(self.start_year_approx, bool) else self.start_year_approx,
			f(self.end_year, other) if self.end_year else None,
			f(self.end_year_approx, other) if not isinstance(self.end_year_approx, bool) else self.end_year_approx)

	def __mul__(self, other):
		return self._basic_math(other, operator.mul)

	def __add__(self, other):
		return self._basic_math(other, operator.add)

	def __sub__(self, other):
		return self._basic_math(other, operator.sub)

	def __eq__(self, other):
		return self.__dict__ == other.__dict__

	def __repr__(self):
		return 'TimelineDate(%r, %r, %r, %r)' % \
			(self.start_year, self.start_year_approx, self.end_year, self.end_year_approx)


_date_regex = re.compile(ur'^(millenium|millennium|th|st|nd|rd|century|ma|to|years|yrs|ago|[\dbcead,±\.\?\-–— ])+')

def parse_date_text(text):
	"""Parses a date from some text, returns (TimelineDate, index) where
	text[:index] is the text determined to be the date. If no date can be
	found, returns None. Assumes that date is at the beginning of the string
	with no superfluous characters.
	"""
	text = text.replace(u'\xa0', u' ')

	date_grammar = parse_cfg(u"""
		S -> DATE | YEARSAGO | DATERANGE

		YEARSAGO -> YAS | YAR | MAS | MAR

		YAS -> NUM osp years sp ago
		YAR -> NUM TO NUM osp years sp ago

		MAS -> DEC osp ma ago | DEC osp ma
		MAR -> DEC TO DEC ma ago | DEC TO DEC osp ma

		NUM -> NUME | NUMQ
		NUME -> NUMLEADGROUP NUMGROUPS
		NUMQ -> CA osp NUME | NUME q
		NUMLEADGROUP -> n | n n | n n n
		NUMGROUP -> NUMGROUPSEP n n n
		NUMGROUPSEP -> comma |
		NUMGROUPS -> NUMGROUPS NUMGROUP |

		DEC -> DECE | DECQ | DECQQ
		DECE -> NUME x NUME | NUME
		DECQ -> CA osp DECE | DECE q
		DECQQ -> DECE osp pm osp DECE


		DATE -> YBC | YAD | PERIODBC | PERIODAD
		
		YBC -> NUM osp BC
		PERIODBC -> PERIOD osp BC
		YAD -> NUM osp AD | NUM
		PERIODAD ->  PERIOD osp AD | PERIOD

		DATERANGE -> DATE TO DATE | NUM TO DATE | ORD TO DATE

		CA -> c a | c

		BC -> b c | b c e
		AD -> a d | c e

		TO -> osp dash osp | sp to sp

		PERIOD -> ORD osp century | ORD osp millenium
		ORD -> NUM th

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
		comma -> ','
		years -> 'y' 'e' 'a' 'r' 's' | 'y' 'r' 's' | 'y' 'r' 's' x
		ago -> 'a' 'g' 'o'
		ma -> 'm' 'a'
		pm -> '±'
		th -> 't' 'h' | 's' 't' | 'n' 'd' | 'r' 'd'
		century -> 'c' 'e' 'n' 't' 'u' 'r' 'y'
		millenium -> 'm' 'i' 'l' 'l' 'e' 'n' 'i' 'u' 'm' | 'm' 'i' 'l' 'l' 'e' 'n' 'n' 'i' 'u' 'm'
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
			m = _date_regex.search(date_text[:-1])
			if not m: return None
			date_text = m.group().strip()
	
	# these are all very closely tied to date_grammar
	def numetostring(nume):
		return ''.join(l for l in nume.leaves() if l.isdigit())
	def num(num):
		if num[0].node == 'NUME':
			return TimelineDate(int(numetostring(num[0])), False)
		elif num[0].node == 'NUMQ':
			return TimelineDate(
				[int(numetostring(n)) for n in num[0] if n.node == 'NUME'][0],
				True)
	def dece(dece):
		if len(dece) == 1: return int(numetostring(dece[0]))
		else: return float(numetostring(dece[0]) + '.' + numetostring(dece[2]))
	def dec(dec):
		if dec[0].node == 'DECE':
			return TimelineDate(dece(dec[0]), False)
		elif dec[0].node == 'DECQ':
			return TimelineDate([dece(n) for n in dec[0] if n.node == 'DECE'][0], True)
		elif dec[0].node == 'DECQQ':
			return TimelineDate(dece(dec[0][0]), dece(dec[0][4]))
	def period(period):
		isad = period.node == 'PERIODAD'

		n = num(period[0][0][0])
		if period[0][2].node == 'century': factor = 100
		elif period[0][2].node == 'millenium': factor = 1000

		if isad:
			return TimelineDate.span_from_years(n * factor - factor, n * factor)
		else:
			return TimelineDate.span_from_years(-n * factor, -n * factor + factor)
	def year(year):
		if year.node == 'YBC': return -num(year[0])
		elif year.node == 'YAD': return num(year[0])
	def _has_child_node(n, label):
		return [i for i, c in enumerate(n) if hasattr(c, 'node') and c.node == label]
	def daterange(r):
		if r[0].node == 'DATE' and r[0][0].node != 'YAD' and r[0][0].node != 'PERIODAD':
			first = date(r[0])
		else:
			# this if/else deals with interpretations of 12-34 b.c. as YAD TO YBC
			if r[0][0].node == 'YAD':
				replacement_node = r[0][0][0]
			elif r[0][0].node == 'PERIODAD':
				replacement_node = r[0][0][0][0]
			else:
				replacement_node = r[0]
			# replacement_node will always be a NUM or ORD we need to copy the
			# tree for the second part of the range and use that intepretation
			# on this ord/num
			first_mock = r[2].copy(True) #deepcopy
			parent = next(first_mock.subtrees(lambda t: _has_child_node(t, replacement_node.node)))
			parent[_has_child_node(parent, replacement_node.node)[0]] = replacement_node
			first = date(first_mock)

		return TimelineDate.span_from_dates(first, date(r[2]))
	def date(date):
		if date[0].node == 'YAD' or date[0].node == 'YBC':
			return year(date[0])
		elif date[0].node == 'PERIODAD' or date[0].node == 'PERIODBC':
			return period(date[0])
	def yearsago(yearsago):
		# not currently adjusting for the 2014 years since 0 A.D....
		if yearsago[0].node == 'YAS':
			return -num(yearsago[0][0])
		elif yearsago[0].node == 'YAR':
			return TimelineDate.span_from_years(-num(yearsago[0][0]), -num(yearsago[0][2]))
		elif yearsago[0].node == 'MAS':
			return -dec(yearsago[0][0]) * 1000000
		elif yearsago[0].node == 'MAR':
			return TimelineDate.span_from_years(-dec(yearsago[0][0]), -dec(yearsago[0][2])) * 1000000


	# pdb.set_trace()
	if parse[0].node == 'DATE':
		result = date(parse[0])
	elif parse[0].node == 'YEARSAGO':
		result = yearsago(parse[0])
	elif parse[0].node == 'DATERANGE':
		result = daterange(parse[0])
	return (result, len(date_text))


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
	date_string = html_splitter.get_span(0, date_index)

	# strip out any transition characters between the date and the content
	m = re.search(u'^[\s\-–—:\.]+', s[content_offset:])
	if m:
		content_offset += m.end()

	content = '' if content_offset >= len(s) \
		else html_splitter.get_span(content_offset, len(s))

	return (date, date_string, content)