from django.contrib import admin
from timelinedata.models import Timeline, WpPageProcess
from timelineprocessor import wikipediaprocess
from timelinedata.views import admin_populate
from django.conf.urls import patterns, url

class TimelineAdmin(admin.ModelAdmin):
	def populate_view(self, request):
		return admin_populate(request, self)

	def get_urls(self):
		# pretty much taken wholesale from http://www.slideshare.net/lincolnloop/customizing-the-django-admin
		urls = super(TimelineAdmin, self).get_urls()
		add_urls = patterns('',
			url(r'^populate/$', self.populate_view, name='timelineadmin_populate'))
		return add_urls + urls

	def refresh(modeladmin, request, queryset):
		for timeline in queryset:
			timeline.get_events()
			timeline.save()

	actions = ['refresh']

class WpPageProcessAdmin(admin.ModelAdmin):
	list_display = ('title', 'metadata',
		'first_and_last_formatted', 'errors_formatted')
admin.site.register(Timeline, TimelineAdmin)
admin.site.register(WpPageProcess, WpPageProcessAdmin)