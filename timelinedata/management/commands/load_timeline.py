from django.core.management import BaseCommand
from timelinedata.models import Timeline
from optparse import make_option

from timelineprocessor import parsedate


class Command(BaseCommand):
    help = 'Populate a single timeline'
    option_list = BaseCommand.option_list +\
                  (make_option('--title', dest='title'),)

    def handle(self, *args, **options):
        # Timeline.process_wikipedia_page(options['title'], True)
        # Timeline.process_wikipedia_page('Timeline_of_\'s-Hertogenbosch', True)
        Timeline.process_wikipedia_page('Timeline_of_World_War_II', True)

