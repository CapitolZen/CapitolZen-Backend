from django.db.models.signals import post_save
from django.db import transaction

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
        transaction.on_commit(lambda: create_actions(bill))


def create_actions(bill):
    for user in User.objects.all():
        a = Action.objects.create(
            user=user,
            action_object=bill,
            title='bill:introduced',
            priority=0
        )

        a.save()
