# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-04 14:39
from __future__ import unicode_literals

import config.fields
from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import organizations.base
import organizations.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('meta', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('name', models.CharField(help_text='The name of the organization', max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('created', organizations.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False)),
                ('modified', organizations.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False)),
                ('slug', organizations.fields.SlugField(blank=True, editable=False, help_text='The name in all lowercase, suitable for URL identification', max_length=200, populate_from='name', unique=True)),
                ('features', config.fields.ChoiceArrayField(base_field=models.CharField(choices=[('feat_a', 'A'), ('feat_b', 'B'), ('feat_c', 'C')], max_length=256), default=list, size=None)),
            ],
            options={
                'verbose_name': 'organization',
                'verbose_name_plural': 'organizations',
                'ordering': ['name'],
                'abstract': False,
            },
            bases=(organizations.base.UnicodeMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OrganizationInvite',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('meta', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('status', models.CharField(choices=[('claimed', 'Claimed'), ('unclaimed', 'Unclaimed'), ('revoked', 'Revoked')], max_length=254)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organizations.Organization')),
            ],
            options={
                'verbose_name': 'invite',
                'verbose_name_plural': 'invites',
            },
        ),
        migrations.CreateModel(
            name='OrganizationOwner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', organizations.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False)),
                ('modified', organizations.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False)),
                ('organization', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='owner', to='organizations.Organization')),
            ],
            options={
                'verbose_name': 'organization owner',
                'verbose_name_plural': 'organization owners',
                'abstract': False,
            },
            bases=(organizations.base.UnicodeMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OrganizationUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', organizations.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False)),
                ('modified', organizations.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organization_users', to='organizations.Organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organizations_organizationuser', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'organization user',
                'verbose_name_plural': 'organization users',
                'ordering': ['organization', 'user'],
                'abstract': False,
            },
            bases=(organizations.base.UnicodeMixin, models.Model),
        ),
        migrations.AddField(
            model_name='organizationowner',
            name='organization_user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='organizations.OrganizationUser'),
        ),
        migrations.AddField(
            model_name='organization',
            name='users',
            field=models.ManyToManyField(related_name='organizations_organization', through='organizations.OrganizationUser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='organizationuser',
            unique_together=set([('user', 'organization')]),
        ),
    ]
