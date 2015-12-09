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
        saved_count = 0
        
        entries = []
        for tweet in tweets:
            if len(tweet[0]) < 140:
                saved_count += 1
                entries.append(TweetStore(content=tweet[0]))
            
        TweetStore.objects.bulk_create(entries)
        self.stdout.write('Successfully stored %d out of %d status' % (saved_count, len(entries)))
