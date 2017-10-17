# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-12 23:45
from __future__ import unicode_literals

import capitolzen.users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_notification_references'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.FileField(blank=True, max_length=255, null=True, upload_to=capitolzen.users.models.avatar_directory_path),
        ),
    ]
