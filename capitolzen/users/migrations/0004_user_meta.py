# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-07 11:52
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20170728_1543'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='meta',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, null=True),
        ),
    ]