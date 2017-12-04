from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Organization
from .tasks import intercom_manage_organization, stripe_manage_customer
from organizations.signals import user_added, user_removed
from cacheops import invalidate_obj
from capitolzen.groups.models import Group
from django.db import transaction
from django.conf import settings


################################################################################################
# INTERCOM
################################################################################################
@receiver(post_save, sender=Organization)
def intercom_update_organization(sender, **kwargs):
    """
    :param sender:
    :param kwargs:
    :return:
    """
    if settings.INTERCOM_ENABLE_SYNC:
        created = kwargs.get('created')
        organization = kwargs.get('instance')
        operation = 'create' if created else 'update'

        transaction.on_commit(
            lambda: intercom_manage_organization.apply_async(kwargs={
                "organization_id": str(organization.id),
                "operation": operation
            }))


@receiver(post_delete, sender=Organization)
def intercom_delete_organization(sender, **kwargs):
    if settings.INTERCOM_ENABLE_SYNC:
        organization = kwargs.get('instance')
        transaction.on_commit(
            lambda: intercom_manage_organization.apply_async(kwargs={
                "organization_id": str(organization.id),
                "operation": 'delete'
            }))


################################################################################################
# STRIPE
################################################################################################
@receiver(post_save, sender=Organization)
def stripe_update_organization(sender, **kwargs):
    """
    :param sender:
    :param kwargs:
    :return:
    """
    organization = kwargs.get('instance')

    if not organization.stripe_customer_id:
        transaction.on_commit(
            lambda: stripe_manage_customer.apply_async(kwargs={
                "organization_id": str(organization.id),
                "operation": 'create'
            }))

    else:
        transaction.on_commit(
            lambda: stripe_manage_customer.apply_async(kwargs={
                "organization_id": str(organization.id),
                "operation": 'update'
            }))


@receiver(post_delete, sender=Organization)
def stripe_delete_organization(sender, **kwargs):
    organization = kwargs.get('instance')
    transaction.on_commit(
        lambda: stripe_manage_customer.apply_async(kwargs={
            "organization_id": str(organization.id),
            "operation": 'delete'
        }))


################################################################################################
# MISC
################################################################################################
@receiver(user_removed)
@receiver(user_added)
def invalidate_organization_cache(sender, **kwargs):
    """
    Invalidate org cache when users are added and removed.
    Done w/ special methods so the m2m isn't detected. (I think)
    either way this fixes some bugs.
    :param sender:
    :param kwargs:
    :return:
    """
    invalidate_obj(sender)


@receiver(post_save, sender=Organization)
def create_group_for_new_organization(sender, **kwargs):
    """
    Automatically create a group for the new organization.

    :param sender:
    :param kwargs:
    :return:
    """

    created = kwargs.get('created')
    organization = kwargs.get('instance')

    if created:
        Group.objects.create(
            title=organization.name,
            organization=organization,
            description="Your organization",
        )
