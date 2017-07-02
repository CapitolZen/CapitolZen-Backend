from django.contrib.auth.models import AbstractUser
from config.models import AbstractBaseModel
from django.db import models
from dry_rest_permissions.generics import allow_staff_or_superuser


class Alerts(AbstractBaseModel):

    message = models.TextField()
    user = models.TextField()
    organization = models.TextField()
    group = models.TextField()

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
