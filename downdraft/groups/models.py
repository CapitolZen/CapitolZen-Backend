from __future__ import unicode_literals
from django.db import models
from config.models import AbstractBaseModel
from dry_rest_permissions.generics import allow_staff_or_superuser
from django.contrib.postgres.fields import ArrayField, JSONField


class Group(AbstractBaseModel):
    name = models.CharField(blank=False)
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
        return self.name

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
        return request.user.is_authenticated()

    def has_object_read_permission(self, request):
        return self.organization.is_member(request.user) or \
               request.user.is_staff or \
               request.user.is_superuser

    def has_object_write_permission(self, request):
        return self.organization.is_admin(request.user) or \
               self.organization.is_owner(request.user) or \
               request.user.is_staff or \
               request.user.is_superuser

    def has_object_create_permission(self, request):
        return request.user.is_authenticated()
