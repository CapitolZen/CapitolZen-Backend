# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-03-06 15:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0033_auto_20180305_1451'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='update',
            name='status',
        ),
        migrations.AddField(
            model_name='update',
            name='published',
            field=models.BooleanField(default=False),
        ),
    ]