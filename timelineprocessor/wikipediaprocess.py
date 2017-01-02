# -*- coding: UTF-8 -*-

import itertools
import nltk.data
from bs4 import BeautifulSoup
import wikipedia
from htmlsplitter import HtmlSplitter
import htmlprocess


# processing lists of timelines

def wikipedia_timeline_page_titles():
    """Looks at the List of timelines page and gets all of the page titles that are linked"""

    timelines_list_page_title = 'List of timelines'

    soup = BeautifulSoup(wikipedia.page(timelines_list_page_title).html())
    return [a['title'] for a in soup.find_all('a')
            if a['href'].startswith('/wiki/') and a.has_attr('title')
            and ':' not in a['title'] and 'disambiguation' not in a['title'].lower()]


# title-related functions

def normalize_title(title):
    # this is done automatically by the wikipedia servers, but if we want to
    # compare titles locally, we need to call this
    return title.replace('_', ' ')


def get_wp_page(title):
    """Gets the wikipedia.page object the way that it is gotten in wp_page_to_events.
    Applications using wikipediaprocess should never call the wikiepdia library directly for
    consistency. Throws wikipedia.PageError if the page is not found."""
    return wikipedia.page(title, auto_suggest=False)


# processing data

def wp_page_to_events_raw(title, p=None):
    """Takes the title of a timeline page on Wikipedia and returns a list of events {date:
    number, date_string: string, content: string}"""
    p = htmlprocess.param_defaults(p or {})

    article = BeautifulSoup(get_wp_page(title).html())

    string_blocks = htmlprocess.html_to_string_blocks(article)
    events = htmlprocess.string_blocks_to_events(string_blocks, p)
    if p['separate']:
        events = _separate_events(events)
    return events


def wp_post_process(raw_events, url):
    _add_importance_to_events(raw_events)
    raw_events.sort(key=lambda e: e['date'], reverse=True)
    _fix_wikipedia_links(raw_events, url)
    htmlprocess.clean_events(raw_events)
    raw_events = _filter_bad_events(raw_events)

    return raw_events


def _fix_wikipedia_links(events, url):
    """Converts all links in the contents of events that are relative Wikipedia links to absolute
    Wikipedia links. Modifies events in place"""
    for e in events:
        soup = BeautifulSoup(e['content'])
        for a in soup.find_all('a'):
            a['target'] = '_blank'

            if a['href'].startswith('/'):
                a['href'] = 'http://en.wikipedia.org' + a['href']
            elif a['href'].startswith('#'):
                a['href'] = url + a['href']
        e['content'] = unicode(soup)


def _filter_bad_events(events):
    """Eliminates events that are suspected to be incorrect, returns a new list."""
    # TODO add filtering based on order of dates
    return [e for e in events
            if e['content'] and e['date'] is not None and
            len(BeautifulSoup(e['content']).get_text().strip()) > 2]


# requires running the nltk downloader: nltk.download() > d > punkt
_sentence_splitter = nltk.data.load('tokenizers/punkt/english.pickle')


def _separate_events(events):
    new_events = []
    for e in events:
        htmlsplitter = HtmlSplitter(e['content'])
        separated = (htmlsplitter.get_span(start, end)
                     for start, end in _sentence_splitter.span_tokenize(htmlsplitter.text_string))
        for s in separated:
            # not sure whether to go for interface consistency or not having to reparse
            new_events.append({
                'date': e['date'],
                'date_string': e['date_string'],
                'content': unicode(s)})
    return new_events


# errors and diagnostics

def _event_to_str(event):
    return '%s: %s: %s' % (
        str(event['date']),
        BeautifulSoup(event['date_string']).get_text(),
        BeautifulSoup(event['content']).get_text()[:50])


def get_errors(raw_events, event_threshold):
    errors = ''
    first_and_last = ''
    fewer_than_threshold = False

    for e in raw_events:
        if e['date'] is None:
            errors += 'event without date:\n' + _event_to_str(e) + '\n'

    if len(raw_events) < event_threshold:
        fewer_than_threshold = True
        for e in raw_events:
            first_and_last += _event_to_str(e) + '\n'
    else:
        first_and_last += \
            _event_to_str(raw_events[0]) + '\n' + \
            _event_to_str(raw_events[1]) + '\n' + \
            _event_to_str(raw_events[-2]) + '\n' + \
            _event_to_str(raw_events[-1])

        for e in [e for e in raw_events if len(BeautifulSoup(e['content']).get_text()) <= 2]:
            errors += 'short event:' + '\n' + _event_to_str(e)

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
                    errors += _event_to_str(raw_events[i - 1]) + '\n'
                errors += \
                    _event_to_str(curre) + '\n' + \
                    _event_to_str(nexte) + '\n'
    return first_and_last, errors, fewer_than_threshold


# adding importance

def _add_importance_to_events(events):
    """Given a list of events as produced by wp_page_to_events_raw, adds the importance of each
    event so that events are now {date, content, importance: float}. Modifies events in place!"""

    links_lists = [
        [a['title'] for a in BeautifulSoup(event['content']).find_all('a')
         if a.has_key('title') and a['href'].startswith('/wiki/')]
        for event in events]
    counts = (len(l) for l in links_lists)
    # flatten and get importances
    importances = _bulk_importance(itertools.chain.from_iterable(links_lists))
    importance_lists = _group_list_by_count(importances, counts)
    average_importances = \
        (float(sum(importanceList)) / len(importanceList) if len(importanceList) > 0 else 0
         for importanceList in importance_lists)
    for event, importance in zip(events, average_importances):
        event['importance'] = importance


def _group_list_by_constant(l, n):
    length = len(l)
    for i in range(0, length, n):
        yield l[i:min(i + n, length)]


def _group_list_by_count(l, counts):
    i = 0
    for count in counts:
        yield l[i:i + count]
        i += count


def _bulk_importance(links):
    """Given a list of Wikipedia page titles, returns a list of importance scores"""
    rev_sizes = map(lambda ls: wikipedia.batchRevSize(ls),
                    _group_list_by_constant(list(links), wikipedia.BATCH_LIMIT))
    return list(itertools.chain.from_iterable(rev_sizes))
    # return (p.backlinkCount(), len(p.content), p.revCount())

    # TODO: add a relevance metric as a multiplier for the importance
