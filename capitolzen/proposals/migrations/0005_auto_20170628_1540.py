# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-28 19:40
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0004_auto_20170623_0758'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bill',
            old_name='committee',
            new_name='current_committee',
        ),
        migrations.AddField(
            model_name='bill',
            name='versions',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
    ]
