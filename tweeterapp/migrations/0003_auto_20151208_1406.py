# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tweeterapp', '0002_tweetstore'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='favorite_count',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='tweet',
            name='retweet_count',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
    ]
