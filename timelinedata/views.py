from django.http import HttpResponse, Http404
from timelinedata.models import Timeline
from django.shortcuts import get_object_or_404

import json


def detail(request, id):
    t = get_object_or_404(Timeline, id=id)
    return HttpResponse(t.details_json(), content_type='application/json')


def search(request, page_title):
    # note: these parameters can only be used if the timeline has never been
    # processed yet. if the timeline has been processed, the existing
    # parameters will be used. if we did not use this policy, anyone with
    # knowledge of the URL structure could do significant harm to the data.
    # Parameters can be changed through the admin interface
    separate = request.GET.get('separate', None) == 'yes'
    single_section = request.GET.get('single_section', '')
    result = Timeline.process_wikipedia_page(
        page_title, p={'separate': separate, 'single_section': single_section})
    if not result:
        raise Http404
    else:
        return HttpResponse(result.details_json(), content_type='application/json')


def all(request):
    return HttpResponse(
        json.dumps([t.summary() for t in Timeline.objects.all() if t.is_valid]),
        content_type='application/json')
