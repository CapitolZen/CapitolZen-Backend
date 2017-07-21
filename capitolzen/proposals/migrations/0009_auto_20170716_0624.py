# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-16 10:24
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0008_auto_20170707_0613'),
    ]

    operations = [
        migrations.AddField(
            model_name='wrapper',
            name='summary',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='bill',
            name='last_action_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 7, 16, 6, 24, 22, 541673)),
        ),
    ]
