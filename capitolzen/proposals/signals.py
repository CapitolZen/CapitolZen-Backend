from datetime import datetime, timedelta

from django.db.models.signals import post_save
from django.db import transaction
from django.db.models import Q

from django.dispatch import receiver

from capitolzen.proposals.models import Bill, Event, Wrapper
from capitolzen.users.models import User, Action
from capitolzen.groups.models import Group



###################################
# Create introduction action
###################################


def _create_introduction_actions(bill):
    for user in User.objects.filter(is_active=True, notification_preferences__bill_introduced=True):
        a = Action.objects.create(
            user=user,
            bill=bill,
            title='bill:introduced',
            priority=0
        )

        a.save()

def _create_bill_update_action(bill):
    yesterday = datetime.today() - timedelta(days=1)
    if bill.updated_after(yesterday):
        for user in User.objects.filter(is_active=True, notification_preferences__wrapper_updated=True):
            groups = Group.objects.filter(assigned_to=user)
            for group in groups:
                try:
                    wrapper = Wrapper.objects.get(group=group, bill=bill)
                    a = Action.objects.create(
                        user=user,
                        wrapper=wrapper,
                        title='wrapper:updated',
                        priority=2
                    )
                    a.save()
                except Exception:
                    continue

@receiver(post_save, sender=Bill)
def create_introduction_actions(sender, **kwargs):
    bill = kwargs.get('instance')
    created = kwargs.get('created')
    if created:
        transaction.on_commit(lambda: _create_introduction_actions(bill))
    else:
        transaction.on_commit(lambda : _create_bill_update_action(bill))



def _create_committee_actions(event):
    users = User.objects.filter(
        Q(is_active=True),
        Q(notification_preferences__committee_meeting=['all']) |
        Q(notification_preferences__committee_meeting__contains=event.committee.id)
    )

    for user in users:
        a = Action.objects.create(
            user=user,
            event=event,
            title='committee:meeting',
            priority=1
        )

        a.save()


@receiver(post_save, sender=Event)
def create_committee_actions(sender, **kwargs):
    event = kwargs.get('instance')
    created = kwargs.get('created')
    if created:
        transaction.on_commit(lambda: _create_committee_actions(event))

