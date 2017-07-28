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
    state_id = models.CharField(max_length=255, null=True)
    remote_id = models.CharField(max_length=255, null=True)
    session = models.CharField(max_length=255, null=True)
    history = JSONField(default=dict, blank=True, null=True)
    action_dates = JSONField(default=dict, blank=True, null=True)
    chamber = models.CharField(max_length=255, null=True)
    type = models.CharField(max_length=255, null=True)
    status = models.TextField(null=True)
    current_committee = models.ForeignKey('proposals.Committee')
    sponsor = models.ForeignKey('proposals.Legislator')
    cosponsors = JSONField(default=dict, blank=True)
    title = models.TextField()
    companions = ArrayField(blank=True, default=list, base_field=models.TextField(blank=True))
    categories = ArrayField(
        models.TextField(blank=True),
        default=list
    )
    versions = JSONField(default=dict, blank=True),
    votes = JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True, null=True)
    sources = JSONField(default=dict, blank=True)
    documents = JSONField(default=dict, blank=True)

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

    def update_from_source(self, source):
        props = {
            "actions": "history",
            "sources": "sources",
            "session": "session",
            "id": "remote_id",
            "votes": "votes",
            "versions": "versions",
            "documents": "documents",
            "title": "title",
            "state": "state",
            "action_dates": "action_dates",
            "bill_id": "state_id",
        }

        for key, value in props.items():
            setattr(self, value, source.get(key, None))

        # TODO SPonsors

        self.type = next(source.get('type', ['bill']))
        for cat in source.categories:
            self.categories.append(cat)

        self.save()

    class Meta:
        abstract = False
        verbose_name = "bill"
        verbose_name_plural = "bills"

    class JSONAPIMeta:
        resource_name = "bills"


class Legislator(AbstractBaseModel, MixinExternalData):
    # External Data
    remote_id = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    chamber = models.CharField(max_length=255)
    party = models.CharField(max_length=255)
    district = models.CharField(max_length=255, null=True)
    email = models.EmailField(blank=True)
    url = models.URLField(blank=True)
    photo_url = models.URLField(blank=True)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    suffixes = models.CharField(max_length=255, blank=True, null=True)

    # Properties
    @property
    def full_name(self):
        fl = "%s %s" % (self.first_name, self.last_name)
        if self.suffixes:
            fl = "%s %s" % (fl, self.suffixes)
        return fl

    def update_from_source(self, source):
        props = {
            "state": "state",
            "last_name": "last_name",
            "first_name": "first_name",
            "middle_name": "middle_name",
            "suffixes": "suffixes",
            "district": "district",
            "active": "active",
            "chamber": "chamber",
            "party": "party",
            "email": "email",
            "url": "url",
            "photo_url": "photo_url",
        }

        for key, value in props.items():
            setattr(self, value, source.get(key, None))

        self.save()

    class Meta:
        abstract = False
        verbose_name = "legislator"
        verbose_name_plural = "legislators"

    class JSONAPIMeta:
        resource_name = "legislators"


class Committee(AbstractBaseModel, MixinExternalData):

    name = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    chamber = models.CharField(max_length=255)
    remote_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)

    class Meta:
        abstract = False
        verbose_name = "Committee"
        verbose_name_plural = "Committees"

    class JSONAPIMeta:
        resource_name = "committees"


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
