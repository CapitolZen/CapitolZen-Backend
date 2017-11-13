from __future__ import unicode_literals
from json import loads

from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from django_fsm import FSMField, transition
from model_utils import Choices

from capitolzen.organizations.models import Organization
from capitolzen.users.models import User

from config.models import AbstractBaseModel

from capitolzen.organizations.mixins import MixinResourcedOwnedByOrganization


def avatar_directory_path(instance, filename):
    """
    Note the need to use the ID here. meaning we can't
    upload files during creation.
    :param instance:
    :param filename:
    :return:
    """
    return '{0}/misc/{1}'.format(instance.organization.id, filename)


class Group(AbstractBaseModel, MixinResourcedOwnedByOrganization):
    title = models.CharField(blank=False, max_length=225)
    description = models.TextField(blank=True, null=True)
    contacts = JSONField(blank=True, null=True)
    avatar = models.FileField(
        blank=True, null=True, max_length=255, upload_to=avatar_directory_path
    )
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


def report_diretory_path(instance, filename):
    """
    :param instance:
    :param filename:
    :return:
    """
    return '{0}/reports/{1}'.format(instance.organization.id, filename)


# TODO Permissions
class Report(AbstractBaseModel, MixinResourcedOwnedByOrganization):
    user = models.ForeignKey('users.User', blank=True)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE
    )
    group = models.ForeignKey('groups.Group')
    attachments = JSONField(blank=True, default=dict)
    filter = JSONField(blank=True, default=dict)
    scheduled = models.BooleanField(default=False)
    status = FSMField(default='draft')
    static = models.BooleanField(default=False)
    publish_date = models.DateTimeField(blank=True, null=True)
    publish_output = models.CharField(blank=True, max_length=255)
    title = models.CharField(default="Generated Report", max_length=255)
    description = models.TextField(blank=True, null=True)
    template = JSONField(default=dict)
    recurring = models.BooleanField(default=False)
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

    def prepared_filters(self):
        if not self.filter:
            return None
        return prepare_report_filters(self.filter)


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


def prepare_report_filters(data, is_dict=False):
    output = {}

    if is_dict:
        filters = data
    else:
        filters = loads(data)

    for key, value in filters.items():
        if key.endswith('__range'):
            output[key] = value.split(',')
            continue
        if value.startswith('{') and value.endswith('}'):
            output[key] = '2006-01-01'
            continue
        output[key] = value

    return output


def file_directory_path(instance, filename):
    """
    format directory path for file library
    :param instance:
    :param filename:
    :return string:
    """
    return '{0}/files/{1}'.format(instance.id, filename)


class File(AbstractBaseModel, MixinResourcedOwnedByOrganization):
    organization = models.ForeignKey(
        'organizations.Organization', on_delete=models.CASCADE
    )
    user = models.ForeignKey('users.User')
    file = models.FileField(
        max_length=255, null=True, blank=True,
        upload_to=file_directory_path
    )
    user_path = models.CharField(
        default='', max_length=255, blank=True, null=True
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    visibility_choices = Choices(
        ('public', 'Public'),
        ('org', 'Private to organization')
    )

    visibility = models.CharField(
        choices=visibility_choices, max_length=225, default='org', db_index=True
    )

    class Meta:
        verbose_name = _("file")
        verbose_name_plural = _("files")

    class JSONAPIMeta:
        resource_name = "files"
