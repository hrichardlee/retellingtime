from django.db import models

# Create your models here.
class Timeline(models.Model):
	title = models.CharField(max_length = 500)
	events = models.CharField(max_length = 1000000)
	separate = models.BooleanField()

	def __unicode__(self):
		return "Timeline(id: %d, title: %s, separate: %s, events: %s)" \
			% (self.id, self.title, self.separate, self.events[:30])