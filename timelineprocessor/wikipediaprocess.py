# -*- coding: UTF-8 -*-

import sys
import codecs
import re
import datetime
import json
import wikipedia
from bs4 import BeautifulSoup

import pdb

def jsonFromPage(title):
	"""Takes the title of a timeline page on Wikipedia and
	outputs it to a json file
	"""
	return json.dumps(extractTimeline(wikipedia.page(title)))

def getStringBlocks(html, 
	blockElements = set(["address", "article", "aside", "blockquote", "dd", "div", "dl", "p", "ol", "ul", "li"]),
	headerElements = set(["h2", "h3"])):
	"""Given an html element, returns a list of list of strings. Each section, demarcated
	by a headerElement is a list of strings. Each block element in html is a string.
	Empty lines are not retained.
	"""

	def closeStringBlock(sb, s):
		s = s.strip()
		if s:
			sb.append(s)

	def closeStringBlocks(sbs, sb, s):
		closeStringBlock(sb, s)
		if sb:
			sbs.append(sb)

	stringBlocks = []
	currStringBlock = []
	currString = ""
	for el in html.children:
		if el.name in headerElements:
			closeStringBlocks(stringBlocks, currStringBlock, currString)
			currStringBlock = []
		elif el.name in blockElements:
			closeStringBlock(currStringBlock, currString)
			currString = ""
			# assumes no header elements in child elements
			# TODO deal with headers better, and incorporate information
			childStringBlocks = getStringBlocks(el)
			if childStringBlocks:
				currStringBlock += childStringBlocks[0]
		else:
			currString += unicode(el)

	closeStringBlocks(stringBlocks, currStringBlock, currString)

	return stringBlocks


def stringsToEvents(stringBlocks):
	"""Given a set of sets of strings, returns a list of timeline events.
	Expects that all strings are non-empty"""

	currEvent = {}
	events = []

	lineBreak = "<br />"

	for stringBlock in stringBlocks:
		for string in stringBlock:
			extract = findDate(string)
			if extract:
				if currEvent:
					events.append(currEvent)
				currEvent = {"date": extract[0], "content": extract[1]}
			else:
				if currEvent:
					currEvent["content"] += lineBreak + string
	return events


def extractTimeline(page):
	"""Takes a timeline page from Wikipedia and turns it
	into ... something?

	page must be a wikipedia.WikipediaPage
	""" 

	article = BeautifulSoup(page.html())

	return stringsToEvents(getStringBlocks(article))

def getFirstPart(soup, remainder = []):
	"""Given an html string, returns (firstPart, remainder) where firstPart is the 
	"""
	try:
		if soup.contents:
			(firstPart, rem) = getFirstPart(soup.contents[0], soup.contents[1:])
			return (firstPart, rem + "".join(unicode(s) for s in remainder))
		else:
			return ("", "".join(unicode(s) for s in remainder))
	except AttributeError:
		return (soup, "".join(unicode(s) for s in remainder))

def findDate(string):
	"""Takes an html string, and returns (date, content) as a tuple.
	For now, date is an int that represents the year. Negative numbers are B.C. and positive are A.D. years
	"""

	soup = BeautifulSoup(string)
	(s, remainder) = getFirstPart(soup)

	# strip out all non-letter/digit characters from the beginning
	m = re.search('^[^\d\w]+', s)
	if m:
		s = s[m.end():]
	if not s:
		return None

	# find a date and store it in date
	# TODO should probably stop ignoring question marks and circa (c)

	date = None

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
	content = rem[m2.end():] + remainder

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
