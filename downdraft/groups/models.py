from __future__ import unicode_literals
from django.db import models
from config.models import AbstractBaseModel
from dry_rest_permissions.generics import allow_staff_or_superuser
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from downdraft.meta.billing import CHEAP


class Group(AbstractBaseModel):
    title = models.CharField(blank=False)
    description = models.TextField(blank=True)
    contacts = JSONField()
    logo = models.URLField()
    organization = models.ForeignKey(
        'organizations',
        on_delete=models.CASCADE,
    )

    class JSONAPIMeta:
        resource_name = "groups"

    class Meta(self):
        abstract = False
        verbose_name = _("group")
        verbose_name_plural = _("groups")

    def __unicode__(self):
        return self.title

    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return request.user.is_authenticated()

    @staticmethod
    @allow_staff_or_superuser
    def has_write_permission(request):
        return request.user.is_authenticated()

    @staticmethod
    def has_create_permission(request):
        if request.organization.plan_type is not CHEAP:
            allowed = True
        else:
            allowed = False

        return request.organization.user.is_staff or request.user.is_superuser or allowed

    def has_object_read_permission(self, request):
        return self.organization.is_member(request.user) or \
               request.user.is_staff or \
               request.user.is_superuser

    def has_object_write_permission(self, request):
        return self.organization.user.is_admin() or \
               self.organization.user.is_owner() or \
               request.user.is_staff or \
               request.user.is_superuser

    def has_object_update_permission(self, request):
        return self.organization.user.is_admin or request.user.is_staff or request.user.is_superuser


class Comment(AbstractBaseModel):
    author = models.ForeignKey('User', on_delete=models.CASCADE)
    reactions = JSONField()
    attachments = ArrayField(models.URLField(blank=True))
    text = models.TextField()

    VISIBILITY_OPTIONS = (
        ('public', 'anyone'),
        ('group', 'just group contacts'),
        ('private', 'just organization')
    )

    visibility = models.CharField(
        choices= VISIBILITY_OPTIONS,
        max_length=255
    )

    referenced_id = models.UUIDField
    referenced_object = GenericForeignKey('content_type', 'reference_id')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)

    class JSONAPIMeta:
        resource_name = "comments"

    class Meta(self):
        abstract = False
        verbose_name = _("comment")
        verbose_name_plural = _("comments")
