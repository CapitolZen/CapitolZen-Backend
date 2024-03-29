# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-07 10:13
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0006_auto_20170703_0827'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='saved_filters',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='report',
            name='recurring',
            field=models.BooleanField(default=False),
        ),
    ]
