# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-22 19:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0008_auto_20170722_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='publish_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]