from django.contrib import admin
from timelinedata.models import Timeline
from timelineprocessor import wikipediaprocess


class TimelineAdmin(admin.ModelAdmin):
	def refresh(modeladmin, request, queryset):
		for timeline in queryset:
			timeline.events = wikipediaprocess.wp_page_to_json(timeline.title, timeline.separate)
			timeline.save()

	actions = ["refresh"]

admin.site.register(Timeline, TimelineAdmin)