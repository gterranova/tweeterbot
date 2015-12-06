from django.core.management.base import BaseCommand

from tweeterapp.models import TweetStore
import simplejson as json

class Command(BaseCommand):
    help = 'Import tweets from json'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str)
        
    def handle(self, *args, **options):
        f = open(options['filename'], 'r')
        tweets = json.load(f)
        f.close()
        
        entries = []
        for tweet in tweets:
            entries.append(TweetStore(content=tweet[0]))
            
        TweetStore.objects.bulk_create(entries)
        self.stdout.write('Successfully stored %d status' % len(entries))