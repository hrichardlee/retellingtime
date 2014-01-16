# -*- coding: UTF-8 -*-

import sys
import argparse
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
from parsedate import parse_date_html

import pdb


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
	header_elements = ["h2", "h3", "h4", "h5", "h6"]):
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
				extract = parse_date_html(string)
				if extract:
					if curr_event:
						events.append(curr_event)
					curr_event = {"date": extract[0].simple_year, "content": extract[1]}
				else:
					if curr_event:
						curr_event["content"] += line_break + string
	if curr_event:
		events.append(curr_event)

	return events


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

def main():
	parser = argparse.ArgumentParser(description="Writes a json file that represents extracted timeline data")
	parser.add_argument('titles', metavar='titles', type=str, nargs='+', help='The titles of the Wikipedia pages to process')
	parser.add_argument('--separate', action='store_true', help='Separate blocks of text')

	args = parser.parse_args()

	for t in args.titles:
		with open("".join([c for c in t if c.isalpha() or c.isdigit() or c==' ']).rstrip() + ".json", "w") as f:
			f.write(wp_page_to_json(t, args.separate).encode('utf-8'))

if __name__ == "__main__":
	main()