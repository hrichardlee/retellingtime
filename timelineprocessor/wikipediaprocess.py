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


def param_defaults(p):
	p['separate'] = p.get('separate') or False
	p['single_section'] = p.get('single_section') or ''
	p['continuations'] = p.get('continuations') or False
	p['keep_row_together'] = p.get('keep_row_together') or False
	return p


def wp_page_to_events_raw(title, p = None):
	"""Without the post_processing in wp_page_to_events"""
	p = param_defaults(p or {})

	article = BeautifulSoup(get_wp_page(title).html())

	string_blocks = _html_to_string_blocks(article)
	events = _string_blocks_to_events(string_blocks, p)
	if p['separate']:
		events = _separate_events(events)
	return events



def event_to_str(event):
	return '%s: %s: %s' % (
		str(event['date']),
		BeautifulSoup(event['date_string']).get_text(),
		BeautifulSoup(event['content']).get_text()[:50])

def get_errors(raw_events, event_threshold):
	errors = ''
	first_and_last = ''
	fewer_than_threshold = False

	for e in raw_events:
		if e['date'] == None:
			errors += 'event without date:\n' + event_to_str(e) + '\n'

	if len(raw_events) < event_threshold:
		fewer_than_threshold = True
		for e in raw_events:
			first_and_last += event_to_str(e) + '\n'
	else:
		first_and_last += \
			event_to_str(raw_events[0]) + '\n' + \
			event_to_str(raw_events[1]) + '\n' + \
			event_to_str(raw_events[-2]) + '\n' + \
			event_to_str(raw_events[-1])

		for e in [e for e in raw_events if len(e['content']) < 5]:
			errors += 'short event:' + '\n' + event_to_str(e)

		# look for out of order events
		if raw_events[0]['date'] < raw_events[-1]['date']:
			bad_cmp = lambda x, y: x > y
		else:
			bad_cmp = lambda x, y: x < y

		for i, (curre, nexte) in enumerate(zip(raw_events[:-1], raw_events[1:])):
			if bad_cmp(curre['date'], nexte['date']):
				errors += 'out of order events:' + '\n'
				if (i == 0):
					errors += '---' + '\n'
				else:
					errors += event_to_str(raw_events[i-1]) + '\n'
				errors += \
					event_to_str(curre) + '\n' + \
					event_to_str(nexte) + '\n'
	return (first_and_last, errors, fewer_than_threshold)


def wp_post_process(raw_events):
	_add_importance_to_events(raw_events)
	raw_events.sort(key=lambda e: e['date'], reverse=True)
	raw_events = _filter_bad_events(raw_events)
	_fix_wikipedia_links(raw_events)

	return raw_events


def wp_page_to_events(title, p = None):
	"""Takes the title of a timeline page on Wikipedia and returns a list of
	events {date: number, date_string: string, content: string}"""
	return wp_post_process(wp_page_to_events_raw(title, p))


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


_block_elements = set([
	'address', 'article', 'aside', 'blockquote', 'section',
	'dd', 'div', 'dl', 'p', 'ol', 'ul', 'li'
])
_header_elements = ['h2', 'h3', 'h4', 'h5', 'h6']

def _html_to_string_blocks(html):
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

	_bs_fix_brs(html)

	string_blocks = []
	curr_heading = ['']
	curr_string_block = {'lines': [], 'heading': curr_heading}
	curr_string = ''
	for el in html.children:
		if el.name in _header_elements:
			# close the previous block
			close_string_blocks(string_blocks, curr_string_block, curr_string)

			heading_index = _header_elements.index(el.name)
			curr_heading = curr_heading[:heading_index]
			if len(curr_heading) < heading_index:
				curr_heading += [''] * (heading_index - len(curr_heading)) 
			# heading is usually under mw-headline, but sometimes is not
			curr_heading.append(el.find(class_='mw-headline').text if el.find(class_='mw-headline') else el.get_text())

			curr_string_block = {'lines': [], 'heading': curr_heading}
			curr_string = ''
		elif el.name in _block_elements:
			close_string(curr_string_block, curr_string)

			# assumes no header elements under block elements, which implies
			# that child_string_blocks will never have more than one
			# string_block
			child_string_blocks = _html_to_string_blocks(el)
			if child_string_blocks:
				curr_string_block['lines'] += child_string_blocks[0]['lines']

			curr_string = ''
		elif el.name == 'br':
			close_string(curr_string_block, curr_string)
			curr_string = ''
		elif el.name == 'table':
			close_string(curr_string_block, curr_string)
			curr_string_block['lines'].append({'line_type': LineTypes.table, 'line': el})
			curr_string = ''
		else:
			curr_string += unicode(el)

	close_string_blocks(string_blocks, curr_string_block, curr_string)

	return string_blocks

_line_break = '<br />'
_ignore_sections = set([
	'',
	'contents', 'see also',	'references', 'external links',	'notes',
	'further reading', 'related media', 'notes and citations'
])

def _string_blocks_to_events(string_blocks, p = None):
	"""Given a set of string blocks (as produced by _html_to_string_blocks,
	expects that all strings are non-empty), returns a list of timeline
	events. A timeline event is {date: number, date_string: string, content: string}
	"""

	curr_ignore_sections = _ignore_sections

	def section_test(name):
		if p['single_section']:
			return name.strip().lower() == p['single_section'].strip().lower()
		else:
			return name.strip().lower() not in curr_ignore_sections

	def close_event(es, e):
		if e:
			es.append(e)

	p = param_defaults(p or {})

	if all(not section_test(sb['heading'][0]) for sb in string_blocks):
		# allow the first section to be processed if it is the only section,
		# excluding excluded sections like see also, etc. Usually this section
		# is just an intro paragraph, but if this if statement is true, it is
		# probably the entire content of the article
		try:
			curr_ignore_sections = _ignore_sections.copy()
			curr_ignore_sections.remove('')
		except KeyError:
			pass

	curr_event = None
	events = []

	for string_block in string_blocks:
		prev_date = None
		if section_test(string_block['heading'][0]):
			# create base date based on headings:
			# possible perf improvement by caching results for headings across string_blocks
			base_date = TimelineDate(TimePoint())
			base_date_string = ''
			for h in string_block['heading']:
				parse = parse_date_html(h)
				if parse:
					base_date = TimelineDate.combine(base_date, parse[0])
					base_date_string = parse[1]

			# if there's a year specified in the headings, we create a fuzzy
			# range that child elements of those headings need to fall in
			base_date_range = None
			if base_date.simple_year() != None:
				delta_minus = 10
				delta_plus = 20
				m = re.search(ur'0+$', str(base_date.start.year))
				if m:
					delta_minus = int('1' + ('0' * (m.end() - m.start())))
					delta_plus = delta_minus * 2
				base_date_range = (base_date.simple_year() - delta_minus, base_date.simple_year() + delta_plus)

			for line in string_block['lines']:
				if line['line_type'] == LineTypes.line:
					parse = parse_date_html(line['line'])
					# if we can parse a date, create a new event
					if parse and \
						((not base_date_range) or \
						 (parse[0].simple_year() == None) or \
						 (parse[0].simple_year() >= base_date_range[0] and \
						 	parse[0].simple_year() <= base_date_range[1]) or \
						 (TimelineDate.can_combine_as_day(base_date, parse[0]))
						 ):

						close_event(events, curr_event)
						date = TimelineDate.combine(base_date, parse[0])
						if date.simple_year() == None and prev_date:
							# this is the case where we have a month or
							# monthday but no year. in this case, take it from
							# the previous event
							date = TimelineDate.combine(prev_date, date)
						curr_event = {
							'date': date.simple_year(),
							'date_string': parse[1],
							'content': parse[2]
						}
						prev_date = date
					# if we can't parse a date, append the line to the
					# current event if there is one
					elif curr_event:
						if p['continuations']:
							curr_event['content'] += line_break + line['line']
						else:
							close_event(events, curr_event)
							curr_event = {
								'date': curr_event['date'],
								'date_string': curr_event['date_string'],
								'content': line['line']
							}
					# if there's no parse and no current event, see if we can
					# use the base_date
					elif base_date.simple_year() != None:
						# no need to close events because curr_event is None
						curr_event = {
							'date': base_date.simple_year(),
							'date_string': base_date_string,
							'content': line['line']
						}
				elif line['line_type'] == LineTypes.table:
					close_event(events, curr_event)
					events += _table_to_events(line['line'], base_date, p)
					curr_event = None
			close_event(events, curr_event)
			curr_event = None

	return events


def _bs_fix_brs(soup):
	"""This function only works on soups (if it is given a tag, it will do
	nothing). When BeautifulSoup parses a <br> tag, it makes a closing <br />
	tag somewhere later in the document. This function fixes this problem."""
	if soup.new_tag:
		for br in soup.find_all('br'):
			br.insert_before(soup.new_tag('br'))
			br.unwrap()

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


def _lines_from_html(html):
	return \
		(line['line'] for lines in \
			(block['lines'] for block in \
				_html_to_string_blocks(html) \
			) \
			for line in lines
		if line['line_type'] == LineTypes.line)


def _table_to_events(table, base_date, p = None):
	"""Given a table html element as a BeautifulSoup, returns a list of
	"""
	p = param_defaults(p or {})

	def get_rowspan(td):
		s = td.get('rowspan')
		if s == None:
			return None

		try:
			i = int(s)
		except ValueError:
			return None

		if i >= 0:
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
		# only used if split_within_row is True
		open_rowspans = {}

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

			if len(cells) == 0 and len(row.find_all('th')) == 1:
				cells = row.find_all('th')

			if len(cells) == 1:
				extract = parse_date_html(_bs_inner_html(cells[0]))
				if extract:
					base_date = TimelineDate.combine(base_date, extract[0])
			elif len(cells) > year_col_index:
				extract = parse_date_html(_bs_inner_html(cells[year_col_index]))
				if extract:
					date = extract[0]
					date_string = extract[1]
					if date_col_index != None and len(cells) > date_col_index:
						extract2 = parse_date_html(_bs_inner_html(cells[date_col_index]))
						if extract2:
							date = TimelineDate.combine(date, extract2[0])
							date_string += ' ' + extract2[1]
					date = TimelineDate.combine(base_date, date)
					content_cells = [cell for (i, cell) in \
						enumerate(cells) if i != year_col_index and i != date_col_index]
					if p['keep_row_together']:
						content = ' '.join(_bs_inner_html(cell) for cell in content_cells)
						events.append({
							'date': date.simple_year(),
							'date_string': date_string,
							'content': content
						})
					else:
						# deal with rowspan cells
						rowspan_cells = [cell for cell in content_cells if get_rowspan(cell) != None]
						for cell in rowspan_cells:
							if _bs_inner_html(cell) not in open_rowspans:
								open_rowspans[_bs_inner_html(cell)] = (date, date_string)
							elif get_rowspan(cell) <= 0: # and in open_rowspans, implicitly
								rowspan_start = open_rowspans[_bs_inner_html(cell)]
								rowspan_date = TimelineDate.span_from_dates(rowspan_start[0], date).simple_year()
								rowspan_date_string = rowspan_start[1] + ' - ' + date_string
								for line in _lines_from_html(cell):
									events.append({
										'date': rowspan_date,
										'date_string': rowspan_date_string,
										'content': line
									})

						# deal with non-rowspan cells
						for cell in content_cells:
							if get_rowspan(cell) == None:
								for line in _lines_from_html(cell):
									events.append({
										'date': date.simple_year(),
										'date_string': date_string,
										'content': line
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