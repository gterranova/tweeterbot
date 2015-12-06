import tweepy
from django.conf import settings
from django.db import transaction
from django.contrib.auth.models import User

from .models import Tweet


class ImportTweets:

    def __init__(self):
        self.consumer_key = settings.SOCIAL_AUTH_TWITTER_KEY
        self.consumer_secret = settings.SOCIAL_AUTH_TWITTER_SECRET

    def update_tweets(self):
        users = User.objects.all()
        for user in users:
            if user.social_auth.count() > 0:
                raw_tweets = self._get_latest_tweets_from_api(user)
                tweets = [self._tweepy_status_to_tweet(user, status=status) for status in raw_tweets]
                self._replace_all_tweets(user, tweets)

    def update_user_tweets(self, user):
        if user.social_auth.count() > 0:
            raw_tweets = self._get_latest_tweets_from_api(user)
            tweets = [self._tweepy_status_to_tweet(user, status=status) for status in raw_tweets]
            self._replace_all_tweets(user, tweets)
                
    def _get_latest_tweets_from_api(self, user):
        """
        http://pythonhosted.org/tweepy/html/index.html
        """
        access_token = user.social_auth.first().access_token
        auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(access_token['oauth_token'], access_token['oauth_token_secret'])
        api = tweepy.API(auth)

        return api.user_timeline()

    def _tweepy_status_to_tweet(self, user, status):
        """
        Fields documentation: https://dev.twitter.com/docs/api/1.1/get/statuses/home_timeline
        """
        tweet = Tweet()
        tweet.author = user
        tweet.twitter_id_str = status.id_str
        tweet.published_at = status.created_at
        tweet.content = status.text

        return tweet

    @transaction.atomic
    def _replace_all_tweets(self, user, new_tweets):
        Tweet.objects.remove_all(user)

        for tweet in new_tweets:
            tweet.save()
