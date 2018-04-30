from __future__ import unicode_literals
from json import loads

from base64 import b64decode

from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from django_fsm import FSMField, transition
from model_utils import Choices

from hashid_field import HashidAutoField

from capitolzen.organizations.models import Organization
from capitolzen.users.models import User
from django.contrib.auth import get_user_model

from config.models import AbstractBaseModel

from capitolzen.organizations.mixins import MixinResourcedOwnedByOrganization
from capitolzen.groups.mixins import MixinResourceModifiedByPage


def avatar_directory_path(instance, filename):
    """
    Note the need to use the ID here. meaning we can't
    upload files during creation.
    :param instance:
    :param filename:
    :return:
    """
    return '{0}/misc/{1}'.format(instance.organization.id, filename)


class Group(AbstractBaseModel, MixinResourceModifiedByPage, MixinResourcedOwnedByOrganization):
    title = models.CharField(blank=False, max_length=225)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
    )
    avatar = models.FileField(
        blank=True, null=True, max_length=255, upload_to=avatar_directory_path
    )

    assigned_to = models.ManyToManyField(get_user_model(), related_name='assigned_to_users')
    guest_users = models.ManyToManyField(get_user_model(), related_name='guest_users_users')

    def is_guest(self, user):
        return user in self.guest_users.all()

    class JSONAPIMeta:
        resource_name = "groups"

    class Meta:
        abstract = False
        verbose_name = "group"
        verbose_name_plural = "groups"

    def __unicode__(self):
        return self.title


def report_directory_path(instance, filename):
    """
    :param instance:
    :param filename:
    :return:
    """
    return '{0}/reports/{1}'.format(instance.organization.id, filename)


def prepare_report_filters(data):
    output = {}
    if type(data) == 'dict':
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

class Report(AbstractBaseModel, MixinResourceModifiedByPage, MixinResourcedOwnedByOrganization):
    user = models.ForeignKey('users.User', blank=True)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE
    )

    group = models.ForeignKey('groups.Group')
    page = models.ForeignKey('groups.Page', blank=True, null=True)

    attachments = JSONField(blank=True, default=dict)
    filter = JSONField(blank=True, default=dict)
    status = FSMField(default='draft')
    publish_output = models.CharField(blank=True, max_length=255)
    title = models.CharField(default="Generated Report", max_length=255)
    description = models.TextField(blank=True, null=True)
    preferences = JSONField(default=dict)

    report_types = Choices(
        ('scorecard', 'scorecard'),
        ('table', 'table'),
        ('list', 'list'),
        ('slideshow', 'slideshow')
    )

    display_type = models.CharField(choices=report_types, max_length=255, default='list')

    @property
    def file_title(self):
        return "%s-%s" % (self.group.title, self.title)

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


def file_directory_path(instance, filename):
    """
    format directory path for file library
    :param instance:
    :param filename:
    :return string:
    """
    return '{0}/files/{1}'.format(instance.id, filename)


class File(AbstractBaseModel, MixinResourceModifiedByPage, MixinResourcedOwnedByOrganization):
    organization = models.ForeignKey(
        'organizations.Organization', on_delete=models.CASCADE
    )

    group = models.ForeignKey('groups.Group', on_delete=models.CASCADE, null=True, blank=True)

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


def generate_preview():
    return {
        "preview": None,
        "summary": None,
        "pubname": None,
        "keywords": []
    }


class Link(AbstractBaseModel, MixinResourceModifiedByPage, MixinResourcedOwnedByOrganization):
    url = models.URLField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    scraped_data = JSONField(default=generate_preview)
    page = models.ForeignKey('groups.Page', on_delete=models.CASCADE)
    class Meta:
        verbose_name = _("link")
        verbose_name_plural = _("links")

    class JSONAPIMeta:
        resource_name = "links"


class Update(AbstractBaseModel, MixinResourceModifiedByPage, MixinResourcedOwnedByOrganization):
    user = models.ForeignKey('users.User')
    group = models.ForeignKey('groups.Group', on_delete=models.CASCADE, related_name='group')
    page = models.ForeignKey('groups.Page', on_delete=models.CASCADE, related_name='update')
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE)
    files = models.ManyToManyField('groups.File', blank=True, null=True)
    links = models.ManyToManyField('groups.Link', blank=True, null=True)
    wrappers = models.ManyToManyField('proposals.Wrapper', blank=True, null=True)
    reports = models.ManyToManyField('groups.Report', blank=True, null=True)

    document = JSONField(default=dict)
    title = models.TextField(max_length=255)

    published = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("update")
        verbose_name_plural = _("updates")

    class JSONAPIMeta:
        resource_name = "updates"


def create_structured_page_info():
    return {
        "objectives": [],
        "social_links": [],
        "newsletter": {
            "provider": None,
            "id": None
        }
    }

class Page(AbstractBaseModel, MixinResourceModifiedByPage, MixinResourcedOwnedByOrganization):
    id = HashidAutoField(primary_key=True)

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE
    )
    group = models.ForeignKey('groups.Group', on_delete=models.CASCADE)
    author = models.ForeignKey('users.User', blank=True, null=True)
    usage_choices = Choices(
        ('anyone', 'Anyone with link'),
        ('organization', 'Anyone in my org'),
    )
    visibility = models.CharField(choices=usage_choices, default='organization', db_index=True, max_length=255)

    viewers = models.ManyToManyField(get_user_model(), related_name='page_viewer_users')

    title = models.CharField(max_length=255, default='My Group Page')
    description = models.TextField(blank=True, null=True)
    published = models.BooleanField(default=False)

    bill_layout_choices = Choices(
        ('table', 'Table'),
        ('slides', 'slides'),
        ('list', 'list')
    )

    bill_layout = models.CharField(choices=bill_layout_choices, default='table', max_length=255)

    avatar = models.FileField(
        blank=True, null=True, max_length=255, upload_to=avatar_directory_path
    )

    structured_page_info = JSONField(default=create_structured_page_info)

    def is_viewer(self, user):
        return user in self.viewers.all()

    @property
    def allow_anon(self):
        return self.visibility == 'anyone'

    class Meta:
        verbose_name = _("page")
        verbose_name_plural = _("pages")

    class JSONAPIMeta:
        resource_name = "pages"
