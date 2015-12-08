from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from random import shuffle
from django.conf import settings
from django.core.mail import send_mail

import tweepy
from tweeterapp.models import Tweet, TweetStore

class Command(BaseCommand):
    help = 'Post random tweet from store'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument('--user',
            action='store',
            dest='user',
            default=False,
            help='Post as the specified user')        
            
    def handle(self, *args, **options):
        
        if options['user']:
            available_users = list(get_user_model().objects.filter(username=options['user']))
        else:
            available_users = list(get_user_model().objects.filter(is_staff=False).exclude(social_auth__iexact=None))
            
        shuffle(available_users)
        user = available_users[0]
        random_tweet = TweetStore.objects.random()
        
        consumer_key = settings.SOCIAL_AUTH_TWITTER_KEY
        consumer_secret = settings.SOCIAL_AUTH_TWITTER_SECRET
        access_token = user.social_auth.first().access_token
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token['oauth_token'], access_token['oauth_token_secret'])
        api = tweepy.API(auth)

        tweet = Tweet()
        tweet.author = user
        try:
            status = api.update_status(random_tweet.content)
            tweet.twitter_id_str = status.id_str
            tweet.published_at = status.created_at
            tweet.content = status.text
            tweet.save()
            random_tweet.used = True
            random_tweet.save()
            message = 'Successfully posted "%s" for user %s' % (random_tweet.content, user)
            send_mail("[SocialTrumpet] New tweet from %s" % user, message, settings.DEFAULT_FROM_EMAIL, ['gianpaoloterranova@gmail.com','info@ema.mu'])
            self.stdout.write(message)
            
        except tweepy.TweepError, e:
            message = e.message
            output = []
            for msg in message:
                output.append('Error: User %s: %s' % (user, msg['message']))
            message = '\n'.join(output)
            send_mail("[SocialTrumpet] Error posting tweet for %s" % user, message, settings.DEFAULT_FROM_EMAIL, ['gianpaoloterranova@gmail.com','info@ema.mu'])            
            self.stderr.write(message)
