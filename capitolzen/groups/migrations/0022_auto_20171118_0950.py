# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-18 14:50
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0021_file_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='starred',
        ),
        migrations.AddField(
            model_name='group',
            name='user_list',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(blank=True, null=True), default=list, size=None),
        ),
    ]
