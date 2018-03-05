from __future__ import unicode_literals
import stripe

from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField, ArrayField

from dry_rest_permissions.generics import allow_staff_or_superuser


from config.models import AbstractBaseModel
from organizations.abstract import (
    AbstractOrganization,
    AbstractOrganizationUser,
    AbstractOrganizationOwner
)
from capitolzen.meta.billing import BASIC, PlanChoices
from capitolzen.organizations.notifications import email_member_invite


def avatar_directory_path(instance, filename):
    """
    Note the need to use the ID here. meaning we can't
    upload files during creation.
    :param instance:
    :param filename:
    :return:
    """
    return '{0}/misc/{1}'.format(instance.id, filename)


class OrganizationManager(models.Manager):
    def for_user(self, user):
        return self.get_queryset().filter(users=user)


class Organization(AbstractOrganization, AbstractBaseModel):
    """
    Default Organization model.
    """
    objects = OrganizationManager()

    ORG_DEMO = (
        ('association', 'Association'),
        ('union', 'Labor Union'),
        ('multi_client', 'Multi Client'),
        ('corporate', 'Corporation'),
        ('individual', 'Individual'),
    )

    PLAN_CHOICES = PlanChoices
    PLAN_DEFAULT = BASIC
    plan_name = models.CharField(max_length=256, blank=True, null=True)

    stripe_customer_id = models.CharField(max_length=256, blank=True)
    stripe_subscription_id = models.CharField(max_length=256, blank=True)
    stripe_payment_tokens = JSONField(blank=True, null=True)

    # Billing
    billing_name = models.CharField(max_length=256, blank=True, null=True)
    billing_email = models.EmailField(max_length=256, blank=True, null=True)
    billing_phone = models.CharField(max_length=256, blank=True, null=True)
    billing_address_one = models.CharField(max_length=254, null=True, blank=True)
    billing_address_two = models.CharField(max_length=254, blank=True, null=True)
    billing_city = models.CharField(max_length=254, null=True, blank=True)
    billing_state = models.CharField(max_length=100, null=True, blank=True)
    billing_zip_code = models.CharField(max_length=10, null=True, blank=True)

    demographic_org_type = models.CharField(
        blank=True, max_length=255, choices=ORG_DEMO, default='individual'
    )
    avatar = models.FileField(
        blank=True, null=True, max_length=255, upload_to=avatar_directory_path
    )
    contacts = JSONField(blank=True, default=dict)
    available_states = ArrayField(models.CharField(
        max_length=255, blank=True, null=True), default=['MI']
    )

    features = JSONField(default=list)
    client_label = models.CharField(max_length=255, default='Client')
    client_label_plural = models.CharField(max_length=255, default='Clients')

    def owner_user_account(self):
        """Because I can never remember how to get this"""
        if self.owner:
            return self.owner.organization_user.user
        else:
            return None

    def is_guest(self, user):
        return True if self.organization_users.filter(user=user, is_guest=True) else False


    class Meta(AbstractOrganization.Meta):
        abstract = False
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")

    class JSONAPIMeta:
        resource_name = "organizations"

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
        return self.is_member(request.user) or \
            request.user.is_staff or \
            request.user.is_superuser

    def has_object_write_permission(self, request):
        return self.is_admin(request.user) or \
            self.is_owner(request.user) or \
            request.user.is_staff or \
            request.user.is_superuser

    @staticmethod
    def has_billing_permission(request):
        if request.user.is_anonymous:
            return False

        if not request.organization:
            return False

        return True

    def has_object_billing_permission(self, request):
        if request.user.is_anonymous:
            return False

        if not request.organization:
            return False

        if request.organization.is_admin(request.user) or request.organization.is_owner(request.user):
            return True

        return False

    @staticmethod
    def has_update_subscription_permission(request):
        if request.user.is_anonymous:
            return False

        if not request.organization:
            return False

        return True

    def has_object_update_subscription_permission(self, request):
        if request.user.is_anonymous:
            return False

        if not request.organization:
            return False

        if request.organization.is_admin(request.user) or request.organization.is_owner(request.user):
            return True

        return False

    @staticmethod
    def has_update_source_permission(request):
        if request.user.is_anonymous:
            return False

        if not request.organization:
            return False

        return True

    def has_object_update_source_permission(self, request):
        if request.user.is_anonymous:
            return False

        if not request.organization:
            return False

        if request.organization.is_admin(request.user) or request.organization.is_owner(request.user):
            return True

        return False

    def has_object_create_permission(self, request):
        return request.user.is_authenticated


class OrganizationUser(AbstractOrganizationUser):
    """
    Default OrganizationUser model.
    """

    is_guest = models.BooleanField(default=False)

    class Meta(AbstractOrganizationUser.Meta):
        abstract = False
        verbose_name = _("organization user")
        verbose_name_plural = _("organization users")


class OrganizationOwner(AbstractOrganizationOwner):
    """
    Default OrganizationOwner model.
    """
    class Meta(AbstractOrganizationOwner.Meta):
        abstract = False
        verbose_name = _("organization owner")
        verbose_name_plural = _("organization owners")


class OrganizationInvite(AbstractBaseModel):
    STATUS_CHOICES = (
        ("claimed", 'Claimed'),
        ("unclaimed", 'Unclaimed'),
        ("revoked", 'Revoked'),

    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    email = models.EmailField(max_length=254)
    status = models.CharField(max_length=254, choices=STATUS_CHOICES)
    user = models.ForeignKey('users.User', blank=True, null=True)

    @property
    def organization_name(self):
        return self.organization.name

    class Meta:
        verbose_name = _("invite")
        verbose_name_plural = _("invites")

    def send_user_invite(self):
        url = "%s/claim/%s" % (settings.APP_FRONTEND, self.id)
        email_member_invite(
            self.email,
            action_url=url,
            name=self.user.name,
            organization_name=self.organization_name)

    class JSONAPIMeta:
        resource_name = "invites"

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
        return request.user.is_authenticated()

    def has_object_write_permission(self, request):
        return request.user.is_authenticated()

    def has_object_create_permission(self, request):
        return request.user.is_authenticated()


def file_directory_path(instance, filename):
    """
    format directory path for file library
    :param instance:
    :param filename:
    :return string:
    """
    return '{0}/files/{1}'.format(instance.id, filename)
