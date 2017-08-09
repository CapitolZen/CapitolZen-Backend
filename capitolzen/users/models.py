from django.contrib.auth.models import AbstractUser
from config.models import AbstractBaseModel
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from dry_rest_permissions.generics import allow_staff_or_superuser

@python_2_unicode_compatible
class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    meta = JSONField(null=True, default=dict)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    @property
    def user_is_admin(self):
        return self.is_superuser

    @property
    def user_is_staff(self):
        return self.is_staff

    class JSONAPIMeta:
        resource_name = "users"

    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_write_permission(request):
        return True

    @staticmethod
    def has_create_permission(request):
        return True

    def has_object_read_permission(self, request):
        return request.user.id == self.id

    def has_object_write_permission(self, request):
        return request.user.id == self.id

    def has_object_create_permission(self, request):
        return request.user.id == self.id


class Alert(AbstractBaseModel):

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    references = JSONField(default=dict, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    message = models.TextField()

    @property
    def bill_id(self):
        model = self.references.get("model", False)
        if model is not "bill":
            return False
        return self.references.get("id")

    def set_type(self, model):
        t = type(model)
        data = self.references
        data["model"] = t
        data["references"] = model.id
        self.references = data
        self.save()

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
