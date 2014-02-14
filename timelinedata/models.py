from django.db import models
import logging

import pdb

import timelineprocessor.wikipediaprocess as wikipediaprocess

logger = logging.getLogger(__name__)

# Create your models here.
class Timeline(models.Model):
	title = models.CharField(max_length = 500)
	events = models.CharField(max_length = 1000000)
	separate = models.BooleanField()

	def get_events(self):
		events = wikipediaprocess.wp_page_to_events(self.title, self.separate)
		if len(events) > 2:
			self.events = events
			return True
		else:
			return False

	def __unicode__(self):
		return "Timeline(id: %d, title: %s, separate: %s, events: %s)" \
			% (self.id, self.title, self.separate, self.events[:30])

	@classmethod
	def process_wikipedia_timelines(cls):
		for timeline_title in wikipediaprocess.wikipedia_timeline_page_titles():
			objs = cls.objects.filter(title=timeline_title)
			if objs:
				objs[0].get_events()
				objs[0].save()
				logger.info("Refreshed " + timeline_title)
			else:
				timeline = cls.objects.create(title=timeline_title, separate=False)
				if timeline.get_events():
					timeline.save()
					logger.info("Added " + timeline_title + " successfully")
				else:
					logger.info("Failed to add " + timeline_title)