from django.core.management import BaseCommand
from timelinedata.models import Timeline


class Command(BaseCommand):
    help = 'Populate timelines from search'

    def handle(self, *args, **options):
        Timeline.populate_from_search()
