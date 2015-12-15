from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from tweet_master.exceptions import AlreadyExistsError

from django.core.cache import cache
from django.core.exceptions import ValidationError


AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

CACHE_TYPES = {
    'slaves': 'sl-%d',
    'masters': 'ld-%d',
}

BUST_CACHES = {
    'slaves': ['slaves'],
    'masters': ['masters'],
}


def cache_key(type, user_pk):
    """
    Build the cache key for a particular type of cached value
    """
    return CACHE_TYPES[type] % user_pk


def bust_cache(type, user_pk):
    """
    Bust our cache for a given type, can bust multiple caches
    """
    bust_keys = BUST_CACHES[type]
    keys = [CACHE_TYPES[k] % user_pk for k in bust_keys]
    cache.delete_many(keys)

class TweetMasterRelationshipManager(models.Manager):
    """ serving manager """

    def slaves(self, user):
        """ Return a list of all slaves """
        key = cache_key('slaves', user.pk)
        slaves = cache.get(key)

        if slaves is None:
            qs = self.filter(master=user).all()
            slaves = [u.slave for u in qs]
            cache.set(key, slaves)

        return slaves

    def masters(self, user):
        """ Return a list of all users the given user serves """
        key = cache_key('masters', user.pk)
        masters = cache.get(key)

        if masters is None:
            qs = self.filter(slave=user).all()
            masters = [u.master for u in qs]
            cache.set(key, masters)

        return masters

    def add_slave(self, slave, master):
        """ Create 'slave' serves 'master' relationship """
        if slave == master:
            raise ValidationError("Users cannot serve themselves")

        relation, created = self.get_or_create(slave=slave, master=master)

        if created is False:
            raise AlreadyExistsError("User '%s' already serves '%s'" % (slave, master))

        #slave_created.send(sender=self, slave=slave)
        #master_created.send(sender=self, master=master)
        #masters_created.send(sender=self, master=relation)

        bust_cache('slaves', master.pk)
        bust_cache('masters', slave.pk)

        return relation

    def remove_slave(self, slave, master):
        """ Remove 'slave' serves 'master' relationship """
        try:
            rel = self.get(slave=slave, master=master)
            #slave_removed.send(sender=rel, slave=rel.slave)
            #master_removed.send(sender=rel, master=rel.master)
            #masters_removed.send(sender=rel, serving=rel)
            rel.delete()
            bust_cache('slaves', master.pk)
            bust_cache('masters', slave.pk)
            return True
        except TweetMasterRelationship.DoesNotExist:
            return False

    def serves(self, slave, master):
        """ Does slave follow master? Smartly uses caches if exists """
        slaves = cache.get(cache_key('masters', slave.pk))
        masters = cache.get(cache_key('slaves', master.pk))

        if slaves and master in slaves:
            return True
        elif masters and slave in masters:
            return True
        else:
            try:
                self.get(slave=slave, master=master)
                return True
            except TweetMasterRelationship.DoesNotExist:
                return False


@python_2_unicode_compatible
class TweetMasterRelationship(models.Model):
    """ Model to represent masters relationships """
    slave = models.ForeignKey(AUTH_USER_MODEL, related_name='serving')
    master = models.ForeignKey(AUTH_USER_MODEL, related_name='leading')
    created = models.DateTimeField(default=timezone.now)

    objects = TweetMasterRelationshipManager()

    class Meta:
        verbose_name = 'Master/Slave Relationship'
        verbose_name_plural = 'Master/Slave Relationships'
        unique_together = ('slave', 'master')

    def __str__(self):
        return "User #%d is slave of #%d" % (self.slave_id, self.master_id)

    def save(self, *args, **kwargs):
        # Ensure users can't be friends with themselves
        if self.slave == self.master:
            raise ValidationError("Users cannot serve themselves.")
        super(TweetMasterRelationship, self).save(*args, **kwargs)
