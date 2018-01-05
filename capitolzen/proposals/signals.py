from django.db.models.signals import post_save
from django.db import transaction
from django.db.models import Q

from django.dispatch import receiver

from capitolzen.proposals.models import Bill, Event
from capitolzen.users.models import User, Action


###################################
# Create introduction action
###################################


@receiver(post_save, sender=Bill)
def create_introduction_actions(sender, **kwargs):
    bill = kwargs.get('instance')
    created = kwargs.get('created')
    if created:
        transaction.on_commit(lambda: _create_introduction_actions(bill))


def _create_introduction_actions(bill):
    for user in User.objects.filter(is_active=True, notification_preferences__bill__introduced=True):
        a = Action.objects.create(
            user=user,
            action_object=bill,
            title='bill:introduced',
            priority=0
        )

        a.save()


@receiver(post_save, sender=Event)
def create_committee_actions(sender, **kwargs):
    event = kwargs.get('instance')
    created = kwargs.get('created')
    if created:
        transaction.on_commit()


def _create_committee_actions(event):
    users = User.objects.filter(
        Q(is_active=True),
        Q(notification_preferences__committee_meeting=['all']) |
        Q(notification_preferences__committee_meeting__contains=event.committee.id)
    )
