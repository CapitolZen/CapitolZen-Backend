from __future__ import unicode_literals
from datetime import datetime
from django.db import models
from config.models import AbstractBaseModel
from dry_rest_permissions.generics import allow_staff_or_superuser, authenticated_users
from django.contrib.postgres.fields import ArrayField, JSONField
from capitolzen.meta.states import AvailableStateChoices
from capitolzen.organizations.mixins import MixinResourcedOwnedByOrganization
from .mixins import MixinExternalData


class Bill(AbstractBaseModel, MixinExternalData):
    # External Data
    state = models.TextField(choices=AvailableStateChoices)
    state_id = models.CharField(max_length=255)
    remote_id = models.CharField(max_length=255)
    session = models.CharField(max_length=255)
    history = JSONField(default=dict, blank=True, null=True)
    action_dates = JSONField(default=dict, blank=True, null=True)
    chamber = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    status = models.TextField()
    current_committee = models.TextField()
    sponsor = models.TextField()
    title = models.TextField()
    companions = ArrayField(blank=True, default=list, base_field=models.TextField(blank=True))
    categories = ArrayField(
        models.CharField(max_length=255, blank=True),
        default=list
    )
    versions = JSONField(default=dict, blank=True),
    votes = JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True, null=True)

    # Properties
    @property
    def affected_section(self):
        if self.type != "bill":
            return False
        return True

    @property
    def last_action_date(self):
        return self.action_dates.get('last', False)

    @property
    def remote_url(self):
        return self.sources.get('url', False)

    class Meta:
        abstract = False
        verbose_name = "bill"
        verbose_name_plural = "bill"

    class JSONAPIMeta:
        resource_name = "bills"


class Wrapper(AbstractBaseModel, MixinResourcedOwnedByOrganization):

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    bill = models.ForeignKey(
        'proposals.Bill',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    group = models.ForeignKey(
        'groups.Group',
        blank=False,
        on_delete=models.CASCADE,
        null=True
    )

    position = models.CharField(blank=True, max_length=255)
    position_detail = models.TextField(blank=True, null=True)
    notes = JSONField(blank=True, default=dict)
    starred = models.BooleanField(default=False)
    summary = models.TextField(blank=True, null=True)

    @property
    def display_summary(self):
        if not self.summary:
            return self.bill.summary
        return self.summary

    @staticmethod
    def valid_position(position):
        valid = ['support', 'oppose', 'neutral', False]
        if position in valid:
            return True
        else:
            return False

    class Meta:
        abstract = False
        verbose_name = "wrapper"
        verbose_name_plural = "wrapper"

    class JSONAPIMeta:
        resource_name = "wrappers"
