# -*- coding: UTF-8 -*-
from bs4 import BeautifulSoup
import re
from htmlsplitter import HtmlSplitter
from dategrammar import date_grammar_string, date_grammar_words, date_valid_nonwords_re_string, date_valid_end_char
from nltk import parse_cfg
from nltk.parse import BottomUpChartParser
import itertools
import operator
import warnings
import copy

import pdb


class TimePoint:
	"""Represents a point in time"""
	def __init__(self, year = None, month = None, day = None, year_approx = False):
		self.year = year
		self.month = month
		self.day = day
		self.year_approx = year_approx

	def __neg__(self):
		return TimePoint(-self.year, self.month, self.day, self.year_approx)

	def _basic_math(self, other, f):
		return TimePoint(f(self.year, other),
			self.month,
			self.day,
			f(self.year_approx, other) \
				if not isinstance(self.year_approx, bool)
				else self.year_approx
			)
	# scalar mul/add/sub
	def __mul__(self, other):
		return self._basic_math(other, operator.mul)
	def __add__(self, other):
		return self._basic_math(other, operator.add)
	def __sub__(self, other):
		return self._basic_math(other, operator.sub)
	# comparison with other TimePoints
	def __eq__(self, other):
		return self.__dict__ == other.__dict__
	def __lt__(self, other):
		if self.year != other.year or not self.month or not other.month:
			return self.year < other.year
		elif self.month != other.month or not self.day or not other.day:
			return self.month < other.month
		else:
			return self.day < other.day

	def __repr__(self):
		return 'TimePoint(%r, %r, %r, %r)' % \
			(self.year, self.month, self.day, self.year_approx)

	@classmethod
	def combine(cls, a, b):
		"""Given TimePoints a and b, returns a new TimePoint that self takes
		on b's attributes, except if b does not have that attribute, in which
		case a's are taken."""
		if b.year:
			year = b.year
			year_approx = b.year_approx
		else:
			year = a.year
			year_approx = a.year_approx
		if b.month: month = b.month
		else: month = a.month
		if b.day: day = b.day
		else: day = a.day
		return cls(year, month, day, year_approx = year_approx)

class TimelineDate:
	"""Represents either a year or a range of years. simple_year returns the
	best single number approximation of the time of the event
	"""

	def __init__(self, start, end = None):
		self.start = start
		self.end = end

		self.simple_year = start.year

	@classmethod
	def span_from_dates(cls, a, b):
		years = [y for y in [a.start, a.end, b.start, b.end] \
				if y is not None]
		# in case of overlap, tighter approx should be taken
		return TimelineDate(min(years), max(years))

	@classmethod
	def combine(cls, a, b):
		"""Given two TimelineDates a and b, returns a new TimelineDate. The
		result's start will be a's start combined with b's start and the
		result's end will be a's end combined with b's end. (It doesn't really
		make sense for a to have an end, but we're not going to deal with that
		here.)

		The only exception is that if a and b both do not have ends, and a has
		year and month but not day and b has only year and self, and its value
		for year is between 1 and 31 the result will be combining a with b but
		interpreting b to only have a day value."""
		if not a.end and not b.end \
			and a.start.year and a.start.month and not a.start.day \
			and b.start.year and not b.start.month and not b.start.day \
			and b.start.year >= 1 and b.start.year <= 31:

			return cls(TimePoint(a.start.year, a.start.month, b.start.year, a.start.year_approx))
		else:
			start = TimePoint.combine(a.start, b.start)
			end = None
			if b.end: end = TimePoint.combine(a.start, b.end)

			return cls(start, end)


	def __eq__(self, other):
		return self.__dict__ == other.__dict__
	def __repr__(self):
		return 'TimelineDate(%r, %r)' % (self.start, self.end)


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
		parses = date_parser.nbest_parse(date_text)
		if parses:
			break

	if not parses:
		return None
	
	# these are all very closely tied to date_grammar
	def numstr(nume): # returns string of digits
		return ''.join(l for l in nume.leaves() if l.isdigit())
	def month(month): # returns TimePoint
		return TimePoint(month = month_to_num(month[0].node))
	def monthday(monthday): # returns TimePoint
		d = None
		for n in monthday:
			if n.node == 'DAY':
				d = int(numstr(n))
			elif n.node == 'MONTH':
				m = month(n)
		m.day = d
		return m
	def num(num): # returns TimePoint
		if num[0].node == 'NUME':
			return TimePoint(int(numstr(num[0])))
		elif num[0].node == 'NUMQ':
			return TimePoint(
				[int(numstr(n)) for n in num[0] if n.node == 'NUME'][0],
				year_approx = True)
	def dece(dece): # returns number
		if len(dece) == 1: return int(numstr(dece[0]))
		else: return float(numstr(dece[0]) + '.' + numstr(dece[2]))
	def dec(dec): # returns TimePoint
		if dec[0].node == 'DECE':
			return TimePoint(dece(dec[0]))
		elif dec[0].node == 'DECQ':
			return TimePoint([dece(n) for n in dec[0] if n.node == 'DECE'][0], year_approx = True)
		elif dec[0].node == 'DECQQ':
			return TimePoint(dece(dec[0][0]), year_approx = dece(dec[0][4]))
	def period(period): # returns TimelineDate
		isad = period.node == 'PERIODAD'

		n = num(period[0][0][0])
		if period[0][2].node == 'century': factor = 100
		elif period[0][2].node == 'millenium': factor = 1000

		if isad:
			return TimelineDate(n * factor - factor, n * factor)
		else:
			return TimelineDate(-n * factor, -n * factor + factor)
	def yadyymymd(yad): # returns TimePoint
		# name stands for year AD: year, year month, year month day
		monthtp = None
		daynum = None
		for s in yad.subtrees():
			if s.node == 'NUM':
				yeartp = num(s)
			elif s.node == 'MONTH':
				monthtp = month(s)
			elif s.node == 'DAY':
				daynum = int(numstr(s))
		if monthtp: yeartp.month = monthtp.month
		if daynum != None: yeartp.day = daynum
		return yeartp
	def year(year): # returns TimePoint
		if year.node == 'YBC': return -num(year[0])
		elif year.node == 'YAD': return yadyymymd(year)
	def _has_child_node(n, label):
		return [i for i, c in enumerate(n) if hasattr(c, 'node') and c.node == label]
	def daterange(r): # returns TimelineDate
		if r[0][0].node == 'YAD' and r[2][0].node == 'YAD':
			# for cases like 1832-34. gets parsed as YAD to YAD, but we need
			# to modify the second node
			first = date(r[0])
			second = date(r[2])
			first_str = str(first.start.year)
			second_str = str(second.start.year)
			if len(second_str) < len(first_str):
				second.start.year = int(
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
	def date(date): # returns TimelineDate
		if date[0].node == 'YAD' or date[0].node == 'YBC':
			return TimelineDate(year(date[0]))
		elif date[0].node == 'PERIODAD' or date[0].node == 'PERIODBC':
			return period(date[0])
	def yearsago(yearsago): # returns TimelineDate
		# not currently adjusting for the 2014 years since 0 A.D....
		if yearsago[0].node == 'YAS':
			return TimelineDate(-num(yearsago[0][0]))
		elif yearsago[0].node == 'YAR':
			return TimelineDate(-num(yearsago[0][0]), -num(yearsago[0][2]))
		elif yearsago[0].node == 'MAS':
			return TimelineDate(-dec(yearsago[0][0]) * 1000000)
		elif yearsago[0].node == 'MAR':
			return TimelineDate(-dec(yearsago[0][0]) * 1000000, -dec(yearsago[0][2]) * 1000000)
	def monthdayrange(r): # returns TimelineDate
		second = None
		if r[2].node == 'MONTHDAY':
			second = monthday(r[2])
		elif r[2].node == 'YADYEARMONTH' or r[2].node == 'YADYEARMONTHDAY':
			second = yadyymymd(r[2])

		if r[0].node == 'DAY':
			first = TimePoint(second.year, second.month, int(numstr(r[0])), year_approx = second.year_approx)
		elif r[0].node == 'MONTH':
			first = TimePoint(second.year, month(r[0]).month, year_approx = second.year_approx)
		elif r[0].node == 'MONTHDAY':
			temp = monthday(r[0])
			first = TimePoint(second.year, temp.month, temp.day, year_approx = second.year_approx)
		return TimelineDate(first, second)
	def monthdayyearrange(r): # returns TimelineDate
		yeartp = yadyymymd(r[4])
		monthdaytp = monthday(r[0])
		return TimelineDate(
			TimePoint(yeartp.year, monthdaytp.month, monthdaytp.day, year_approx = yeartp.year_approx),
			TimePoint(yeartp.year, monthdaytp.month, int(numstr(r[2])), year_approx = yeartp.year_approx))



	parse = None
	if len(parses) > 1:
		# ambiguous parses will fall into 3 categories
		# 1. DATE/MONTHDAY ambiguity
		# for a string like December 3:
		#	MONTHDAY (prefer)
		#	DATE -> YAD -> YADYEARMONTH
		# or 3 December
		#
		# 2. DATERANGE/MONTHDAYRANGE ambiguity
		# for a string like 6 June - 3 October 2013
		#	MONTHDAYRANGE -> MONTHDAY TO DATE (prefer)
		#	DATERANGE -> DATE TO DATE -> YAD TO YAD -> YADYEARMONTH TO YADYEARMONTHDAY
		# (this is almost the same thing as problem 1)
		#
		# The other category is something like 3 December 4
		#	YADYEARMONTHDAY -> MONTHDAY ocommadotsp YADYEAR (prefer)
		#	YADYEARMONTHDAY -> YADYEAR ocommadotsp MONTHDAY
		# this should be extremely rare, and we will not bother dealing with these issues
		# this can also happen in DATERANGE

		temp = [p for p in parses if p[0].node == 'MONTHDAY']
		if len(temp) == 1:
			parse = temp[0]
		if not parse:
			temp = [p for p in parses if p[0].node == 'MONTHDAYRANGE']
			if len(temp) == 1:
				parse = temp[0]
		if not parse:
			pdb.set_trace()
			warnings.warn('not sure how to decide between multiple parses %s' % date_text)
			parse = parses[0]
	else:
		parse = parses[0]


	if parse[0].node == 'DATE':
		result = date(parse[0])
	elif parse[0].node == 'YEARSAGO':
		result = yearsago(parse[0])
	elif parse[0].node == 'DATERANGE':
		result = daterange(parse[0])
	elif parse[0].node == 'MONTH':
		result = TimelineDate(month(parse[0]))
	elif parse[0].node == 'MONTHDAY':
		result = TimelineDate(monthday(parse[0]))
	elif parse[0].node == 'MONTHDAYRANGE':
		result = monthdayrange(parse[0])
	elif parse[0].node == 'MONTHDAYYEARRANGE':
		result = monthdayyearrange(parse[0])
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