from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Group, Update
from django.conf import settings
from django.db import transaction
from capitolzen.organizations.tasks import intercom_update_organization_attributes
from capitolzen.groups.tasks import notify_page_viewers_of_update

@receiver(post_save, sender=Group)
def update_group_count(sender, **kwargs):
    if settings.INTERCOM_ENABLE_SYNC:
        group = kwargs.get('instance')

        transaction.on_commit(
            lambda: intercom_update_organization_attributes.apply_async(args=[
                str(group.organization.id)
            ]))


@receiver(post_save, sender=Update)
def send_update_notifications(sender, **kwargs):
    update = kwargs.get('instance')
    created = kwargs.get('created')

    if created:
        transaction.on_commit(
            lambda: notify_page_viewers_of_update.apply_async(args=[str(update.id)])
        )
