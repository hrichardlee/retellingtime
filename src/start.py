# -*- coding: UTF-8 -*-

import sys
import codecs
import re
import datetime
import wikipedia
from bs4 import BeautifulSoup


def timelinePageToStructuredData(page):
	"""Takes a timeline page from Wikipedia and turns it
	into ... something?

	page must be a wikipedia.WikipediaPage
	"""

	structuredData = []
	article = BeautifulSoup(page.html())

	# heading keeps track of the headings for the current context
	heading = []
	for el in article.children:
		if el.name == 'h2':
			heading = [el.find(class_='mw-headline').text]
		elif el.name == 'h3':
			heading = heading[0:1]
			heading.append(el.find(class_='mw-headline').text)
		# for now, assume that timelines always require bullet points
		elif el.name == 'ul':
			for li in el.children:
				if li.name == 'li':
					data = findDate(li.text)
					if data:
						structuredData.append(data)
	return structuredData

def findDate(s):
	"""Takes a string, and returns (date, content) as a tuple.
	For now, date is an int that represents the year. Negative numbers are B.C. and positive are A.D. years
	"""

	date = None

	# strip out initial irrelevant characters
	# TODO should probably replace with stripping all non-word/digit chars
	s = s.strip()

	# find a date and store it in date
	# TODO should probably stop ignoring question marks and circa (c)

	# B.C. dates
	if date is None:
		m = re.search('^(\d{1,6}) [bB]\.?[cC]\.?', s)
		if m:
			rem = s[m.end():]
			date = (0 - int(m.groups()[0]))

	# just the year
	if date is None:
		m = re.search('^(\d{1,4})\?? ?(-|–|—|to) ?(\d{1,4})\??', s)
		if m:
			rem = s[m.end():]
			date = (int(m.groups()[0]), int(m.groups()[2]))

	# year range
	if date is None:
		m = re.search('^\d{1,4}\??', s)
		if m:
			rem = s[m.end():]
			date = int(m.group())

	if date is None:
		return None

	# strip out any transition characters between the date and the content
	# c stands for circa and is ignored for now
	m2 = re.search(u'^[c\s\-–—:\.]+', rem)
	content = rem[m2.end():]

	return (date, content)

def importance(s):
	"""Given a content string for a timeline item, returns the importance score
	"""

	