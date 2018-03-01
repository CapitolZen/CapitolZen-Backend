from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Group, Report
from django.conf import settings
from django.db import transaction
from capitolzen.organizations.tasks import intercom_update_organization_attributes

@receiver(post_save, sender=Group)
def update_group_count(sender, **kwargs):
    if settings.INTERCOM_ENABLE_SYNC:
        group = kwargs.get('instance')

        transaction.on_commit(
            lambda: intercom_update_organization_attributes.apply_async(args=[
                str(group.organization.id)
            ]))


@receiver(post_save, sender=Report)
def update_report_count(sender, **kwargs):
    if settings.INTERCOM_ENABLE_SYNC:
        report = kwargs.get('instance')
        transaction.on_commit(
            lambda: intercom_update_organization_attributes.apply_async(args=[
                str(report.organization.id)
            ])
        )
