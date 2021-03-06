import tweepy
from django.conf import settings
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib import messages

from .models import Tweet


class ImportTweets:

    def __init__(self, request=None):
        self.consumer_key = settings.SOCIAL_AUTH_TWITTER_KEY
        self.consumer_secret = settings.SOCIAL_AUTH_TWITTER_SECRET
        self.request = request
        
    def update_tweets(self):
        users = User.objects.all()
        for user in users:
            self.update_user_tweets(user)

    def update_user_tweets(self, user):
        if user.social_auth.count() > 0:
            raw_tweets = self._get_latest_tweets_from_api(user)
            tweets = [self._tweepy_status_to_tweet(user, status=status) for status in raw_tweets]
            ##self._replace_all_tweets(user, tweets)
                
    def _get_latest_tweets_from_api(self, user):
        """
        http://pythonhosted.org/tweepy/html/index.html
        """
        access_token = user.social_auth.first().access_token
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(access_token['oauth_token'], access_token['oauth_token_secret'])
        try:
            api = tweepy.API(auth)
            timeline = api.user_timeline()
        except tweepy.TweepError, e:
            self.process_exc(e, user)
            return []
        return timeline

    def _tweepy_status_to_tweet(self, user, status):
        """
        Fields documentation: https://dev.twitter.com/docs/api/1.1/get/statuses/home_timeline
        """
        tweet, created = user.twits.get_or_create(twitter_id_str=status.id_str, defaults={'published_at': status.created_at, 'content': status.text})
        
        if tweet.favorite_count != status.favorite_count or tweet.retweet_count != status.retweet_count:
            tweet.favorite_count = status.favorite_count
            tweet.retweet_count = status.retweet_count
            tweet.save()
        
        if hasattr(status, 'retweeted_status'):
            username = status.retweeted_status.author.screen_name
            try:
                retweeted_user = User.objects.get(username=username)
                retweeted_tweet = self._tweepy_status_to_tweet(retweeted_user, status.retweeted_status)
                if user not in list(retweeted_tweet.retwittered_by.all()):
                    retweeted_tweet.retwittered_by.add(user)
                    retweeted_tweet.save()
                    #print "Added %s to tweet %d by %s" % (user, retweeted_tweet.id, username)
            except User.DoesNotExist:
                #print "RT by %s not managed by the app" % (username,)
                pass

        return tweet

    @transaction.atomic
    def _replace_all_tweets(self, user, new_tweets):
        Tweet.objects.remove_all(user)

        for tweet in new_tweets:
            tweet.save()
    
    def process_exc(self, e, user):
        if self.request:
            message = e.message
            for msg in message:
                messages.error(self.request, "(User %s) %s" % (user, msg['message']))
                