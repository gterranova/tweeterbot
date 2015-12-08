from __future__ import unicode_literals
from django.db import models
from django.conf import settings

from django.db.models.aggregates import Count
from random import randint
from django.core.urlresolvers import reverse_lazy
import itertools

class TweetManager(models.Manager):

    def get_all_latest_tweets(self, update=False, request=None):
        if update:
            from import_tweets import ImportTweets
            importer = ImportTweets(request=request)
            importer.update_tweets()
        
        results = itertools.chain(
                self.filter(published_at__isnull=True),
                self.filter(published_at__isnull=False).order_by('-published_at'))
        return list(results)

    def get_latest_tweets(self, user, update=False, request=None):
        if update:
            from import_tweets import ImportTweets
            importer = ImportTweets(request=request)
            importer.update_user_tweets(user)
        
        results = itertools.chain(
                self.filter(author=user, published_at__isnull=True),
                self.filter(author=user, published_at__isnull=False).order_by('-published_at'))
        return list(results)

    def get_unpublished_tweets(self, user):
        return self.filter(author=user, published_at__isnull=True).order_by('-created_at')
        
    def remove_all(self, user):
        self.filter(author=user, published_at__isnull=False).delete()


class Tweet(models.Model):
    """
    Cached imported tweet
    """
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="twits", verbose_name="user")
    content = models.TextField(u"Tweet Content", max_length=20000)
    twitter_id_str = models.CharField(u"Twitter Id", max_length=32, blank=True)    
    retwittered_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='retwits', blank=True)    
    
    # Engagement - not likely to be very useful for streamed tweets but whatever
    favorite_count = models.PositiveIntegerField(null=True, blank=True)
    retweet_count = models.PositiveIntegerField(null=True, blank=True)

    published_at = models.DateTimeField(u"Published At", blank=True, null=True)
    updated_at = models.DateTimeField(u"Last Update", auto_now=True)
    created_at = models.DateTimeField(u"Date", auto_now_add=True)

    objects = TweetManager()

    class Meta:
        verbose_name = 'Tweet'
        verbose_name_plural = 'Tweets'

    def __unicode__(self):
        return self.content

class TweetStoreManager(models.Manager):
    def random(self):
        count = self.filter(used=False).aggregate(count=Count('id'))['count']
        if count > 0:
            random_index = randint(0, count - 1)
            return self.filter(used=False)[random_index]        
        return None
        
class TweetStore(models.Model):
    content = models.TextField(u"Tweet Content", max_length=20000)
    used = models.BooleanField(blank=True, default=False)
    objects = TweetStoreManager()

    class Meta:
        verbose_name = 'Stored Tweet'
        verbose_name_plural = 'Stored Tweets'
        
    def __unicode__(self):
        return self.content
