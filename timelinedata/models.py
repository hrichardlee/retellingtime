from django.db import models

# Create your models here.
class Timeline(models.Model):
	title = models.CharField(max_length = 500)
	events = models.CharField(max_length = 1000000)

	def __unicode__(self):
		return "Timeline(id: %d, title: %s, events: %s)" \
			% (self.id, self.title, self.events[:30])