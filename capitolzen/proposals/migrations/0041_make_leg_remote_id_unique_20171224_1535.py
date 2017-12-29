# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-24 20:35
from __future__ import unicode_literals

from django.db import migrations, models
from django.core.exceptions import MultipleObjectsReturned


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0040_auto_20171224_1535'),
    ]
    operations = [
        migrations.AlterField(
            model_name='legislator',
            name='remote_id',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='wrapper',
            name='position',
            field=models.CharField(blank=True, default='neutral', max_length=255),
        ),
    ]
