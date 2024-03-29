# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-24 02:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_notification_references'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='created',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='notification',
            name='modified',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='created',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='user',
            name='modified',
            field=models.DateTimeField(db_index=True),
        ),
    ]
