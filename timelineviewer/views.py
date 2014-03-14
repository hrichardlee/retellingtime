from django.shortcuts import render
from timelinedata.models import Timeline

# Create your views here.
def index(request):
	all_timelines = Timeline.objects.filter(is_valid__exact = True).order_by('sort_order_title')
	return render(request, 'timelineviewer/index.html',
		# well this should really be a view, shouldn't it
		{'timelines': all_timelines,
		'highlighted_timelines': all_timelines.filter(highlighted__exact = True)
		})

def about(request):
	return render(request, 'timelineviewer/about.html')