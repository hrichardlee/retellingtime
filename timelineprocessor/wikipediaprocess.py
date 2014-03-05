# -*- coding: UTF-8 -*-

import sys
import argparse
import codecs
import re
import datetime
import json
import wikipedia
import itertools
from exceptions import ValueError
from enum import Enum
import nltk.data
from bs4 import BeautifulSoup
import bs4
from htmlsplitter import HtmlSplitter
from parsedate import parse_date_html, TimelineDate, TimePoint

import pdb


def normalize_title(title):
	# this is done automatically by the wikipedia servers, but if we want to
	# compare titles locally, we need to call this
	return title.replace('_', ' ')


def wikipedia_timeline_page_titles():
	"""Looks at the List of timelines page and gets all of the page titles
	that are linked"""
	
	timelines_list_page_title = 'List of timelines'

	soup = BeautifulSoup(wikipedia.page(timelines_list_page_title).html())
	return [a['title'] for a in soup.find_all('a') \
		if a['href'].startswith('/wiki/') and a.has_attr('title') and ':' not in a['title'] and 'disambiguation' not in a['title'].lower()]


def wp_page_to_events_raw(title, separate = False, single_section = None):
	"""Without the post_processing in wp_page_to_events"""
	article = BeautifulSoup(get_wp_page(title).html())

	string_blocks = _html_to_string_blocks(article)
	events = _string_blocks_to_events(string_blocks, single_section = single_section)
	if separate:
		events = _separate_events(events)
	return events

def wp_post_process(raw_events):
	_add_importance_to_events(raw_events)
	raw_events.sort(key=lambda e: e['date'], reverse=True)
	raw_events = _filter_bad_events(raw_events)
	_fix_wikipedia_links(raw_events)

	return raw_events


def wp_page_to_events(title, separate = False, single_section = None):
	"""Takes the title of a timeline page on Wikipedia and returns a list of
	events {date: number, date_string: string, content: string}"""
	return wp_post_process(
		wp_page_to_events_raw(
			title, separate, single_section))


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
	return [e for e in events if e['content'] and e['date'] != None]


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
			curr_string = ''
		elif el.name in block_elements:
			close_string(curr_string_block, curr_string)

			# assumes no header elements under block elements
			child_string_blocks = _html_to_string_blocks(el)
			if child_string_blocks:
				curr_string_block['lines'] += child_string_blocks[0]['lines']

			curr_string = ''
		elif el.name == 'table':
			close_string(curr_string_block, curr_string)
			curr_string_block['lines'].append({'line_type': LineTypes.table, 'line': el})
			curr_string = ''
		else:
			curr_string += unicode(el)

	close_string_blocks(string_blocks, curr_string_block, curr_string)

	return string_blocks


def _string_blocks_to_events(string_blocks,
	line_break = '<br />', single_section = None,
	ignore_sections = set(['', 'contents', 'see also', 'references', 'external links', 'notes', 'further reading', 'related media'])):
	"""Given a set of string blocks (as produced by _html_to_string_blocks,
	expects that all strings are non-empty), returns a list of timeline
	events. A timeline event is {date: number, date_string: string, content: string}
	"""

	def section_test(name):
		if single_section:
			return name.strip().lower() == single_section.strip().lower()
		else:
			return name.strip().lower() not in ignore_sections

	def close_event(es, e):
		if e:
			es.append(e)

	if all(not section_test(sb['heading'][0]) for sb in string_blocks):
		# allow the first section to be processed if it is the only section,
		# excluding excluded sections like see also, etc. Usually this section
		# is just an intro paragraph, but if this if statement is true, it is
		# probably the entire content of the article
		try:
			ignore_sections.remove('')
		except KeyError:
			pass

	curr_event = None
	events = []

	for string_block in string_blocks:
		if section_test(string_block['heading'][0]):
			# create base date based on headings:
			# possible perf improvement by caching results for headings across string_blocks
			base_date = TimelineDate(TimePoint())
			for h in string_block['heading']:
				parse = parse_date_html(h)
				if parse:
					base_date = TimelineDate.combine(base_date, parse[0])

			for line in string_block['lines']:
				if line['line_type'] == LineTypes.line:
					parse = parse_date_html(line['line'])
					# if we can parse a date, create a new event
					if parse:
						close_event(events, curr_event)
						curr_event = {
							'date': TimelineDate.combine(base_date, parse[0]).simple_year(),
							'date_string': parse[1],
							'content': parse[2]
						}
					# if we can't parse a date, append the line to the
					# current event if there is one
					elif curr_event:
						curr_event['content'] += line_break + line['line']
				elif line['line_type'] == LineTypes.table:
					close_event(events, curr_event)
					events += _table_to_events(line['line'])
					curr_event = None
			close_event(events, curr_event)
			curr_event = None

	return events


def _bs_inner_html(soup):
	"""Gets the inner html (almost) of a BeautifulSoup element. It is slightly
	different than the javascript function because it drops all comments and
	comment-like items"""
	return ''.join(unicode(c) for c in soup.children if
		not isinstance(c, bs4.Comment) and
		not isinstance(c, bs4.CData) and
		not isinstance(c, bs4.ProcessingInstruction) and
		not isinstance(c, bs4.Declaration) and
		not isinstance(c, bs4.Doctype))


def _table_to_events(table):
	"""Given a table html element as a BeautifulSoup, returns a list of
	"""
	def get_rowspan(td):
		s = td.get('rowspan')
		if not s:
			return None

		try:
			i = int(s)
		except ValueError:
			return None

		if i >= 1:
			return i
		else:
			return None

	events = []

	year_col_index = None
	date_col_index = None
	for row in table.find_all('tr'):
		cells = row.find_all('th')
		for i, cell in enumerate(cells):
			cell_text = cell.get_text().strip().lower()
			if cell_text == 'year': year_col_index = i
			elif cell_text == 'date': date_col_index = i
	if date_col_index != None and year_col_index == None:
		year_col_index = date_col_index
		date_col_index = None
	if year_col_index == None and date_col_index == None:
		# just try using the first column. could be a bit smarter about giving
		# up early to save some cycles...
		year_col_index = 0

	if year_col_index != None or date_col_index != None:
		# a td that has a rowspan will be stored as (col_index, cell) The
		# rowspan number essentially gets decremented in the td element each
		# time it is added to the subsequent row
		rowspans = []

		for row in table.find_all('tr'):
			cells = row.find_all('td')

			# first, apply existing rowspans
			for (i, cell) in rowspans:
				if get_rowspan(cell) > 0:
					cells.insert(i, cell)
			# then, recollect existing and new rowspans
			rowspans = []
			for (i, cell) in enumerate(cells):
				rs = get_rowspan(cell)
				if rs:
					cell['rowspan'] = rs - 1
					rowspans.append((i, cell))

			if len(cells) > year_col_index:
				extract = parse_date_html(_bs_inner_html(cells[year_col_index]))
				if extract:
					date = extract[0]
					date_string = extract[1]
					if date_col_index != None and len(cells) > date_col_index:
						extract2 = parse_date_html(_bs_inner_html(cells[date_col_index]))
						if extract2:
							date = TimelineDate.combine(date, extract2[0])
							date_string += ' ' + extract2[1]
					content = ''.join(_bs_inner_html(cell) for (i, cell) in \
						enumerate(cells) if i != year_col_index and i != date_col_index)
					events.append({
						'date': date.simple_year(),
						'date_string': date_string,
						'content': content
					})

	return events


def _add_importance_to_events(events):
	"""Given a list of events as produced by _string_blocks_to_events, adds the
	importance of each event so that events are now {date, content,
	importance: float}. Modifies events in place!
	"""

	links_lists = [
		[a['title'] for a in BeautifulSoup(event['content']).find_all('a')
			if a.has_key('title') and a['href'].startswith('/wiki/')]
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
			f.write(json.dumps(wp_page_to_events(t, args.separate)).encode('utf-8'))

if __name__ == '__main__':
	main()