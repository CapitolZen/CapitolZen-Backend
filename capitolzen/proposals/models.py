from __future__ import unicode_literals
from django.db import models
from config.models import AbstractBaseModel
from dry_rest_permissions.generics import allow_staff_or_superuser, authenticated_users
from django.contrib.postgres.fields import ArrayField, JSONField
from capitolzen.meta.states import AvailableStateChoices
from capitolzen.organizations.mixins import MixinResourcedOwnedByOrganization
from capitolzen.alerts.tasks import create_alert_task


class Bill(AbstractBaseModel):
    state = models.TextField(choices=AvailableStateChoices)
    status = models.TextField()
    committee = models.TextField()
    sponsor = models.TextField()
    title = models.TextField()
    state_id = models.CharField(max_length=225)
    categories = ArrayField(
        models.CharField(max_length=225, blank=True),
        default=list
    )
    history = JSONField(default=dict, blank=True, null=True)
    summary = models.TextField()

    class Meta:
        abstract = False
        verbose_name = "bill"
        verbose_name_plural = "bill"

    class JSONAPIMeta:
        resource_name = "bills"

    def update_from_source(self, data):
        self.status = data['status']
        self.committee = data['currentCommittee']
        self.serialize_history(data['history'])
        self.serialize_categories(data['categories'])
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
        create_alert_task.delay()
        super(Bill, self).save(*args, **kwargs)


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

    # Includes group reference && position
    groups = JSONField(blank=True, default=dict)
    notes = JSONField(blank=True, default=dict)

    def update_group(self, group_id, position=False, note=''):
        if not group_id:
            raise Exception

        if not self.valid_position(position):
            raise Exception

        groups = self.groups
        new_group = {
            'id': group_id,
            'position': position,
            'note': note
        }

        groups.append(new_group)
        self.groups = groups

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
