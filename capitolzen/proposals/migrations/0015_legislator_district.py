# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-28 18:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0014_auto_20170728_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='legislator',
            name='district',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
