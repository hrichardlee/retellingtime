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
		events = wikipediaprocess.wp_page_to_events(self.title, self.separate)
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
			'events': self.events
		}

	def details_json(self):
		# this is a massive hack, but will work as long as 1234512345 does not
		# show up in short_title...
		return json.dumps({ 'short_title': self.short_title(),
				'events': 1234512345
			}).replace('1234512345', self.events)

	def __unicode__(self):
		return "Timeline(id: %d, title: %s, separate: %s, events: %s)" \
			% (self.id, self.title, self.separate, self.events[:30])
			

	@classmethod
	def process_wikipedia_page(cls, page_title, refresh=False, separate=False):
		"""Looks for the wikipedia page with the given title in the database.
		If found, (optionally) refreshes it and returns it. If it is not
		found, tries to parse the wikipedia page. If successful, returns the
		result. Otherwise returns None."""
		objs = cls.objects.filter(title=page_title)
		if objs:
			if refresh:
				objs[0].get_events()
				objs[0].save()
				logger.info("Refreshed " + page_title)
			return objs[0]
		else:
			timeline = cls(title=page_title, separate=separate)
			if timeline.get_events():
				timeline.save()
				logger.info("Added " + page_title + " successfully")
				return timeline
			else:
				logger.info("Failed to add " + page_title)
				return None