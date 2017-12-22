from django.db.models.signals import post_save, post_delete

from django.dispatch import receiver
from django.conf import settings
from django.db import transaction

from organizations.signals import user_added, user_removed
from capitolzen.users.models import User
from capitolzen.users.tasks import (
    intercom_manage_user,
    user_action_defaults
)
from logging import getLogger

logger = getLogger('app')

################################################################################
# INTERCOM
################################################################################
@receiver(post_save, sender=User)
def intercom_update_user(sender, **kwargs):
    """
    Sync user with intercom

    :param sender:
    :param kwargs:
    :return:
    """
    user = kwargs.get('instance')

    if settings.INTERCOM_ENABLE_SYNC:
        logger.debug("INTERCOM USER SYNC - %s - %s" % ( 'create_or_update', user.username))

        transaction.on_commit(
            lambda: intercom_manage_user.apply_async(kwargs={
                'user_id': str(user.id),
                'operation': 'create_or_update'
            }))


@receiver(post_delete, sender=User)
def intercom_delete_user(sender, **kwargs):
    """
    When a user is deleted, delete them from intercom
    :param sender:
    :param kwargs:
    :return:
    """
    if settings.INTERCOM_ENABLE_SYNC:
        user = kwargs.get('instance')

        logger.debug("INTERCOM USER SYNC - %s - %s" % ('delete', user.username))

        transaction.on_commit(lambda: intercom_manage_user.apply_async(kwargs={
            'user_id': str(user.id),
            'operation': 'delete'
        }))


@receiver(user_added)
@receiver(user_removed)
def user_manage_organizations(sender, **kwargs):
    """
    Note: This is only called when we use the add_user / etc
    methods directly (which we do via the api) however it doesn't
    get called when using things like the django admin.py area to
    add or remove users from an organization see:
    https://github.com/bennylope/django-organizations/issues/123
    :param sender:
    :param kwargs:
    :return:
    """
    if settings.INTERCOM_ENABLE_SYNC:
        user = kwargs.get('user')

        logger.debug("INTERCOM USER SYNC - %s - %s" % ('organizations', user.username))

        transaction.on_commit(
            lambda: intercom_manage_user.apply_async(kwargs={
                'user_id': str(user.id),
                'operation': 'create_or_update'
            }))

################################################################################
# MISC
################################################################################
@receiver(post_save, sender=User)
def set_user_action_defaults(sender, **kwargs):
    """
    Creates default user actions.

    :param sender:
    :param kwargs:
    :return:
    """
    user = kwargs.get('instance')
    user_action_defaults(str(user.id))
