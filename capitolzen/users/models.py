from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser
from model_utils.models import TimeStampedModel
from config.models import AbstractBaseModel
from dry_rest_permissions.generics import allow_staff_or_superuser


class User(AbstractUser, TimeStampedModel):
    first_name = None
    last_name = None

    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    metadata = JSONField(default=dict, null=True, blank=True)

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
        return request.user.id == self.id

    @staticmethod
    @allow_staff_or_superuser
    def has_write_permission(request):
        if request.user.is_anonymous:
            return False

        return True

    def has_object_write_permission(self, request):
        return request.user.id == self.id


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
        return request.user.id == self.id


class Notification(AbstractBaseModel):
    references = JSONField(default=list, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    message = models.TextField()
    notification_type = models.CharField(max_length=255, default="user")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = False
        verbose_name = "notification"
        verbose_name_plural = "notifications"

    class JSONAPIMeta:
        resource_name = "notification"

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
        return False

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return self.user == request.user

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        return self.user == request.user

    @allow_staff_or_superuser
    def has_object_create_permission(self, request):
        return False
