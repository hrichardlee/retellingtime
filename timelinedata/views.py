from django.http import HttpResponse
from timelinedata.models import Timeline

from timelineprocessor import wikipediaprocess
import json


import pdb

def detail(request, page_title):
	if (page_title == "test1"):
		return HttpResponse(open("timelinedata/timeline of particle physics.json"), content_type = "application/json")
	elif (page_title == "test2"):
		return HttpResponse(open("timelinedata/timeline of modern history.json"), content_type = "application/json")
	elif (page_title == "test3"):
		return HttpResponse(open("timelinedata/timeline of solar astronomy.json"), content_type = "application/json")
	elif (page_title == "test4"):

		return HttpResponse(open("timelinedata/timeline of mathematics.json"), content_type = "application/json")
	elif (page_title == "test5"):
		return HttpResponse(open("timelinedata/timeline of algorithms.json"), content_type = "application/json")
	else:
		timelines = Timeline.objects.filter(title = page_title)	
		if timelines:
			events = timelines[0].events
		else:
			events = wikipediaprocess.wp_page_to_json( \
				page_title, request.GET.get("separate", "no") == "yes")
			timeline = Timeline.objects.create(title = page_title, events = events)
			timeline.save() # move this to after the response

		return HttpResponse(events, content_type = "application/json")

def all(request):
	return HttpResponse(json.dumps([t.title for t in Timeline.objects.all()]), content_type = "application/json")