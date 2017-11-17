from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser

from dry_rest_permissions.generics import allow_staff_or_superuser

from config.models import AbstractNoIDModel, AbstractBaseModel


def avatar_directory_path(instance, filename):
    """
    Note the need to use the ID here. meaning we can't
    upload files during creation.
    :param instance:
    :param filename:
    :return:
    """
    return '{0}/misc/{1}'.format(instance.id, filename)


class User(AbstractUser, AbstractNoIDModel):
    first_name = None
    last_name = None

    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    metadata = JSONField(default=dict, null=True, blank=True)
    avatar = models.FileField(
        blank=True, null=True, max_length=255,
        upload_to=avatar_directory_path
    )

    def __str__(self):
        return self.name or self.username

    class JSONAPIMeta:
        resource_name = "users"

    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        if request.user.is_anonymous:
            return False

        return True

    def has_object_read_permission(self, request):

        # Can be read if user is current user
        if request.user == self:
            return True

        # Can be read if user is in same organization as current organization
        # request.organization already validates the request.user is in the org.
        return request.organization and request.organization.organization_users.filter(user=self)

    @staticmethod
    @allow_staff_or_superuser
    def has_write_permission(request):
        if request.user.is_anonymous:
            return False

        return True

    def has_object_write_permission(self, request):
        return request.user == self

    @staticmethod
    def has_create_permission(request):
        return False

    def has_object_create_permission(self, request):
        return False

    @staticmethod
    def has_change_password_permission(request):
        if request.user.is_anonymous:
            return False

        return True

    def has_object_change_password_permission(self, request):
        return request.user == self

    @staticmethod
    def has_change_status_permission(request):
        if request.user.is_anonymous:
            return False

        if not request.organization:
            return False

        return True

    def has_object_change_status_permission(self, request):
        if request.user.is_anonymous:
            return False

        if not request.organization:
            return False

        if request.user == self:
            return False

        if request.organization.is_admin(request.user) or request.organization.is_owner(request.user):
            return True

        return False

    @staticmethod
    def has_change_organization_role_permission(request):
        if request.user.is_anonymous:
            return False

        if not request.organization:
            return False

        return True

    def has_object_change_organization_role_permission(self, request):
        if request.user.is_anonymous:
            return False

        if not request.organization:
            return False

        if request.user == self:
            return False

        if request.organization.is_admin(request.user) or request.organization.is_owner(request.user):
            return True

        return False


