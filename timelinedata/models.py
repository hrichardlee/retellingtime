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

	def get_events(self):
		events = wikipediaprocess.wp_page_to_events(self.title, self.separate)
		if len(events) > 2:
			self.events = json.dumps(events)
			return True
		else:
			return False

	def __unicode__(self):
		return "Timeline(id: %d, title: %s, separate: %s, events: %s)" \
			% (self.id, self.title, self.separate, self.events[:30])

	@classmethod
	def process_wikipedia_page(cls, page_title):
		objs = cls.objects.filter(title=page_title)
		if objs:
			objs[0].get_events()
			objs[0].save()
			logger.info("Refreshed " + page_title)
		else:
			timeline = cls(title=page_title, separate=False)
			if timeline.get_events():
				timeline.save()
				logger.info("Added " + page_title + " successfully")
			else:
				logger.info("Failed to add " + page_title)