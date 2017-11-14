from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Group, Report


@receiver(post_save, sender=Group)
def create_group_default_report(sender, **kwargs):
    group = kwargs.get('instance')
    organization = group.organization

    if getattr(organization, 'owner', False):
        user = organization.owner_user_account()
        preferences = {
            'layout': 'detail_list'
        }
        report = Report.objects.create(
            user=user,
            group=group,
            organization=organization,
            title="All Saved Bills",
            preferences=preferences
        )

        report.save()
