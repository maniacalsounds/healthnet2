# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-08 17:52
from __future__ import unicode_literals

import HealthNet.models
import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('HealthNet', '0013_auto_20161106_1959'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='endtime',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 8, 13, 22, 46, 185429)),
        ),
        migrations.AlterField(
            model_name='patient',
            name='cur_hospital',
            field=models.ForeignKey(blank=True, default=HealthNet.models.Hospital(3, 'None', 'None'), null=True, on_delete=django.db.models.deletion.CASCADE, related_name='admitted', to='HealthNet.Hospital'),
        ),
    ]
