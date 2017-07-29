# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-28 19:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0015_legislator_district'),
    ]

    operations = [
        migrations.RenameField(
            model_name='committee',
            old_name='title',
            new_name='parent_id',
        ),
        migrations.AlterField(
            model_name='bill',
            name='current_committee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='proposals.Committee'),
        ),
    ]