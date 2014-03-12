# -*- coding: UTF-8 -*-

import re
from enum import Enum
from bs4 import BeautifulSoup
import bs4
from parsedate import parse_date_html, TimelineDate, TimePoint


def param_defaults(p):
	p['separate'] = p.get('separate') or False
	p['single_section'] = p.get('single_section') or ''
	p['extra_ignore_sections'] = p.get('extra_ignore_sections') or ''
	p['continuations'] = p.get('continuations') or False
	p['keep_row_together'] = p.get('keep_row_together') or False
	return p


class LineTypes(Enum):
	line = 1
	table = 2


_block_elements = set([
	'address', 'article', 'aside', 'blockquote', 'section',
	'dd', 'div', 'dl', 'p', 'ol', 'ul', 'li'
])
_header_elements = ['h2', 'h3', 'h4', 'h5', 'h6']

def _close_string(sb, s):
	if s:
		s = s.strip()
	if s:
		sb['lines'].append({'line_type': LineTypes.line, 'line': s})

def _close_string_blocks(sbs, sb, s):
	_close_string(sb, s)
	if sb['lines']:
		sbs.append(sb)

_ignore_classes = set([
	'thumb', 'toc',
])

def html_to_string_blocks(html):
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

	_bs_fix_brs(html)

	string_blocks = []
	curr_heading = ['']
	curr_string_block = {'lines': [], 'heading': curr_heading}
	curr_string = ''
	for el in html.children:
		try:
			if el.has_attr('class') and any((c in _ignore_classes) for c in el['class']):
				continue
		except (AttributeError, KeyError):
			pass

		if el.name in _header_elements:
			# close the previous block
			_close_string_blocks(string_blocks, curr_string_block, curr_string)

			heading_index = _header_elements.index(el.name)
			curr_heading = curr_heading[:heading_index]
			if len(curr_heading) < heading_index:
				curr_heading += [''] * (heading_index - len(curr_heading)) 
			# heading is usually under mw-headline, but sometimes is not
			curr_heading.append(el.find(class_='mw-headline').text if el.find(class_='mw-headline') else el.get_text())

			curr_string_block = {'lines': [], 'heading': curr_heading}
			curr_string = ''
		elif el.name in _block_elements:
			_close_string(curr_string_block, curr_string)

			# assumes no header elements under block elements, which implies
			# that child_string_blocks will never have more than one
			# string_block
			child_string_blocks = html_to_string_blocks(el)
			if child_string_blocks:
				curr_string_block['lines'] += child_string_blocks[0]['lines']

			curr_string = ''
		elif el.name == 'br':
			_close_string(curr_string_block, curr_string)
			curr_string = ''
		elif el.name == 'table':
			_close_string(curr_string_block, curr_string)
			curr_string_block['lines'].append({'line_type': LineTypes.table, 'line': el})
			curr_string = ''
		else:
			curr_string += unicode(el)

	_close_string_blocks(string_blocks, curr_string_block, curr_string)

	return string_blocks


_line_break = '<br />'
_ignore_sections = set([
	'',
	'contents', 'see also',	'references', 'external links',	'notes',
	'further reading', 'related media', 'notes and citations', 'footnotes',
])

def _close_event(es, e):
	if e:
		es.append(e)

def string_blocks_to_events(string_blocks, p = None):
	"""Given a set of string blocks (as produced by html_to_string_blocks,
	expects that all strings are non-empty), returns a list of timeline
	events. A timeline event is {date: number, date_string: string, content: string}
	"""

	curr_ignore_sections = _ignore_sections.copy()
	p = param_defaults(p or {})

	def section_test(name):
		if p['single_section']:
			return name.strip().lower() == p['single_section'].strip().lower()
		else:
			return name.strip().lower() not in curr_ignore_sections

	if all(not section_test(sb['heading'][0]) for sb in string_blocks):
		# allow the first section to be processed if it is the only section,
		# excluding excluded sections like see also, etc. Usually this section
		# is just an intro paragraph, but if this if statement is true, it is
		# probably the entire content of the article
		try:
			curr_ignore_sections.remove('')
		except KeyError:
			pass
	if p['extra_ignore_sections']:
		for s in p['extra_ignore_sections'].split('&'):
			curr_ignore_sections.add(s.lower().strip())

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
			if base_date.start_year() != None:
				delta_minus = 10
				delta_plus = 20
				m = re.search(ur'0+$', str(base_date.start.year))
				if m:
					delta_minus = int('1' + ('0' * (m.end() - m.start())))
					delta_plus = delta_minus * 2
				base_date_range = (base_date.start_year() - delta_minus, base_date.start_year() + delta_plus)

			for line in string_block['lines']:
				if line['line_type'] == LineTypes.line:
					parse = parse_date_html(line['line'])
					# if we can parse a date, create a new event
					if parse and \
						((not base_date_range) or \
						 (parse[0].start_year() == None) or \
						 (base_date_string.lower().strip() == 'antiquity') or \
						 (parse[0].start_year() >= base_date_range[0] and \
						 	parse[0].start_year() <= base_date_range[1]) or \
						 (TimelineDate.can_combine_as_day(base_date, parse[0]))
						 ):

						_close_event(events, curr_event)
						date = TimelineDate.combine(base_date, parse[0])
						if date.start_year() == None and prev_date:
							# this is the case where we have a month or
							# monthday but no year. in this case, take it from
							# the previous event
							date = TimelineDate.combine(prev_date, date)
						curr_event = {
							'date': date.start_year(),
							'date_length': date.length(),
							'date_string': parse[1],
							'content': parse[2]
						}
						prev_date = date
					# if we can't parse a date, append the line to the
					# current event if there is one
					elif curr_event:
						if p['continuations']:
							curr_event['content'] += _line_break + line['line']
						else:
							_close_event(events, curr_event)
							curr_event = {
								'date': curr_event['date'],
								'date_length': curr_event['date_length'],
								'date_string': curr_event['date_string'],
								'content': line['line']
							}
					# if there's no parse and no current event, see if we can
					# use the base_date
					elif base_date.start_year() != None:
						# no need to close events because curr_event is None
						curr_event = {
							'date': base_date.start_year(),
							'date_length': base_date.length(),
							'date_string': base_date_string,
							'content': line['line']
						}
				elif line['line_type'] == LineTypes.table:
					_close_event(events, curr_event)
					events += _table_to_events(line['line'], base_date, p)
					curr_event = None
			_close_event(events, curr_event)
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
				html_to_string_blocks(html) \
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
					events.append({
						'date': base_date.start_year(),
						'date_length': base_date.length(),
						'date_string': extract[1],
						'content': extract[2]
					})
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
							'date': date.start_year(),
							'date_length': date.length(),
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
								rowspan_date = TimelineDate.span_from_dates(rowspan_start[0], date)
								rowspan_date_string = rowspan_start[1] + ' - ' + date_string
								for line in _lines_from_html(cell):
									events.append({
										'date': rowspan_date.start_year(),
										'date_length': rowspan_date.length(),
										'date_string': rowspan_date_string,
										'content': line
									})

						# deal with non-rowspan cells
						for cell in content_cells:
							if get_rowspan(cell) == None:
								for line in _lines_from_html(cell):
									events.append({
										'date': date.start_year(),
										'date_length': date.length(),
										'date_string': date_string,
										'content': line
									})

	return events


_problem_elements = set([
	'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
	'table', 'tr', 'td', 'thead', 'tfoot', 'tbody', 'th',	
])

def clean_events(events):
	"""Takes raw events and replaces any problematic elements. Modifies events
	in place."""
	for e in events:
		e['content'] = clean_html(BeautifulSoup(e['content']))
		e['date_string'] = clean_html(BeautifulSoup(e['date_string']))

def clean_html(soup):
	rewrapped = True
	while rewrapped:
		rewrapped = False
		for el in soup.descendants:
			if el.name in _problem_elements:
				el.wrap(soup.new_tag('div'))
				el.unwrap()
				rewrapped = True
			elif el.name == 'img' and el.get('src'):
				text = el.get('alt') or 'img'
				a = soup.new_tag('a', href=el.get('src'))
				a.string = '[' + text + ']'
				el.replace_with(a)

			try:
				if el.get('class') and 'mw-editsection' in el.get('class'):
					el.extract()
			except AttributeError:
				# non tags won't have the get method
				pass
	return unicode(soup)