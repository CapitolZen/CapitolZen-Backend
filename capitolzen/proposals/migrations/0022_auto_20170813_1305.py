# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-13 17:05
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0021_bill_bill_versions'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bill',
            old_name='meta',
            new_name='metadata',
        ),
        migrations.RenameField(
            model_name='committee',
            old_name='meta',
            new_name='metadata',
        ),
        migrations.RenameField(
            model_name='legislator',
            old_name='meta',
            new_name='metadata',
        ),
        migrations.RenameField(
            model_name='wrapper',
            old_name='meta',
            new_name='metadata',
        ),
    ]
