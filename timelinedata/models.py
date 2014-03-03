from django.db import models
import logging
import json

import pdb

import timelineprocessor.wikipediaprocess as wikipediaprocess

logger = logging.getLogger(__name__)

# Create your models here.
class Timeline(models.Model):
	title = models.CharField(max_length = 500)
	events = models.CharField(max_length = 1000000)
	single_section = models.CharField(max_length = 500, default = '')
	separate = models.BooleanField()
	url = models.CharField(max_length = 500)

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
		events = wikipediaprocess.wp_page_to_events(self.title, self.separate, self.single_section)
		if len(events) > 2:
			self.events = json.dumps(events)
			self.url = wikipediaprocess.get_wp_page(self.title).url
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