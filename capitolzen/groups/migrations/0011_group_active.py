# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-05 11:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0010_report_update_frequency'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
