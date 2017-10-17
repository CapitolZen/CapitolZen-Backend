# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-02 00:43
from __future__ import unicode_literals

import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0023_auto_20170923_2242'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='created_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='bill',
            name='updated_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='bill',
            name='bill_versions',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='bill',
            name='companions',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(blank=True), blank=True, default=list, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='bill',
            name='current_version',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='bill',
            name='documents',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='bill',
            name='sources',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='bill',
            name='sponsors',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name='bill',
            name='title',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='bill',
            name='votes',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True),
        ),
    ]