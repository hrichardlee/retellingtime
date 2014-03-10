from django.db import models
from django.utils.html import format_html, escape
import logging
import json
from bs4 import BeautifulSoup

import pdb

import timelineprocessor.wikipediaprocess as wikipediaprocess
import timelineprocessor.htmlprocess as htmlprocess

logger = logging.getLogger(__name__)


# a timeline must have at least this many events before it will be shown
_event_threshold = 4


class Timeline(models.Model):
	# metadata
	title = models.CharField(max_length = 500)
	url = models.CharField(max_length = 500)
	timestamp = models.DateTimeField(auto_now = True)
	highlighted = models.BooleanField(default = False)

	# data
	events = models.CharField(max_length = 1000000, blank = True)
	banned = models.BooleanField(default = False)
	fewer_than_threshold = models.BooleanField()

	# error and diagnostic info
	first_and_last = models.CharField(max_length = 1000, blank = True)
	errors = models.CharField(max_length = 1000000, blank = True)

	# parameters
	single_section = models.CharField(max_length = 500, blank = True)
	separate = models.BooleanField()
	continuations = models.BooleanField()
	keep_row_together = models.BooleanField()

	def set_params(self, p):
		self.single_section = p['single_section']
		self.separate = p['separate']
		self.continuations = p['continuations']
		self.keep_row_together = p['keep_row_together']
	def get_params(self):
		return {
			'separate': self.separate,
			'single_section': self.single_section,
			'continuations': self.continuations,
			'keep_row_together': self.keep_row_together,
		}

	# admin fields params
	def params(self):
		s = ''
		if self.separate: s += 'sep '
		if self.continuations: s += 'cont '
		if self.keep_row_together: s += 'rows_together '
		if self.single_section: s += '#' + self.single_section + ' '
		s += format_html('<a href="{0}">orig</a>', self.url)
		return s
	params.allow_tags = True

	# admin fields data
	def ban(self):
		# banned pages will not be processed until the ban is lifted
		self.banned = True
		self.save()

	def unban(self):
		self.banned = False
		self.save()

	def highlight(self):
		self.highlighted = True
		self.save()

	def unhighlight(self):
		self.highlighted = False
		self.save()

	def short_events(self):
		return self.events[:50]

	def pretty_events(self):
		# way too lazy to put this in a css file...
		return format_html('<pre style="white-space: pre-wrap; font-size: medium">{0}</pre>',
				json.dumps(json.loads(self.events), indent = 4))

	# admin fields error and diagnostic
	def first_and_last_formatted(self):
		return escape(self.first_and_last).replace('\n', '<br />')
	first_and_last_formatted.allow_tags = True
	first_and_last_formatted.admin_order_field = 'first_and_last'
	first_and_last_formatted.short_description = 'first and last'

	def errors_formatted_short(self):
		return escape(self.errors[:500]).replace('\n', '<br />')
	errors_formatted_short.allow_tags = True
	errors_formatted_short.admin_order_field = 'errors'
	errors_formatted_short.short_description = 'errors (short)'

	def errors_formatted(self):
		return escape(self.errors).replace('\n', '<br />')
	errors_formatted.allow_tags = True
	errors_formatted.short_description = 'errors'

	# presenting data
	def short_title(self):
		prefixes = ['timeline of ', 'chronology of ']
		suffixes = [' timeline']

		t = self.title.lower()

		for p in prefixes:
			if t.startswith(p):
				temp = self.title[len(p):].strip()
				return temp[0].upper() + temp[1:]
		for s in suffixes:
			if t.endswith(s):
				return self.title[:-len(s)].strip()
		return self.title

	def summary(self):
		return { 'title': self.title,
				'short_title': self.short_title(),
				'tags': 'TODO add tags',
				'id': self.id }

	def details_json(self):
		# this is a massive hack, but will work as long as 3021621274449386 does not
		# show up in any of the other fields...
		return json.dumps({
				'metadata': {
					'title': self.title,
					'short_title': self.short_title(),
					'url': self.url
				},
				'events': 3021621274449386
			}).replace('3021621274449386', self.events)

	def __unicode__(self):
		return "Timeline(id: %d, title: %s, separate: %s, events: %s)" \
			% (self.id or -1, self.title, self.separate, self.events[:30])
			
	# processing data
	def is_valid(self):
		return not self.banned and not self.fewer_than_threshold

	def get_events(self):
		raw_events = wikipediaprocess.wp_page_to_events_raw(self.title, self.get_params())
		(self.first_and_last, self.errors, self.fewer_than_threshold) = wikipediaprocess.get_errors(raw_events, _event_threshold)
		self.url = wikipediaprocess.get_wp_page(self.title).url
		events = wikipediaprocess.wp_post_process(raw_events, self.url)
		if not self.fewer_than_threshold:
			self.events = json.dumps(events)
		self.save()
		return self.fewer_than_threshold

	@classmethod
	def process_wikipedia_page(cls, page_title, refresh = False, p = None):
		"""Looks for the wikipedia page with the given title in the database.
		If found, (optionally) refreshes it and returns it. If it is not
		found, tries to parse the wikipedia page. If successful, returns the
		result. Otherwise returns None."""
		page_title = wikipediaprocess.normalize_title(page_title)
		objs = cls.objects.filter(title__iexact=page_title)
		if objs:
			# assume that there is only ever one item with the same title
			timeline = objs[0]
			if refresh and not timeline.banned:
				timeline.get_events()
		else:
			timeline = cls(title=page_title)
			timeline.set_params(htmlprocess.param_defaults(p or {}))
			timeline.get_events()
		
		if timeline.is_valid():
			return timeline
		else:
			return None