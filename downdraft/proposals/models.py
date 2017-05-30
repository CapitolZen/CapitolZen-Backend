from __future__ import unicode_literals
from django.db import models
from config.models import AbstractBaseModel
from dry_rest_permissions.generics import allow_staff_or_superuser
from django.contrib.postgres.fields import ArrayField, JSONField


class Bill(AbstractBaseModel):
    state = models.TextField()
    status = models.TextField()
    committee = models.TextField()
    sponsor = models.TextField()
    title = models.TextField()
    categories = ArrayField()

    class Meta(self):
        abstract = False
        verbose_name = _("bill")
        verbose_name_plural = _("bill")

    class JSONAPIMeta:
        resource_name = "bills"


class Wrapper(AbstractBaseModel):

    organization = models.ForeignKey(
        'organizations',
        on_delete=models.CASCADE
    )

    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
    )

    group = models.ForeignKey(
        'group',
        on_delete=models.CASCADE,
        limit_choices_to='list_org_groups'
    )

    notes = JSONField(blank=True)
    comments = JSONField(blank=True)

    def list_org_groups(self):
        org = self.organization

    class Meta(self):
        abstract = False
        verbose_name = _("wrapper")
        verbose_name_plural = _("wrapper")

    class JSONAPIMeta:
        resource_name = "wrappers"
