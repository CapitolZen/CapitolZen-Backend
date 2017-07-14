from __future__ import unicode_literals
from datetime import datetime
from django.db import models
from config.models import AbstractBaseModel
from dry_rest_permissions.generics import allow_staff_or_superuser, authenticated_users
from django.contrib.postgres.fields import ArrayField, JSONField
from capitolzen.meta.states import AvailableStateChoices
from capitolzen.organizations.mixins import MixinResourcedOwnedByOrganization
from capitolzen.users.tasks import create_alert_task


class Bill(AbstractBaseModel):
    state = models.TextField(choices=AvailableStateChoices)
    status = models.TextField()
    current_committee = models.TextField()
    sponsor = models.TextField()
    title = models.TextField()
    state_id = models.CharField(max_length=225)
    categories = ArrayField(
        models.CharField(max_length=225, blank=True),
        default=list
    )
    history = JSONField(default=dict, blank=True, null=True)
    versions = JSONField(default=dict, blank=True)
    summary = models.TextField()
    last_action_date = models.DateTimeField(default=datetime.now())
    affected_section = models.TextField(blank=True, null=True)
    remote_url = models.URLField(null=True, blank=True)

    class Meta:
        abstract = False
        verbose_name = "bill"
        verbose_name_plural = "bill"

    class JSONAPIMeta:
        resource_name = "bills"

    def update_from_source(self, data):
        self.status = data['status']
        self.current_committee = data['current_committee']
        self.serialize_history(data['history'])
        self.last_action_date = data['last_action_date']
        # self.serialize_categories(data['categories'])
        self.save()

    def serialize_categories(self, data):
        self.categories = data

    def serialize_history(self, data):
        self.history = data

    @staticmethod
    @authenticated_users
    def has_read_permission(request):
        return True

    @authenticated_users
    def has_object_read_permission(self, request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_write_permission(request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(request):
        return True

    def save(self, *args, **kwargs):
        super(Bill, self).save(*args, **kwargs)
        create_alert_task.delay(self.title, self.categories)


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

    position = models.CharField(blank=True, max_length=255, )
    notes = JSONField(blank=True, default=dict)
    starred = models.BooleanField(default=False)

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
