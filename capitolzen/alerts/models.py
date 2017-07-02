from django.contrib.auth.models import AbstractUser
from config.models import AbstractBaseModel
from django.db import models
from dry_rest_permissions.generics import allow_staff_or_superuser
from capitolzen.organizations.models import Organization
from capitolzen.groups.models import Group
from capitolzen.users.models import User


class Alerts(AbstractBaseModel):

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    message = models.TextField()

    class Meta:
        abstract = False
        verbose_name = "alert"
        verbose_name_plural = "alert"

    class JSONAPIMeta:
        resource_name = "alerts"

    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_write_permission(request):
        return False

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return True

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        return True

    @allow_staff_or_superuser
    def has_object_create_permission(self, request):
        return True
