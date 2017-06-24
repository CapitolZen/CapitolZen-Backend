from django.contrib.auth.models import AbstractUser
from config.models import AbstractBaseModel
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from dry_rest_permissions.generics import allow_staff_or_superuser


class Alerts(AbstractBaseModel):

    user = models.ForeignKey('users.User',)
    message = models.TextField()

    def __str__(self):
        return self.message

    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_write_permission(request):
        return False

    @staticmethod
    def has_create_permission(request):
        return True

    def has_object_read_permission(self, request):
        return True

    def has_object_write_permission(self, request):
        return True

    def has_object_create_permission(self, request):
        return True
