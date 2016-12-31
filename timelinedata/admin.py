from __future__ import absolute_import

from django.contrib import admin
from timelinedata.models import Timeline


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
	def refresh(modeladmin, request, queryset):
		for timeline in queryset:
			timeline.get_events()

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

	actions = ['refresh', 'ban', 'unban', 'highlight', 'unhighlight', 'combine']

	readonly_fields = ('timestamp', 'first_and_last_formatted', 'errors_formatted', 'pretty_events')

admin.site.register(Timeline, TimelineAdmin)