# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import re
from htmlsplitter import HtmlSplitter
from dategrammar import date_grammar_string, date_grammar_words, date_valid_nonwords_re_string, date_valid_end_char
from nltk import parse_cfg
from nltk.parse import BottomUpChartParser
import itertools
import operator

import pdb


class TimelineDate:
	"""Represents either a year or a range of years. simple_year returns the
	best single number approximation of the time of the event
	"""

	def __init__(self, start_year = None, start_year_approx = False,
		end_year = None, end_year_approx = False,
		month = None, day = None):

		self.month = month
		self.day = day

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

	def monthday_from(self, other):
		self.month = other.month
		self.day = other.day

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
		return 'TimelineDate(%r, %r, %r, %r, %r, %r)' % \
			(self.start_year, self.start_year_approx, self.end_year, self.end_year_approx, self.month, self.day)


def month_to_num(text):
	"""This takes a month node name as defined in the date grammar and
	converts it to a number"""
	months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
	return months.index(text) + 1


_splitter_re = re.compile(ur'([^a-zA-Z0-9]|\d+)')
_valid_nonwords_re = re.compile(date_valid_nonwords_re_string)
_date_grammar_words_set = set(date_grammar_words)
_whitespace_re = re.compile(ur'^\s+$')
_valid_end_char_re = re.compile(date_valid_end_char)

def _possible_texts(text):
	"""Given a string, returns a generator of strings which are all possible
	date_text strings for the given input, anchored at the first character"""
	# warning: this will only work as long as there are no cases where
	# concatenating multiple words in date_grammar_words could form another
	# valid word. ad/bc/ce/bce are an exception, they will work fine

	# this step is not particularly efficient, especially with long content,
	# but not worrying about it for now
	tokens = _splitter_re.split(text)
	# find the first token that cannot be part of a date string, and remove
	# that token and all subsequent tokens
	for i, t in enumerate(tokens):
		if _valid_nonwords_re.search(t) == None and t not in _date_grammar_words_set:
			tokens = tokens[:i]
			break
	prev_is_break_char = True
	# generate all possible strings	
	for i, t in reversed(list(enumerate(tokens))):
		if t and _whitespace_re.search(t) == None and prev_is_break_char:
			yield ''.join(tokens[:i + 1])
		if t:
			# this is to make sure we only end the date string on valid
			# characters
			prev_is_break_char = _valid_end_char_re.search(t[0]) != None
		# if t is an empty string, don't change prev_is_break_char


def parse_date_text(text):
	"""Parses a date from some text, returns (TimelineDate, index) where
	text[:index] is the text determined to be the date. If no date can be
	found, returns None. Assumes that date is at the beginning of the string
	with no superfluous characters.
	"""
	# replace non-breaking spaces
	text = text.replace(u'\xa0', u' ')
	text = text.lower()

	date_parser = BottomUpChartParser(parse_cfg(date_grammar_string))

	parses = []

	for date_text in _possible_texts(text):
		# parse = date_parser.parse(date_text)
		parses = date_parser.nbest_parse(date_text)
		if parses:
			break

	if not parses:
		return None
	
	# these are all very closely tied to date_grammar
	def numstr(nume):
		return ''.join(l for l in nume.leaves() if l.isdigit())

	def monthday(monthday):
		d = None
		for n in monthday:
			if n.node == 'DAY':
				d = int(numstr(n))
			elif n.node == 'MONTH':
				m = TimelineDate(month = month_to_num(n[0].node))
		m.day = d
		return m

	def num(num):
		if num[0].node == 'NUME':
			return TimelineDate(int(numstr(num[0])), False)
		elif num[0].node == 'NUMQ':
			return TimelineDate(
				[int(numstr(n)) for n in num[0] if n.node == 'NUME'][0],
				True)
	def dece(dece):
		if len(dece) == 1: return int(numstr(dece[0]))
		else: return float(numstr(dece[0]) + '.' + numstr(dece[2]))
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
		elif year.node == 'YAD':
			if year[0].node == 'MONTHDAYYEAR':
				mdynode = year[0]
			else:
				mdynode = year
			mddate = None
			for n in mdynode:
				if n.node == 'NUM': yeardate = num(n)
				elif n.node == 'MONTHDAY': mddate = monthday(n)
			if mddate: yeardate.monthday_from(mddate)
			return yeardate
	def _has_child_node(n, label):
		return [i for i, c in enumerate(n) if hasattr(c, 'node') and c.node == label]
	def daterange(r):
		if r[0][0].node == 'YAD' and r[2][0].node == 'YAD':
			# for cases like 1832-34. gets parsed as YAD to YAD, but we need
			# to modify the second node
			first = date(r[0])
			second = date(r[2])
			first_str = str(first.start_year)
			second_str = str(second.start_year)
			if len(second_str) < len(first_str):
				second.start_year = int(
					first_str[:len(first_str) - len(second_str)] + second_str)
		elif r[0].node == 'DATE' and r[0][0].node != 'YAD' and r[0][0].node != 'PERIODAD':
			# these cases should work without any modification to either node
			first = date(r[0])
			second = date(r[2])
		else:
			# for cases like 34-12 b.c. or 12 century to 10th century bc. Gets
			# parsed as YAD to YBC or NUM to YBC. replacement_node finds the
			# '34' in the AST for YAD, and puts it in the corresponding
			# location for a copy of the YBC ast. This gets us a fully
			# qualified date for '34' that we can use to create the range
			if r[0][0].node == 'YAD':
				replacement_node = r[0][0].subtrees(filter = lambda x: x.node == 'NUM').next()
			elif r[0][0].node == 'PERIODAD':
				replacement_node = r[0][0][0][0]
			elif r[0].node == 'ORD':
				replacement_node = r[0]
			else:
				raise RuntimeError('unexpected node type in date AST')
			# copy the second date's AST, replace, and get the date
			first_mock = r[2].copy(True) #deepcopy
			parent = next(first_mock.subtrees(lambda t: _has_child_node(t, replacement_node.node)))
			parent[_has_child_node(parent, replacement_node.node)[0]] = replacement_node
			first = date(first_mock)

			second = date(r[2])

		return TimelineDate.span_from_dates(first, second)
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

	parse = parses[0]

	if parse[0].node == 'DATE':
		result = date(parse[0])
	elif parse[0].node == 'YEARSAGO':
		result = yearsago(parse[0])
	elif parse[0].node == 'DATERANGE':
		result = daterange(parse[0])
	elif parse[0].node == 'MONTH':
		result = month(parse[0])
	elif parse[0].node == 'MONTHDAY':
		result = monthday(parse[0])
	return (result, len(date_text))


def parse_date_html(html_string):
	"""Takes a string that contains html, and returns (date, date_string,
	content) as a tuple. For now, date is an int that represents the year.
	Negative numbers are B.C. and positive are A.D. years. If there is no date
	that can be parsed, returns None.
	"""

	html_splitter = HtmlSplitter(html_string)
	s = html_splitter.text_string

	content_offset = 0

	# strip out all non-letter/digit characters from the beginning
	m = re.search('^[^\d\w]+', s)
	if m:
		content_offset += m.end()
	if not s:
		return None

	# get the date
	extract = parse_date_text(s[content_offset:])
	if not extract:
		return None
	(date, date_index) = extract
	date_string = html_splitter.get_span(content_offset, date_index + content_offset)

	content_offset += date_index

	# strip out any transition characters between the date and the content
	m = re.search(u'^[\s\-–—:\.]+', s[content_offset:])
	if m:
		content_offset += m.end()

	content = '' if content_offset >= len(s) \
		else html_splitter.get_span(content_offset, len(s))

	return (date, date_string, content)