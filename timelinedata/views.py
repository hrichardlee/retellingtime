from django.http import HttpResponse, Http404
from timelinedata.models import Timeline
import timelinedata.tasks
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from timelineprocessor import wikipediaprocess
import wikipedia
import json

import pdb

def detail(request, id):
	t = get_object_or_404(Timeline, id=id)
	return HttpResponse(t.details_json(), content_type = 'application/json')

def search(request, page_title):
	try:
		wikipediaprocess.get_wp_page(page_title)
	except wikipedia.PageError:
		# this is a quick hack. should be symmetric with Timeline.short_title
		page_title = 'Timeline of ' + page_title
	try:
		wikipediaprocess.get_wp_page(page_title)
	except wikipedia.PageError:
		raise Http404
	# note: these parameters can only be used if the timeline has never been
	# processed yet. if the timeline has been processed, the existing
	# parameters will be used. if we did not use this policy, anyone with
	# knowledge of the URL structure could do significant harm to the data.
	# Parameters can be changed through the admin interface
	separate = request.GET.get('separate', None) == 'yes'
	single_section = request.GET.get('single_section', '')
	result = Timeline.process_wikipedia_page(page_title,
		p = { 'separate': separate, 'single_section': single_section })
	if not result:
		raise Http404
	else:
		return HttpResponse(result.details_json(), content_type = 'application/json')

def all(request):
	return HttpResponse(
		json.dumps([t.summary() for t in Timeline.objects.all()]),
		content_type = 'application/json')


@staff_member_required
def admin_populate(request, model_admin):
	timeline_titles =  wikipediaprocess.wikipedia_timeline_page_titles()
	for title in timeline_titles:
		timelinedata.tasks.getWikipediaTimeline.delay(title)

	# pretty much taken wholesale from http://www.slideshare.net/lincolnloop/customizing-the-django-admin
	opts = model_admin.model._meta
	admin_site = model_admin.admin_site
	has_perm = request.user.has_perm(opts.app_label + '.' + opts.get_change_permission())

	context = {'admin_site': admin_site.name,
		'title': 'Populate',
		'opts': opts,
		# 'root_path': '/%s' % admin_site.root_path, # this is from the slides but doesn't work
		'app_label': opts.app_label,
		'has_change_permission': has_perm,
		'timeline_titles': timeline_titles }
	return render_to_response('timelinedata/admin_populate.html',
		context,
		context_instance=RequestContext(request))