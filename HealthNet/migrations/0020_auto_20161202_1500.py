# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-12-02 20:00
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HealthNet', '0019_auto_20161120_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='endtime',
            field=models.DateTimeField(default=datetime.datetime(2016, 12, 2, 15, 30, 37, 119824)),
        ),
    ]
