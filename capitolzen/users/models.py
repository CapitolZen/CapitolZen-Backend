from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from model_utils import Choices


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


def default_notifications():
    return {
        'bill_introduced': True,
        'wrapper_updated': True,
        'committee_meeting': [],
        'user_mention': True
    }


class User(AbstractUser, AbstractNoIDModel):
    first_name = None
    last_name = None

    name = models.CharField(_('Name of User'), blank=True, max_length=255)
    metadata = JSONField(default=dict, null=True, blank=True)
    avatar = models.FileField(
        blank=True, null=True, max_length=255,
        upload_to=avatar_directory_path
    )

    features = JSONField(default=list)
    notification_preferences = JSONField(default=default_notifications)

    def __str__(self):
        return self.name or self.username

    class JSONAPIMeta:
        resource_name = "users"

    def has_notification(self, action_type, **kwargs):
        prefs = getattr(self, 'notification_preferences', False)

        if not prefs:
            return False

        # Check for committee id because of all the lists
        if action_type == 'committee:meeting':
            if not kwargs.get('committee_id', False):
                return False
            committees = prefs.get('committee:meeting', [])

            # This is getting kind of shitty...
            if committees[0] == 'all':
                return True

            if not len(committees):
                return False

            return kwargs['committee_id'] in committees

        # Finally check the easy shit
        return prefs.get(action_type, False)

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


class Action(AbstractBaseModel):

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE
    )
    priority = models.IntegerField(
        default=0,
        validators=[MaxValueValidator(10), MinValueValidator(-10)]
    )

    object_id = models.UUIDField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    action_object = GenericForeignKey('content_type', 'object_id')

    state_choices = Choices(
        ('active', 'Active'),
        ('dismissed', 'Dismissed'),
        ('snoozed', 'Snoozed'),
        ('flagged', 'Flagged')
    )

    state = models.CharField(
        choices=state_choices, max_length=225, db_index=True, default='active'
    )

    type_choices = Choices(
        ('bill:introduced', 'Bill Introduced'),
        ('wrapper:updated', 'Bill Updated'),
        ('wrapper:committee_scheduled', 'Saved Bill in Committee'),
        ('organization:user-add', 'User Joined'),
        ('organization:user-invite', 'User Invited'),
        ('user:mention', 'Mentioned'),
        ('committee:meeting', 'Committee Meeting')
    )

    title = models.CharField(
        choices=type_choices,
        max_length=225,
        db_index=True
    )

    class Meta:
        abstract = False
        verbose_name = "action"
        verbose_name_plural = "actions"

    class JSONAPIMeta:
        resource_name = "actions"

    @staticmethod
    @allow_staff_or_superuser
    def has_write_permission(request):
        return False

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        return request.user == self.user

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(request):
        return False

    @allow_staff_or_superuser
    def has_object_create_permission(self, request):
        return False

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return request.user == self.user
