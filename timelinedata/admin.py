from django.contrib import admin
from timelinedata.models import Timeline
from timelineprocessor import wikipediaprocess
from timelinedata.views import admin_populate
from django.conf.urls import patterns, url


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

	list_display = ('title', 'banned', 'highlighted', 'params', 'timestamp',
		'first_and_last_formatted', 'fewer_than_threshold', 'errors_formatted_short')
	list_filter = ('banned', 'fewer_than_threshold', ErrorsNonEmptyFilter)
	search_fields = ('title',)

	actions = ['refresh', 'ban', 'unban', 'highlight', 'unhighlight']

	readonly_fields = ('timestamp', 'first_and_last_formatted', 'errors_formatted', 'pretty_events')

admin.site.register(Timeline, TimelineAdmin)