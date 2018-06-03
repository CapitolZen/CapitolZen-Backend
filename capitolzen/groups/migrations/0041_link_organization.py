# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-05-16 18:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0022_organizationuser_is_guest'),
        ('groups', '0040_page_structured_page_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organizations.Organization'),
        ),
    ]