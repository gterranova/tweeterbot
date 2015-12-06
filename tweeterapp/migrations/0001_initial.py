# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(max_length=20000, verbose_name='Tweet Content')),
                ('twitter_id_str', models.CharField(max_length=32, verbose_name='Twitter Id', blank=True)),
                ('published_at', models.DateTimeField(null=True, verbose_name='Published At', blank=True)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Last Update')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date')),
                ('author', models.ForeignKey(related_name='twits', verbose_name='user', to=settings.AUTH_USER_MODEL)),
                ('retwittered_by', models.ManyToManyField(related_name='retwits', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'verbose_name': 'Tweet',
                'verbose_name_plural': 'Tweets',
            },
        ),
    ]
