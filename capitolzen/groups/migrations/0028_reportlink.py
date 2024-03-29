# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-02-22 14:11
from __future__ import unicode_literals

import capitolzen.organizations.mixins
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import hashid_field.field


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0021_auto_20180118_0605'),
        ('groups', '0027_remove_group_attachments'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportLink',
            fields=[
                ('created', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('id', hashid_field.field.HashidAutoField(alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890', min_length=7, primary_key=True, serialize=False)),
                ('view_counter', models.IntegerField(default=0)),
                ('visibility', models.CharField(choices=[('unlimited', 'Anyone with link'), ('organization', 'Anyone in my org'), ('once', 'just once'), ('contacts', 'in list of emails')], db_index=True, default='organization', max_length=255)),
                ('contact_list', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=255, null=True), size=None)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groups.Group')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organizations.Organization')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groups.Report')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, capitolzen.organizations.mixins.MixinResourcedOwnedByOrganization),
        ),
    ]
