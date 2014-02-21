from django.shortcuts import render
from timelinedata.models import Timeline

# Create your views here.
def index(request):
	return render(request, 'timelineviewer/index.html', {'timelines': Timeline.objects.all()})