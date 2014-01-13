# -*- coding: UTF-8 -*-

import sys
import codecs
import re
import datetime
import json
import wikipedia
import itertools
import nltk.data
from bs4 import BeautifulSoup
import bs4
from htmlsplitter import HtmlSplitter


def wp_page_to_json(title, separate = False):
	"""Takes the title of a timeline page on Wikipedia and outputs it to a
	json file
	"""
	article = BeautifulSoup(wikipedia.page(title).html())

	events = _string_blocks_to_events(_html_to_string_blocks(article))
	if separate:
		events = _separate_events(events)
	_add_importance_to_events(events)
	events.reverse()

	return json.dumps(events)


# requires running the nltk downloader
_sentence_splitter = nltk.data.load("tokenizers/punkt/english.pickle")

def _separate_events(events):
	new_events = []
	for e in events:
		htmlsplitter = HtmlSplitter(e["content"])
		separated = (htmlsplitter.get_span(start, end) \
			for start, end in _sentence_splitter.span_tokenize(htmlsplitter.text_string))
		for s in separated:
			# not sure whether to go for interface consistency or not having to reparse
			new_events.append({"date": e["date"], "content": unicode(s)})
	return new_events


def _html_to_string_blocks(html, 
	block_elements = set(["address", "article", "aside", "blockquote", "section", "dd", "div", "dl", "p", "ol", "ul", "li"]),
	header_elements = ["h2", "h3"]):
	"""Given an html element as a BeautifulSoup, returns a list of string
	blocks. Each string block represents a section in the html demarcated by a
	header element. Each string block is {heading, lines}. Lines is a list of
	strings where each block element in html is a string. Heading is a list
	where the nth element represents the nth subheading applicable to the
	current section. Empty lines are not retained.
	"""

	def close_string(sb, s):
		s = s.strip()
		if s:
			sb["lines"].append(s)

	def close_string_blocks(sbs, sb, s):
		close_string(sb, s)
		if sb["lines"]:
			sbs.append(sb)

	string_blocks = []
	curr_heading = [""]
	curr_string_block = {"lines": [], "heading": curr_heading}
	curr_string = ""
	for el in html.children:
		if el.name in header_elements:
			# close the previous block
			close_string_blocks(string_blocks, curr_string_block, curr_string)

			heading_index = header_elements.index(el.name)
			curr_heading = curr_heading[:heading_index]
			if len(curr_heading) < heading_index:
				curr_heading += [""] * (heading_index - len(curr_heading)) 
			# heading is usually under mw-headline, but sometimes is not
			curr_heading.append(el.find(class_='mw-headline').text if el.find(class_='mw-headline') else el.get_text())
			curr_string_block = {"lines": [], "heading": curr_heading}
		elif el.name in block_elements:
			close_string(curr_string_block, curr_string)
			curr_string = ""
			# assumes no header elements under block elements
			child_string_blocks = _html_to_string_blocks(el)
			if child_string_blocks:
				curr_string_block["lines"] += child_string_blocks[0]["lines"]
		else:
			curr_string += unicode(el)

	close_string_blocks(string_blocks, curr_string_block, curr_string)

	return string_blocks


def _string_blocks_to_events(string_blocks, line_break = "<br />",
	ignore_sections = set(["", "Contents", "See also", "References"])):
	"""Given a set of string blocks (as produced by _html_to_string_blocks,
	expects that all strings are non-empty), returns a list of timeline
	events. A timeline event is {date: number, content: string}
	"""

	curr_event = {}
	events = []

	for string_block in string_blocks:
		if string_block["heading"][0] not in ignore_sections:
			for string in string_block["lines"]:
				extract = _find_date(string)
				if extract:
					if curr_event:
						events.append(curr_event)
					curr_event = {"date": extract[0], "content": extract[1]}
				else:
					if curr_event:
						curr_event["content"] += line_break + string
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


def _find_date(string):
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


def _add_importance_to_events(events):
	"""Given a list of events as produced by _string_blocks_to_events, adds the
	importance of each event so that events are now {date, content,
	importance: float}. Modifies events in place!
	"""

	links_lists = [
		[a["title"] for a in BeautifulSoup(event["content"]).find_all('a')
			if a['href'].startswith('/wiki/')]
		for event in events]
	counts = (len(l) for l in links_lists)
	# flatten and get importances
	importances = _bulk_importance(itertools.chain.from_iterable(links_lists))
	importance_lists = _group_list_by_count(importances, counts)
	average_importances = \
		(float(sum(importanceList))/len(importanceList) if len(importanceList) > 0 else 0 \
			for importanceList in importance_lists)
	for event, importance in zip(events, average_importances):
		event["importance"] = importance


def _group_list_by_constant(l, n):
	length = len(l)
	for i in range(0, length, n):
		yield l[i:min(i+n, length)]


def _group_list_by_count(l, counts):
	i = 0
	for count in counts:
		yield l[i:i + count]
		i += count


def _bulk_importance(links):
	"""Given a list of Wikipedia page titles, returns a list of importance scores
	"""
	rev_sizes = map(lambda ls: wikipedia.batchRevSize(ls),
		_group_list_by_constant(list(links), wikipedia.BATCH_LIMIT))
	return list(itertools.chain.from_iterable(rev_sizes))
	#return (p.backlinkCount(), len(p.content), p.revCount())

# TODO: add a relevance metric as a multiplier for the importance