# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-02-06 16:38
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0025_remove_group_user_list'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='contacts',
        ),
        migrations.RemoveField(
            model_name='group',
            name='group_label',
        ),
        migrations.RemoveField(
            model_name='group',
            name='saved_filters',
        ),
    ]