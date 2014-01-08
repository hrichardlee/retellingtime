# -*- coding: UTF-8 -*-

import sys
import codecs
import re
import datetime
import json
import wikipedia
from bs4 import BeautifulSoup

def jsonFromPage(title):
	"""Takes the title of a timeline page on Wikipedia and
	outputs it to a json file
	"""
	return json.dumps(extractTimeline(wikipedia.page(title)))

def extractTimeline(page):
	"""Takes a timeline page from Wikipedia and turns it
	into ... something?

	page must be a wikipedia.WikipediaPage
	"""

	structuredData = []
	article = BeautifulSoup(page.html())

	# heading keeps track of the headings for the current context
	heading = []
	ignoreSection = False
	for el in article.children:
		if el.name == 'h2':
			heading = [el.find(class_='mw-headline').text]
			ignoreSection = heading[0] == 'See also'
		elif el.name == 'h3' and not ignoreSection:
			heading = heading[0:1]
			heading.append(el.find(class_='mw-headline').text)
		# for now, assume that timelines always require bullet points
		elif el.name == 'ul' and not ignoreSection:
			for li in el.children:
				if li.name == 'li':
					# hack for getting the Html
					data = findDate("".join(unicode(x) for x in li.contents))
					if data:
						(date, content) = data
						structuredData.append({'date': date, 'content': content, 'importance': importanceString(content)})

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
		m = re.search('^(\d{1,4})\?? ?(-|ΓÇô|ΓÇö|to) ?(\d{1,4})\??', s)
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
	m2 = re.search(u'^[c\s\-ΓÇôΓÇö:\.]+', rem)
	content = rem[m2.end():]

	return (date, content)

def importanceString(s):
	"""Given a content string for a timeline item, returns the importance score
	"""

	imp = 0
	n = 0
	# get all the links
	for a in BeautifulSoup(s).find_all('a'):
		if a['href'].startswith('/wiki/'):
			imp += importancePage(wikipedia.page(a['title'], auto_suggest=False))
			n += 1

	return float(imp) / float(n)

def importancePage(p):
	"""Given a wikipedia.WikipediaPage, returns the importance score
	"""
	return len(p.content)
	#return (p.backlinkCount(), len(p.content), p.revCount())

# TODO: add a relevance metric so that an entry like
# 	1815 - [[William Prout]] [[hypothesizes]] that all matter is built up from [[hydrogen]], adumbrating the [[proton]]
# in the timeline of particle physics doesn't get importance points
# for "hypothesizes", as this doesn't have much to do with particle physics
