from __future__ import unicode_literals
from django.db import models
from config.models import AbstractBaseModel
from dry_rest_permissions.generics import allow_staff_or_superuser
from django.contrib.postgres.fields import ArrayField, JSONField
from downdraft.meta.states import AvailableStateChoices


class Bill(AbstractBaseModel):
    state = models.TextField(choices=AvailableStateChoices)
    status = models.TextField()
    committee = models.TextField()
    sponsor = models.TextField()
    title = models.TextField()
    state_id = models.CharField(max_length=225)
    categories = ArrayField(
        models.CharField(max_length=225, blank=True)
    )

    class Meta:
        abstract = False
        verbose_name = "bill"
        verbose_name_plural = "bill"

    class JSONAPIMeta:
        resource_name = "bills"


class Wrapper(AbstractBaseModel):

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE
    )

    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
    )

    # Includes group reference && position
    groups = JSONField(blank=True)

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

    notes = JSONField(blank=True)

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
