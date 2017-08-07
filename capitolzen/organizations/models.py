from __future__ import unicode_literals

from crum import get_current_user

from django.db import models
from django.utils.translation import ugettext_lazy as _
from config.models import AbstractBaseModel
from dry_rest_permissions.generics import allow_staff_or_superuser
from django.contrib.postgres.fields import ArrayField, JSONField

from organizations.abstract import (AbstractOrganization,
                                    AbstractOrganizationUser,
                                    AbstractOrganizationOwner)
from capitolzen.meta.billing import BASIC, PlanChoices
import stripe


class Organization(AbstractOrganization, AbstractBaseModel):
    """
    Default Organization model.
    """
    PLAN_CHOICES = PlanChoices
    PLAN_DEFAULT = BASIC
    plan_name = models.CharField(max_length=256, blank=True, null=True)

    stripe_customer_id = models.CharField(max_length=256, blank=True)
    stripe_subscription_id = models.CharField(max_length=256, blank=True)
    stripe_payment_tokens = JSONField(blank=True, null=True)

    billing_name = models.CharField(max_length=256, blank=True, null=True)
    billing_email = models.EmailField(max_length=256, blank=True, null=True)
    billing_phone = models.CharField(max_length=256, blank=True, null=True)
    billing_address_one = models.CharField(max_length=254, null=True, blank=True)
    billing_address_two = models.CharField(max_length=254, blank=True, null=True)
    billing_city = models.CharField(max_length=254, null=True, blank=True)
    billing_state = models.CharField(max_length=100, null=True, blank=True)
    billing_zip_code = models.CharField(max_length=10, null=True, blank=True)

    ORG_DEMO = (
        ('association', 'Association'),
        ('union', 'Labor Union'),
        ('multi_client', 'Multi Client'),
        ('corporate', 'Corporation'),
        ('individual', 'Individual'),
    )

    demographic_org_type = models.CharField(blank=True, max_length=255, choices=ORG_DEMO, default='individual')
    logo = models.URLField(blank=True)
    contacts = JSONField(blank=True, default=dict)

    @property
    def user_is_owner(self):
        return self.is_owner(get_current_user())

    @property
    def user_is_admin(self):
        return self.is_admin(get_current_user())

    @property
    def user_is_member(self):
        return self.is_member(get_current_user())

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

    def has_object_create_permission(self, request):
        return request.user.is_authenticated

    def create_subscription(self, plan=BASIC):
        stripe.api_key = 'asdf'
        sub = stripe.subscription.create(
            customer=self.stripe_customer_id,
            plan=plan,
        )

        self.stripe_subscription_id = sub.id
        self.save()

    def update_subscription(self, plan, **kwargs):
        sub = self.stripe_subscription_id
        return True


class OrganizationUser(AbstractOrganizationUser):
    """
    Default OrganizationUser model.
    """
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

    @property
    def organization_name(self):
        return self.organization.name

    class Meta:
        verbose_name = _("invite")
        verbose_name_plural = _("invites")

    # TODO: Actually send emails and such
    def send_user_invite(self):
        return True

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
