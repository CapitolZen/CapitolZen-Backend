from django.db.models.signals import post_save

from django.dispatch import receiver

from capitolzen.proposals.models import Bill
from capitolzen.users.models import User, Action


###################################
# Create introduction action
###################################


@receiver(post_save, sender=Bill)
def create_introduction_actions(sender, **kwargs):
    bill = kwargs.get('instance')
    created = kwargs.get('created')
    if created:
        for user in User.objects.all():
            a, created = Action.objects.get_or_create(
                user=user,
                action_object=bill,
                title='bill:introduced',
                priority=0
            )
            if created:
                a.save()
