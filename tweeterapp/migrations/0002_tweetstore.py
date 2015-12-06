# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tweeterapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TweetStore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(max_length=20000, verbose_name='Tweet Content')),
                ('used', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Stored Tweet',
                'verbose_name_plural': 'Stored Tweets',
            },
        ),
    ]
