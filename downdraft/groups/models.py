from __future__ import unicode_literals
from django.db import models
from config.models import AbstractBaseModel
from dry_rest_permissions.generics import allow_staff_or_superuser
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from downdraft.organizations.mixins import MixinResourcedOwnedByOrganization
from downdraft.meta.billing import CHEAP


class Group(AbstractBaseModel, MixinResourcedOwnedByOrganization):
    title = models.CharField(blank=False, max_length=225)
    description = models.TextField(blank=True)
    contacts = JSONField(blank=True)
    logo = models.URLField(blank=True)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
    )

    class JSONAPIMeta:
        resource_name = "groups"

    class Meta:
        abstract = False
        verbose_name = "group"
        verbose_name_plural = "groups"

    def __unicode__(self):
        return self.title


class Comment(AbstractBaseModel):
    author = models.ForeignKey('users.User', on_delete=models.CASCADE)
    reactions = JSONField(blank=True, null=True)
    attachments = ArrayField(models.URLField(blank=True))
    text = models.TextField()

    VISIBILITY_OPTIONS = (
        ('public', 'anyone'),
        ('group', 'just group contacts'),
        ('private', 'just organization')
    )

    visibility = models.CharField(
        choices=VISIBILITY_OPTIONS,
        max_length=255
    )

    referenced_id = models.UUIDField()
    referenced_object = GenericForeignKey('content_type', 'referenced_id')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    class JSONAPIMeta:
        resource_name = "comments"

    class Meta:
        abstract = False
        verbose_name = "comment"
        verbose_name_plural = "comments"
