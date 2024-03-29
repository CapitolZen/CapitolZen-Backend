# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-08 15:43
from __future__ import unicode_literals

from django.db import migrations

def forwards(apps, schema_editor):
    Bill = apps.get_model('proposals', 'Bill')

    for bill in Bill.objects.all().iterator():
        if bill.cosponsors:
            cosponsors = bill.cosponsors
            cosponsors = set(cosponsors)
            bill.cosponsors = list(cosponsors)


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0034_bill_committees'),
    ]

    operations = [
        migrations.RunPython(forwards),
    ]
