from django.shortcuts import render
from timelinedata.models import Timeline

# Create your views here.
def index(request):
	return render(request, 'timelineviewer/index.html',
		# well this should really be a view, shouldn't it
		{'timelines': sorted([t for t in Timeline.objects.all() if t.is_valid()], key=lambda t: t.short_title()),
		'highlighted_timelines': sorted([t for t in Timeline.objects.filter(highlighted = True)], key = lambda t: t.short_title())
		})