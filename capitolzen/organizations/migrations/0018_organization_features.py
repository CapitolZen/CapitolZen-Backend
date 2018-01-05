# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-03 18:46
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0017_auto_20171107_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='features',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=list),
        ),
    ]