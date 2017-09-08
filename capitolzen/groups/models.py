from __future__ import unicode_literals
from json import dumps
from django.db import models
from config.models import AbstractBaseModel
from django.contrib.postgres.fields import JSONField, ArrayField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django_fsm import FSMField, transition
from capitolzen.organizations.mixins import MixinResourcedOwnedByOrganization
from stream_django.activity import Activity


class Group(AbstractBaseModel, MixinResourcedOwnedByOrganization):
    title = models.CharField(blank=False, max_length=225)
    description = models.TextField(blank=True, null=True)
    contacts = JSONField(blank=True, null=True)
    logo = models.URLField(blank=True, null=True)
    starred = models.BooleanField(default=False)
    attachments = JSONField(blank=True, null=True)
    saved_filters = JSONField(default=dict)
    active = models.BooleanField(default=True)

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


# TODO Permissions
class Report(AbstractBaseModel, MixinResourcedOwnedByOrganization):
    user = models.ForeignKey('users.User', blank=True)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE)
    group = models.ForeignKey('groups.Group')
    attachments = JSONField(blank=True, default=dict)
    filter = JSONField(blank=True, default=dict)
    scheduled = models.BooleanField(default=False)
    status = FSMField(default='draft')
    static = models.BooleanField(default=False)
    publish_date = models.DateTimeField(blank=True, null=True)
    publish_output = models.CharField(blank=True, max_length=255)
    title = models.CharField(default="Generated Report", max_length=255)
    description = models.TextField(blank=True)
    template = JSONField(default=dict)
    recurring = models.BooleanField(default=False)
    update_frequency = models.CharField(blank=True, max_length=255, null=True)
    preferences = JSONField(default=dict)
    static_list = ArrayField(models.TextField(), blank=True, null=True)

    class JSONAPIMeta:
        resource_name = "reports"

    class Meta:
        abstract = False
        verbose_name = "report"
        verbose_name_plural = "reports"

    @transition(field=status, source='draft', target='published')
    def publish(self):
        # TODO notifications
        pass


class Comment(AbstractBaseModel):
    author = models.ForeignKey('users.User', on_delete=models.CASCADE)
    reactions = JSONField(blank=True, null=True)
    text = models.TextField()
    documents = JSONField(blank=True, default=dict)

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
