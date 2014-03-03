from django.db import models
from django.utils.html import format_html
import logging
import json
from bs4 import BeautifulSoup

import pdb

import timelineprocessor.wikipediaprocess as wikipediaprocess

logger = logging.getLogger(__name__)


class CommonTimelineMetadata(models.Model):
	title = models.CharField(max_length = 500)
	single_section = models.CharField(max_length = 500, default = '')
	separate = models.BooleanField()
	url = models.CharField(max_length = 500)

	class Meta:
		abstract = True


class Timeline(CommonTimelineMetadata):
	events = models.CharField(max_length = 1000000)

	def short_title(self):
		prefixes = ['timeline of ', 'chronology of']
		suffixes = [' timeline']

		t = self.title.lower()

		for p in prefixes:
			if t.startswith(p):
				return self.title[len(p)].upper() + self.title[len(p) + 1:]
		for s in suffixes:
			if t.endswith(s):
				return self.title[:-len(s)]
		return self.title

	def get_events(self):
		raw_events = wikipediaprocess.wp_page_to_events_raw(self.title, self.separate, self.single_section)
		self.url = wikipediaprocess.get_wp_page(self.title).url
		WpPageProcess.from_raw_events(raw_events, self)
		events = wikipediaprocess.wp_post_process(raw_events)
		if len(events) > 2:
			self.events = json.dumps(events)
			return True
		else:
			return False

	def summary(self):
		return { 'title': self.title,
				'short_title': self.short_title(),
				'tags': 'TODO add tags',
				'id': self.id }

	def details(self):
		return { 'short_title': self.short_title(),
			'url': self.url,
			'events': self.events
		}

	def details_json(self):
		# this is a massive hack, but will work as long as 3021621274449386 does not
		# show up in any of the other fields...
		return json.dumps({
				'metadata': {
					'short_title': self.short_title(),
					'url': self.url
				},
				'events': 3021621274449386
			}).replace('3021621274449386', self.events)

	def __unicode__(self):
		return "Timeline(id: %d, title: %s, separate: %s, events: %s)" \
			% (self.id or -1, self.title, self.separate, self.events[:30])
			

	@classmethod
	def process_wikipedia_page(cls, page_title, refresh=False, separate=False, single_section=''):
		"""Looks for the wikipedia page with the given title in the database.
		If found, (optionally) refreshes it and returns it. If it is not
		found, tries to parse the wikipedia page. If successful, returns the
		result. Otherwise returns None."""
		page_title = wikipediaprocess.normalize_title(page_title)
		objs = cls.objects.filter(title__iexact=page_title)
		if objs:
			if refresh:
				objs[0].get_events()
				objs[0].save()
				logger.info('Refreshed ' + page_title)
			return objs[0]
		else:
			timeline = cls(title=page_title, separate=separate, single_section=single_section)
			if timeline.get_events():
				timeline.save()
				logger.info('Added ' + page_title + ' successfully')
				return timeline
			else:
				logger.info('Failed to add ' + page_title)
				return None


class WpPageProcess(CommonTimelineMetadata):
	first_and_last = models.CharField(max_length = 1000)
	errors = models.CharField(max_length = 1000000)

	def metadata(self):
		s = ''
		if self.separate:
			s += 'sep '
		if self.single_section:
			s += '#' + self.single_section + ' '
		s += '<a href="%s">orig</a>' % self.url
		return format_html(s)

	def first_and_last_formatted(self):
		return format_html(self.first_and_last)
	first_and_last_formatted.admin_order_field = 'first_and_last'
	first_and_last_formatted.short_description = 'First and last'

	def errors_formatted(self):
		return format_html(self.errors)
	errors_formatted.admin_order_field = 'errors'
	errors_formatted.short_description = 'Errors'

	@classmethod
	def event_to_str(self, event):
		return '%d: %s: %s' % (event['date'], event['date_string'], BeautifulSoup(event['content']).get_text()[:50])

	@classmethod
	def from_raw_events(cls, raw_events, timeline):
		# delete any data about previous runs on this page
		objs = cls.objects.filter(title__iexact = timeline.title).delete()

		(first_and_last, errors) = cls.get_errors(raw_events)
		proc = cls(title = timeline.title, single_section = timeline.single_section,
			separate = timeline.separate, url = timeline.url,
			first_and_last = first_and_last, errors = errors)
		proc.save()

	@classmethod
	def get_errors(cls, raw_events):
		line_break = '\n<br/>\n'
		errors = ''
		first_and_last = ''

		if len(raw_events) < 4:
			errors += 'fewer than 4 events:' + line_break
			for e in raw_events:
				errors += cls.event_to_str(e) + line_break
		else:
			first_and_last += \
				cls.event_to_str(raw_events[0]) + line_break + \
				cls.event_to_str(raw_events[1]) + line_break + \
				cls.event_to_str(raw_events[-2]) + line_break + \
				cls.event_to_str(raw_events[-1])

			for e in [e for e in raw_events if len(e['content']) < 5]:
				errors += 'short event:' + line_break + cls.event_to_str(e)

			# look for out of order events
			if raw_events[0]['date'] < raw_events[-1]['date']:
				bad_cmp = lambda x, y: x > y
			else:
				bad_cmp = lambda x, y: x < y

			for i, (curre, nexte) in enumerate(zip(raw_events[:-1], raw_events[1:])):
				if bad_cmp(curre['date'], nexte['date']):
					errors += 'out of order events:' + line_break
					if (i == 0):
						errors += '---' + line_break
					else:
						errors += cls.event_to_str(raw_events[i-1]) + line_break
					errors += \
						cls.event_to_str(curre) + line_break + \
						cls.event_to_str(nexte) + line_break
		return (first_and_last, errors)