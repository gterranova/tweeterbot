# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TweetMasterRelationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('master', models.ForeignKey(related_name='leading', to=settings.AUTH_USER_MODEL)),
                ('slave', models.ForeignKey(related_name='serving', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Master/Slave Relationship',
                'verbose_name_plural': 'Master/Slave Relationships',
            },
        ),
        migrations.AlterUniqueTogether(
            name='tweetmasterrelationship',
            unique_together=set([('slave', 'master')]),
        ),
    ]
