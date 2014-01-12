from django.http import HttpResponse

from timelineprocessor import wikipediaprocess

import pdb

def index(request, page_title):
	if (page_title == "test1"):
		return HttpResponse(open("timelinedata/timelineofparticlephysics.json"), content_type = "application/json")
	else:
		return HttpResponse(wikipediaprocess.wpPageToJson(
			page_title, True), #request.GET.get("separate", "no") == "yes"),
			content_type = "application/json")