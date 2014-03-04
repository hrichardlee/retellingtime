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


class WpPageProcessAdmin(admin.ModelAdmin):
	def refresh(modeladmin, request, queryset):
		for p in queryset:
			Timeline.process_wikipedia_page(p.title, refresh = True,
				separate = p.separate, single_section = p.single_section)

	def ban(modeladmin, request, queryset):
		for p in queryset:
			p.ban()

	def unban(modeladmin, request, queryset):
		for p in queryset:
			p.unban()

	list_display = ('title', 'banned', 'metadata',
		'first_and_last_formatted', 'errors_formatted')
	list_filter = ('banned', ErrorsNonEmptyFilter)

	actions = ['refresh', 'ban', 'unban']

admin.site.register(Timeline, TimelineAdmin)
admin.site.register(WpPageProcess, WpPageProcessAdmin)