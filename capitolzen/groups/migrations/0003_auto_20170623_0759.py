# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-23 11:59
from __future__ import unicode_literals

import capitolzen.organizations.mixins
from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_fsm
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0004_auto_20170613_0447'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0002_auto_20170613_0518'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('meta', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('attachments', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('bills', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('scheduled', models.BooleanField(default=False)),
                ('status', django_fsm.FSMField(default='draft', max_length=50)),
                ('publish_date', models.DateTimeField(blank=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groups.Group')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organizations.Organization')),
            ],
            options={
                'verbose_name': 'report',
                'verbose_name_plural': 'reports',
                'abstract': False,
            },
            bases=(models.Model, capitolzen.organizations.mixins.MixinResourcedOwnedByOrganization),
        ),
        migrations.RemoveField(
            model_name='comment',
            name='attachments',
        ),
        migrations.AddField(
            model_name='comment',
            name='documents',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
    ]
