from django.contrib import admin
from timelinedata.models import Timeline
from timelineprocessor import wikipediaprocess


class TimelineAdmin(admin.ModelAdmin):
	def refresh(modeladmin, request, queryset):
		for timeline in queryset:
			timeline.get_events()
			timeline.save()

	actions = ["refresh"]

admin.site.register(Timeline, TimelineAdmin)