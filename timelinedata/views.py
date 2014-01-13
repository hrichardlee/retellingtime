from django.http import HttpResponse

from timelineprocessor import wikipediaprocess

import pdb

def index(request, page_title):
	if (page_title == "test1"):
		return HttpResponse(open("timelinedata/timelineofparticlephysics.json"), content_type = "application/json")
	else:
		return HttpResponse(wikipediaprocess.wp_page_to_json(
			page_title, request.GET.get("separate", "no") == "yes"),
			content_type = "application/json")