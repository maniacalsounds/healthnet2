# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-10-05 04:29
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('HealthNet', '0007_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='endtime',
            field=models.DateTimeField(default=datetime.datetime(2016, 10, 5, 4, 29, 31, 942000, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
