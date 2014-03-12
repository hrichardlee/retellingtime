from __future__ import absolute_import
from celery import shared_task

from timelinedata.models import Timeline

@shared_task
def add(x, y):
	print('there')
	return x + y


@shared_task
def getWikipediaTimeline(page_title):
	Timeline.process_wikipedia_page(page_title)

@shared_task
def refreshTimeline(timeline):
	timeline.get_events()