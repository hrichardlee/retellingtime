# -*- coding: UTF-8 -*-

import sys
import codecs
import re
import datetime
import json
import wikipedia
from bs4 import BeautifulSoup

import pdb


def wpPageToJson(title):
	"""Takes the title of a timeline page on Wikipedia and outputs it to a
	json file
	"""
	article = BeautifulSoup(wikipedia.page(title).html())

	return json.dumps(stringBlocksToEvents(htmlToStringBlocks(article)))


def htmlToStringBlocks(html, 
	blockElements = set(["address", "article", "aside", "blockquote", "section", "dd", "div", "dl", "p", "ol", "ul", "li"]),
	headerElements = ["h2", "h3"]):
	"""Given an html element as a BeautifulSoup, returns a list of string
	blocks. Each string block represents a section in the html demarcated by a
	header element. Each string block is {heading, lines}. Lines is a list of
	strings where each block element in html is a string. Heading is a list
	where the nth element represents the nth subheading applicable to the
	current section. Empty lines are not retained.
	"""

	def closeString(sb, s):
		s = s.strip()
		if s:
			sb["lines"].append(s)

	def closeStringBlock(sbs, sb, s):
		closeString(sb, s)
		if sb["lines"]:
			sbs.append(sb)

	stringBlocks = []
	currHeading = [""]
	currStringBlock = {"lines": [], "heading": currHeading}
	currString = ""
	for el in html.children:
		if el.name in headerElements:
			# close the previous block
			closeStringBlock(stringBlocks, currStringBlock, currString)

			headingIndex = headerElements.index(el.name)
			currHeading = currHeading[:headingIndex]
			if len(currHeading) < headingIndex:
				currHeading += [""] * (headingIndex - len(currHeading)) 
			# heading is usually under mw-headline, but sometimes is not
			currHeading.append(el.find(class_='mw-headline').text if el.find(class_='mw-headline') else el.get_text())
			currStringBlock = {"lines": [], "heading": currHeading}
		elif el.name in blockElements:
			closeString(currStringBlock, currString)
			currString = ""
			# assumes no header elements under block elements
			childStringBlocks = htmlToStringBlocks(el)
			if childStringBlocks:
				currStringBlock["lines"] += childStringBlocks[0]["lines"]
		else:
			currString += unicode(el)

	closeStringBlock(stringBlocks, currStringBlock, currString)

	return stringBlocks


def stringBlocksToEvents(stringBlocks, lineBreak = "<br />",
	ignoreSections = set(["", "Contents", "See also", "References"])):
	"""Given a set of string blocks (as produced by htmlToStringBlocks,
	expects that all strings are non-empty), returns a list of timeline
	events. A timeline event is {date: number, content: string}
	"""

	currEvent = {}
	events = []

	for stringBlock in stringBlocks:
		if stringBlock["heading"][0] not in ignoreSections:
			for string in stringBlock["lines"]:
				extract = findDate(string)
				if extract:
					if currEvent:
						events.append(currEvent)
					currEvent = {"date": extract[0], "content": extract[1]}
				else:
					if currEvent:
						currEvent["content"] += lineBreak + string
	return events


def getFirstTextNode(soup, remainder = []):
	"""Given an html BeautifulSoup, returns (firstPart, remainder) where
	firstPart is the first text node and remainder is everything after that
	first text node
	"""
	try:
		if soup.contents:
			(firstPart, innerRem) = getFirstTextNode(soup.contents[0], soup.contents[1:])
			return (firstPart, innerRem + "".join(unicode(s) for s in remainder))
		else:
			return ("", "".join(unicode(s) for s in remainder))
	except AttributeError:
		return (soup, "".join(unicode(s) for s in remainder))


def findDate(string):
	"""Takes a string that contains html, and returns (date, content) as a
	tuple. For now, date is an int that represents the year. Negative numbers
	are B.C. and positive are A.D. years
	"""

	soup = BeautifulSoup(string)
	(s, remainder) = getFirstTextNode(soup)

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
	m2 = re.search(u'^[\s\-–—:\.]+', rem)
	if m2:
		content = rem[m2.end():] + remainder
	else:
		content = rem + remainder

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

# TODO: add a relevance metric as a multiplier for the importance