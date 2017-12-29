# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-24 20:35
from __future__ import unicode_literals

from django.db import migrations, models
from django.core.exceptions import MultipleObjectsReturned


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0039_auto_20171130_0348'),
    ]

    def forwards(apps, schema_editor):
        Legislator = apps.get_model('proposals', 'Legislator')
        for legislator in Legislator.objects.all().iterator():
            try:
                Legislator.objects.get(remote_id=legislator.remote_id)
            except MultipleObjectsReturned:
                response = Legislator.objects.filter(
                    remote_id=legislator.remote_id
                )
                for leg in response[1:]:
                    leg.delete()

    operations = [
        migrations.RunPython(forwards),
    ]
