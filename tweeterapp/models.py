from __future__ import unicode_literals
from django.db import models
from django.conf import settings

class TweetManager(models.Manager):

    def get_latest_tweets(self, user, offset=0, limit=10, update=False):
        if update:
            from import_tweets import ImportTweets
            importer = ImportTweets()
            importer.update_user_tweets(user)
        
        return self.filter(author=user).order_by('-published_at')[offset:limit]

    def get_unpublished_tweets(self, user, offset=0, limit=10):
        return self.filter(author=user, published_at__isnull=True).order_by('-created_at')[offset:limit]
        
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
    published_at = models.DateTimeField(u"Published At", blank=True, null=True)
    updated_at = models.DateTimeField(u"Last Update", auto_now=True)
    created_at = models.DateTimeField(u"Date", auto_now_add=True)

    objects = TweetManager()

    class Meta:
        verbose_name = 'Tweet'
        verbose_name_plural = 'Tweets'

    def __unicode__(self):
        return self.content