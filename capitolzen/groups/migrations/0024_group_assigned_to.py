# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-19 15:50
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0023_group_group_label'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='assigned_to',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
