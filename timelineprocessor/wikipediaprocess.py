# -*- coding: UTF-8 -*-

import sys
import argparse
import codecs
import re
import datetime
import json
import wikipedia
import itertools
from enum import Enum
import nltk.data
from bs4 import BeautifulSoup
import bs4
from htmlsplitter import HtmlSplitter
from parsedate import parse_date_html

import pdb


def wikipedia_timeline_page_titles():
	"""Looks at the List of timelines page and gets all of the page titles
	that are linked"""
	
	timelines_list_page_title = 'List of timelines'

	soup = BeautifulSoup(wikipedia.page(timelines_list_page_title).html())
	return [a['title'] for a in soup.find_all('a') \
		if a['href'].startswith('/wiki/') and a.has_attr('title') and ':' not in a['title'] and 'disambiguation' not in a['title'].lower()]


def wp_page_to_json(title, separate = False):
	"""Takes the title of a timeline page on Wikipedia and returns a json
	string that represents the events in that timeline"""
	return json.dumps(wp_page_to_events(title, separate))


def _wp_page_to_events_raw(title, separate = False):
	"""Without the post_processing in wp_page_to_events"""
	article = BeautifulSoup(get_wp_page(title).html())

	events = _string_blocks_to_events(_html_to_string_blocks(article))
	if separate:
		events = _separate_events(events)
	return events


def wp_page_to_events(title, separate = False):
	"""Takes the title of a timeline page on Wikipedia and returns a list of
	events {date: number, date_string: string, content: string}"""
	events = _wp_page_to_events_raw(title, separate = False)
	_add_importance_to_events(events)
	events.sort(key=lambda e: e['date'], reverse=True)
	events = _filter_bad_events(events)
	_fix_wikipedia_links(events)

	return events


def get_wp_page(title):
	"""Gets the wikipedia.page object the way that it is gotten in
	wp_page_to_events. Applications using wikipediaprocess should never call
	the wikiepdia library directly for consistency. Throws wikipedia.PageError
	if the page is not found."""
	return wikipedia.page(title, auto_suggest=False)


def _fix_wikipedia_links(events):
	"""Converts all links in the contents of events that are relative
	Wikipedia links to absolute Wikipedia links. Modifies events in place"""
	for e in events:
		soup = BeautifulSoup(e['content'])
		for a in soup.find_all('a'):
			a['href'] = 'http://en.wikipedia.org' + a['href']
		e['content'] = unicode(soup)

def _filter_bad_events(events):
	"""Eliminates events that are suspected to be incorrect, returns a new
	list."""
	#TODO add filtering based on order of dates
	return [e for e in events if e['content'] and e['date']]


# requires running the nltk downloader: nltk.download() > d > punkt
_sentence_splitter = nltk.data.load('tokenizers/punkt/english.pickle')

def _separate_events(events):
	new_events = []
	for e in events:
		htmlsplitter = HtmlSplitter(e['content'])
		separated = (htmlsplitter.get_span(start, end) \
			for start, end in _sentence_splitter.span_tokenize(htmlsplitter.text_string))
		for s in separated:
			# not sure whether to go for interface consistency or not having to reparse
			new_events.append({'date': e['date'], 'date_string': e['date_string'], 'content': unicode(s)})
	return new_events


class LineTypes(Enum):
	line = 1
	table = 2


def _html_to_string_blocks(html, 
	block_elements = set(['address', 'article', 'aside', 'blockquote', 'section', 'dd', 'div', 'dl', 'p', 'ol', 'ul', 'li']),
	header_elements = ['h2', 'h3', 'h4', 'h5', 'h6']):
	"""Given an html element as a BeautifulSoup, returns a list of string
	blocks. Each string block represents a section in the html demarcated by a
	header element. Each string block is {heading, lines: [{line_type,
	line}]}. Lines is a list of objects. line_type = LineTypes.table indicates
	that line is a BeautifulSoup table element. line_type = LineTypes.line
	indicates that the line is a string where each block element in html is a
	string. Heading is a list where the nth element represents the nth
	subheading applicable to the current section. Empty lines are not
	retained.
	"""

	def close_string(sb, s):
		if s:
			s = s.strip()
		if s:
			sb['lines'].append({'line_type': LineTypes.line, 'line': s})

	def close_string_blocks(sbs, sb, s):
		close_string(sb, s)
		if sb['lines']:
			sbs.append(sb)

	string_blocks = []
	curr_heading = ['']
	curr_string_block = {'lines': [], 'heading': curr_heading}
	curr_string = ''
	for el in html.children:
		if el.name in header_elements:
			# close the previous block
			close_string_blocks(string_blocks, curr_string_block, curr_string)

			heading_index = header_elements.index(el.name)
			curr_heading = curr_heading[:heading_index]
			if len(curr_heading) < heading_index:
				curr_heading += [''] * (heading_index - len(curr_heading)) 
			# heading is usually under mw-headline, but sometimes is not
			curr_heading.append(el.find(class_='mw-headline').text if el.find(class_='mw-headline') else el.get_text())
			curr_string_block = {'lines': [], 'heading': curr_heading}
			# curr_string = None
		elif el.name in block_elements:
			close_string(curr_string_block, curr_string)
			curr_string = ''
			# assumes no header elements under block elements
			child_string_blocks = _html_to_string_blocks(el)
			if child_string_blocks:
				curr_string_block['lines'] += child_string_blocks[0]['lines']
		elif el.name == 'table':
			close_string(curr_string_block, curr_string)
			curr_string = None
			curr_string_block['lines'].append({'line_type': LineTypes.table, 'line': el})
		else:
			if curr_string != None:
				curr_string += unicode(el)
			# if curr_string is None, that means that there is a non-block
			# element immediately after a heading or table or something like
			# that. In that case, we should just discard the line. It is
			# probably malformed. TODO log the line

	close_string_blocks(string_blocks, curr_string_block, curr_string)

	return string_blocks


def _string_blocks_to_events(string_blocks, line_break = '<br />',
	ignore_sections = set(['', 'Contents', 'See also', 'References'])):
	"""Given a set of string blocks (as produced by _html_to_string_blocks,
	expects that all strings are non-empty), returns a list of timeline
	events. A timeline event is {date: number, date_string: string, content: string}
	"""

	curr_event = {}
	events = []

	for string_block in string_blocks:
		if string_block['heading'][0] not in ignore_sections:
			for line in string_block['lines']:
				if line['line_type'] == LineTypes.line:
					extract = parse_date_html(line['line'])
					# if we can extract a date, create a new event
					if extract:
						if curr_event:
							events.append(curr_event)
						curr_event = {
							'date': extract[0].simple_year,
							'date_string': extract[1],
							'content': extract[2]
						}
					# if we can't extract a date, append the line to the
					# current event if there is one
					else:
						if curr_event:
							curr_event['content'] += line_break + line['line']
				elif line['line_type'] == LineTypes.table:
					if curr_event:
						events.append(curr_event)
					events += _table_to_events(line['line'])
					curr_event = None
			if curr_event:
				events.append(curr_event)
				curr_event = None

	return events


def _table_to_events(table):
	return []


def _add_importance_to_events(events):
	"""Given a list of events as produced by _string_blocks_to_events, adds the
	importance of each event so that events are now {date, content,
	importance: float}. Modifies events in place!
	"""

	links_lists = [
		[a['title'] for a in BeautifulSoup(event['content']).find_all('a')
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
		event['importance'] = importance


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

def main():
	parser = argparse.ArgumentParser(description='Writes a json file that represents extracted timeline data')
	parser.add_argument('titles', metavar='titles', type=str, nargs='+', help='The titles of the Wikipedia pages to process')
	parser.add_argument('--separate', action='store_true', help='Separate blocks of text')

	args = parser.parse_args()

	for t in args.titles:
		with open(''.join([c for c in t if c.isalpha() or c.isdigit() or c==' ']).rstrip() + '.json', 'w') as f:
			f.write(wp_page_to_json(t, args.separate).encode('utf-8'))

if __name__ == '__main__':
	main()