from __future__ import unicode_literals
import base64
import requests

from django.db import models

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.postgres.fields import ArrayField, JSONField

from django.contrib.contenttypes.fields import GenericRelation

from config.models import AbstractBaseModel

from model_utils import Choices

from capitolzen.organizations.mixins import MixinResourcedOwnedByOrganization
from capitolzen.meta.notifications import admin_email
from capitolzen.proposals.mixins import MixinExternalData


class Bill(AbstractBaseModel, MixinExternalData):
    actions = GenericRelation('users.Action', related_query_name="legislator")

    # External Data
    state = models.TextField(max_length=255, null=True)
    state_id = models.CharField(max_length=255, null=True)
    remote_id = models.CharField(
        max_length=255, null=True, unique=True, db_index=True
    )
    session = models.CharField(max_length=255, null=True)
    history = JSONField(default=dict, blank=True, null=True)
    action_dates = JSONField(default=dict, blank=True, null=True)
    chamber = models.CharField(max_length=255, null=True)
    type = models.CharField(default=None, max_length=255, null=True)
    current_committee = models.ForeignKey('proposals.Committee', null=True)
    sponsor = models.ForeignKey('proposals.Legislator', null=True)
    sponsors = JSONField(default=dict, blank=True, null=True)
    cosponsors = JSONField(default=list, null=True)
    title = models.TextField(null=True)
    companions = ArrayField(
        blank=True, null=True, default=list,
        base_field=models.TextField(blank=True)
    )
    categories = ArrayField(
        models.TextField(blank=True),
        default=list
    )
    votes = JSONField(default=dict, blank=True, null=True)
    content_metadata = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    sources = JSONField(default=dict, blank=True, null=True)
    documents = JSONField(default=dict, blank=True, null=True)
    current_version = models.URLField(blank=True, null=True)
    bill_versions = JSONField(default=dict, blank=True, null=True)
    bill_text = models.TextField(null=True)

    updated_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(null=True)

    # ES Ingest Attachment Pipeline Enablers
    bill_text_analysis = JSONField(default=None, null=True)
    bill_raw_text = models.TextField(default=None, null=True)

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
    def introduced_date(self):
        return self.action_dates.get('first', False)

    @property
    def remote_url(self):
        source = next((l for l in self.sources if l.get('url') is not False),
                      None)
        if not source:
            return False
        return source.get('url', False)

    @property
    def remote_status(self):
        if not self.history or not len(self.history):
            return 'no history available'
        latest = self.history[-1]
        return latest['action']

    def update(self, source):
        for sponsor in source.get('sponsors', []):
            if sponsor.get('leg_id', False):
                q = {"remote_id": sponsor['leg_id']}
            else:
                parts = sponsor['name'].split(' ', 1)
                if len(parts) > 1:
                    q = {"first_name": parts[0], "last_name": parts[1]}
                else:
                    q = {"last_name": parts[0]}

            try:
                leg = Legislator.objects.get(**q)
                if sponsor['type'] == "primary":
                    self.sponsor = leg
                else:
                    # Need to prevent duplicate entries
                    if str(leg.id) not in self.cosponsors:
                        self.cosponsors.append(str(leg.id))

            except (ObjectDoesNotExist, MultipleObjectsReturned):
                msg = "id: %s does not match sponsor" % self.id
                admin_email.delay(msg)
                continue

        # So Open states lately isn't reporting primary sponsors...
        if not self.sponsor and len(self.cosponsors) and len(self.sponsors):
            only_id = self.sponsors.pop(0)
            try:
                self.sponsor = Legislator.objects.get(only_id['leg_id'])
            except Exception:
                msg = "id: %s does not match sponsor" % self.id
                admin_email.delay(msg)
        else:
            msg = "id: %s does not match sponsor" % self.id
            admin_email.delay(msg)
        
        self.type = source.get('type', ['bill'])[0]

        for cat in source.get('categories', []):
            self.categories.append(cat)

        if self.bill_versions:
            self.current_version = self.bill_versions[-1].get('url')
        if self.current_version:
            response = requests.get(self.current_version)
            if 200 >= response.status_code < 300:
                self.bill_raw_text = base64.b64encode(
                    response.content).decode('ascii')
        self.history = source.get('history', [])
        self.set_current_committee()
        self.save()

        return self

    def set_current_committee(self):
        committee = None
        chamber = None
        for action in self.history:
            committee = None
            chamber = None
            if action['type'][0] == 'committee:referred':
                action_parts = action['action'].lower().split('referred to committee on ')
                if len(action_parts) > 1:
                    committee = action_parts[1]
                    chamber = action['actor']
            if action['type'][0] == 'committee:passed':
                committee = None
                chamber = None

        if committee and chamber:
            self.current_committee = Committee.objects.filter(name__icontains=committee, chamber=chamber).first()

    class Meta:
        abstract = False
        verbose_name = "bill"
        verbose_name_plural = "bills"

    class JSONAPIMeta:
        resource_name = "bills"


class Legislator(AbstractBaseModel, MixinExternalData):
    actions = GenericRelation('users.Action', related_query_name="legislator")

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
    middle_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255)
    suffixes = models.CharField(max_length=255, blank=True, null=True)
    updated_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(null=True)

    # Properties
    @property
    def full_name(self):
        fl = "%s %s" % (self.first_name, self.last_name)
        if self.suffixes:
            fl = "%s %s" % (fl, self.suffixes)
        return fl

    class Meta:
        abstract = False
        verbose_name = "legislator"
        verbose_name_plural = "legislators"

    class JSONAPIMeta:
        resource_name = "legislators"


class Committee(AbstractBaseModel, MixinExternalData):
    actions = GenericRelation('users.Action', related_query_name="committee")

    name = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    chamber = models.CharField(max_length=255)
    remote_id = models.CharField(max_length=255, db_index=True)
    parent_id = models.CharField(max_length=255, null=True, blank=True)
    subcommittee = models.CharField(max_length=255, null=True, blank=True)
    updated_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(null=True)

    class Meta:
        abstract = False
        verbose_name = "Committee"
        verbose_name_plural = "Committees"

    class JSONAPIMeta:
        resource_name = "committees"


class Event(AbstractBaseModel, MixinExternalData):
    actions = GenericRelation('users.Action', related_query_name="event")

    state = models.CharField(max_length=255)
    chamber = models.CharField(max_length=255)
    time = models.DateTimeField()

    event_choices = Choices(
        ('committee:meeting', 'Committee - Meeting')
    )
    event_type = models.CharField(choices=event_choices, default='committee:meeting', max_length=255)
    url = models.URLField(blank=True, null=True)
    publish_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    # TODO: Need to figure out how to actually turn this into legit locations
    location_text = models.TextField()

    description = models.TextField(blank=True, null=True)
    attachments = JSONField(default=list)

    # Possible external references
    committee = models.ForeignKey('proposals.Committee', blank=True, null=True)
    legislator = models.ForeignKey('proposals.Legislator', blank=True, null=True)
    remote_id = models.TextField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = False
        verbose_name_plural = "Events"
        verbose_name = "event"

    class JSONAPIMeta:
        resource_name = "events"


class Wrapper(AbstractBaseModel, MixinResourcedOwnedByOrganization):
    actions = GenericRelation('users.Action', related_query_name="wrapper")
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
    notes = JSONField(blank=True, default=list)
    starred = models.BooleanField(default=False)
    summary = models.TextField(blank=True, null=True)
    files = JSONField(blank=True, default=list)

    @property
    def display_summary(self):
        if not self.summary:
            return self.bill.title
        return self.summary

    @property
    def display_sponsor(self):
        if self.bill.sponsor:
            return self.bill.sponsor.full_name
        else:
            return None

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
