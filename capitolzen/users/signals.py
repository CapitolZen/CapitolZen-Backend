from django.db.models.signals import post_save, post_delete
from organizations.signals import user_added, user_removed
from django.dispatch import receiver
from .models import User
from .tasks import (intercom_manage_user_companies,
                    intercom_manage_user
                    )


@receiver(post_save, sender=User)
def intercom_update_user(sender, **kwargs):
    """
    https://www.whatan00b.com/posts/celery-jobs-unable-to-access-objects-when-queued-by-post_save-signal-in-django/
    http://docs.celeryproject.org/en/latest/whatsnew-4.0.html#django-support
    https://docs.djangoproject.com/en/1.11/topics/db/transactions/#performing-actions-after-commit

    We delay the task execution 10 seconds because post_save
    isn't post database commit. Need to how to take
    advantage of transaction.on_commit while still using the
    receiver decorator. This isn't great, because technically it
    could take longer than 10 seconds to do a db transaction.

    :param sender:
    :param kwargs:
    :return:
    """

    created = kwargs.get('created')
    user = kwargs.get('instance')

    if created:
        intercom_manage_user.apply_async([str(user.id), "create"], countdown=10)
    else:
        intercom_manage_user.apply_async([str(user.id), "update"], countdown=10)


@receiver(post_delete, sender=User)
def intercom_delete_user(sender, **kwargs):
    """
    When a user is deleted, delete them from intercom
    :param sender:
    :param kwargs:
    :return:
    """
    user = kwargs.get('instance')
    intercom_manage_user.apply_async([str(user.id), "delete"], countdown=10)


@receiver(user_added)
def user_added_to_organization(sender, **kwargs):
    """
    Note: This is only called when we use the add_user / etc
    methods directly (which we do via the api) however it doesn't
    get called when using things like the django admin area to
    add or remove users from an organization see:
    https://github.com/bennylope/django-organizations/issues/123
    :param sender:
    :param kwargs:
    :return:
    """

    user = kwargs.get('user')
    intercom_manage_user_companies.apply_async([user.id], countdown=10)


@receiver(user_removed)
def user_removed_from_organization(sender, **kwargs):
    """
    Note: This is only called when we use the add_user / etc
    methods directly (which we do via the api) however it doesn't
    get called when using things like the django admin area to
    add or remove users from an organization see:
    https://github.com/bennylope/django-organizations/issues/123
    :param sender:
    :param kwargs:
    :return:
    """
    user = kwargs.get('user')
    intercom_manage_user_companies.apply_async([user.id], countdown=10)
