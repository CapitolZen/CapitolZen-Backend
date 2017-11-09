# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-08 09:12
from __future__ import unicode_literals

import capitolzen.groups.models
import capitolzen.organizations.mixins
from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0017_auto_20171107_1433'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0019_auto_20171102_0722'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('created', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file', models.FileField(blank=True, max_length=255, null=True, upload_to=capitolzen.groups.models.file_directory_path)),
                ('user_path', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('name', models.CharField(max_length=255)),
                ('visibility', models.CharField(choices=[('public', 'Public'), ('org', 'Private to organization')], db_index=True, default='org', max_length=225)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organizations.Organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'file',
                'verbose_name_plural': 'files',
            },
            bases=(models.Model, capitolzen.organizations.mixins.MixinResourcedOwnedByOrganization),
        ),
    ]