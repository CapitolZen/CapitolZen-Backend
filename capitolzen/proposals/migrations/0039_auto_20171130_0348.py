# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-30 08:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0038_auto_20171127_0525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='publish_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]