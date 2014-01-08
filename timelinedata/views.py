from django.http import HttpResponse

from timelineprocessor import wikipediaprocess

def index(request, page_title):
	if (page_title == "test1"):
		return HttpResponse(open("timelinedata/timelineofparticlephysics.json"), content_type = "application/json")
	else:
		return HttpResponse(wikipediaprocess.jsonFromPage(page_title), content_type = "application/json")