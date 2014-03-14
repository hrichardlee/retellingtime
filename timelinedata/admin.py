from __future__ import absolute_import

from django.contrib import admin
from timelinedata.models import Timeline
from timelineprocessor import wikipediaprocess
from timelinedata.views import admin_populate_from_list, admin_populate_from_title_search
import timelinedata.tasks
from django.conf.urls import patterns, url
from celery.task.control import discard_all


class ErrorsNonEmptyFilter(admin.SimpleListFilter):
	title = 'has errors?'
	parameter_name = 'has_errors'

	def lookups(self, request, model_admin):
		return (
			('yes', 'yes'),
			('no', 'no'),
		)
	def queryset(self, request, queryset):
		if self.value() == 'yes':
			return queryset.exclude(errors__exact='')
		if self.value() == 'no':
			return queryset.filter(errors__exact='')

class CombinationsFilter(admin.SimpleListFilter):
	title = 'is combo?'
	parameter_name = 'is_combo'

	def lookups(self, request, model_admin):
		return (
			('yes', 'yes'),
			('no', 'no'),
		)
	def queryset(self, request, queryset):
		if self.value() == 'yes':
			return queryset.exclude(orig_titles__exact='')
		if self.value() == 'no':
			return queryset.filter(orig_titles__exact='')

class TimelineAdmin(admin.ModelAdmin):
	def populate_from_list_view(self, request):
		return admin_populate_from_list(request, self)

	def populate_from_title_search_view(self, request):
		return admin_populate_from_title_search(request, self)

	def resave_all_view(self, request):
		timelinedata.tasks.resaveTimelines.delay()
		self.message_user(request, 'Queued resaving all timelines')
		return self.changelist_view(request)

	def refresh_all_view(self, request):
		for t in Timeline.objects.all():
			timelinedata.tasks.refreshTimeline.delay(t)
		self.message_user(request, 'Queued refresh for all')
		return self.changelist_view(request)

	def cancel_all_view(self, request):
		n = discard_all()
		self.message_user(request, 'Discarded %d tasks' % n)
		return self.changelist_view(request)

	def get_urls(self):
		# pretty much taken wholesale from http://www.slideshare.net/lincolnloop/customizing-the-django-admin
		urls = super(TimelineAdmin, self).get_urls()
		add_urls = patterns('',
			url(r'^populate_from_list/$', self.populate_from_list_view, name='timelineadmin_populate_from_list'),
			url(r'^populate_from_title_search/$', self.populate_from_title_search_view, name='timelineadmin_populate_from_title_search'),
			url(r'^resave_all/$', self.resave_all_view, name='timelineadmin_resave_all'),
			url(r'^refresh_all/$', self.refresh_all_view, name='timelineadmin_refresh_all'),
			url(r'^cancel_all/$', self.cancel_all_view, name='timelineadmin_cancel_all'),
			)
		return add_urls + urls

	def refresh(modeladmin, request, queryset):
		for timeline in queryset:
			timeline.get_events()

	def asyncRefresh(modeladmin, request, queryset):
		for timeline in queryset:
			timelinedata.tasks.refreshTimeline.delay(timeline)

	def ban(modeladmin, request, queryset):
		for p in queryset:
			p.ban()

	def unban(modeladmin, request, queryset):
		for p in queryset:
			p.unban()

	def highlight(modeladmin, request, queryset):
		for p in queryset:
			p.highlight()

	def unhighlight(modeladmin, request, queryset):
		for p in queryset:
			p.unhighlight()

	def combine(modeladmin, requests, queryset):
		Timeline.combine_timelines(queryset)

	list_display = ('title', 'banned', 'highlighted', 'params', 'timestamp',
		'first_and_last_formatted', 'fewer_than_threshold', 'errors_formatted_short')
	list_filter = ('highlighted', 'banned', 'fewer_than_threshold', ErrorsNonEmptyFilter, CombinationsFilter)
	search_fields = ('title',)

	actions = ['refresh', 'ban', 'unban', 'highlight', 'unhighlight', 'combine', 'asyncRefresh']

	readonly_fields = ('timestamp', 'first_and_last_formatted', 'errors_formatted', 'pretty_events')

admin.site.register(Timeline, TimelineAdmin)