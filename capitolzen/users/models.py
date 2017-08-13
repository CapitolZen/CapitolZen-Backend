import hashlib
from time import time
from base64 import b64encode, b64decode
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from model_utils.models import TimeStampedModel
from config.models import AbstractBaseModel
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _
from dry_rest_permissions.generics import allow_staff_or_superuser


class User(AbstractUser, TimeStampedModel):
    first_name = None
    last_name = None

    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    metadata = JSONField(default=dict, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})

    def generate_reset_hash(self):
        if self.user_is_admin:
            raise Exception("cannot reset admin password via client")
        encoded = "%s|%s|%s" % (self.username, self.id, self.created)
        return hashlib.md5(encoded.encode()).hexdigest()

    def compare_reset_hash(self, reset_token):
        test = self.generate_reset_hash()
        token = b64decode(reset_token)
        token = token.decode('utf-8')
        parts = token.split('|')
        if parts[0] != test:
            return False

        t = time()
        diff = t - float(parts[1])

        if diff > 18000:
            return False
        return True

    def reset_password(self):
        h = self.generate_reset_hash()
        s = "%s|%s|%s" % (h, time(), self.id)
        token = b64encode((s.encode()))
        url = "%s/reset/%s" % (settings.APP_FRONTEND_URL, token.decode('utf-8'))
        msg = "<p>You requested to reset your password.</p>"
        msg += "<p><a href='%s'>Click here to reset</a></p>" % url
        msg += "<p>If you didn't request a new password, please respond to this email.</p>"
        send_mail("Reset Capitol Zen Password", msg, 'donald@capitolzen.com', [self.username])

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
