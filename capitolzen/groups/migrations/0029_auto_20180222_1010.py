# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-02-22 15:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0028_reportlink'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='publish_date',
        ),
        migrations.RemoveField(
            model_name='report',
            name='scheduled',
        ),
        migrations.RemoveField(
            model_name='report',
            name='static',
        ),
        migrations.RemoveField(
            model_name='report',
            name='static_list',
        ),
        migrations.AddField(
            model_name='report',
            name='report_type',
            field=models.CharField(choices=[('details', 'details'), ('scorecard', 'scorecard'), ('overview', 'overview'), ('latest', 'latest')], default='details', max_length=255),
        ),
    ]
