from django.http import HttpResponse
from timelinedata.models import Timeline
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.template import RequestContext

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
			separate = request.GET.get("separate", "no") == "yes"
			events = wikipediaprocess.wp_page_to_json(page_title, separate)
			timeline = Timeline.objects.create(title = page_title, separate = separate, events = events)
			timeline.save() # move this to after the response

		return HttpResponse(events, content_type = "application/json")

def all(request):
	Timeline.test()

	return HttpResponse(json.dumps([t.title for t in Timeline.objects.all()]), content_type = "application/json")


@staff_member_required
def admin_populate(request, model_admin):
	# pretty much taken wholesale from http://www.slideshare.net/lincolnloop/customizing-the-django-admin

	opts = model_admin.model._meta
	admin_site = model_admin.admin_site
	has_perm = request.user.has_perm(opts.app_label + '.' + opts.get_change_permission())

	context = {'admin_site': admin_site.name,
		'title': 'Populate',
		'opts': opts,
		# 'root_path': '/%s' % admin_site.root_path, # this is from the slides but doesn't work
		'app_label': opts.app_label,
		'has_change_permission': has_perm }
	return render_to_response('timelinedata/admin_populate.html',
		context,
		context_instance=RequestContext(request))