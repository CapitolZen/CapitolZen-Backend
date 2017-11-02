from celery import shared_task
import inflect
from string import capwords
from datetime import datetime, timedelta
from capitolzen.proposals.managers import (
    BillManager, LegislatorManager, CommitteeManager
)
from capitolzen.proposals.utils import iterate_states, normalize_data
from capitolzen.organizations.models import Organization
from capitolzen.proposals.models import Wrapper
from capitolzen.groups.models import Group
from capitolzen.organizations.notifications import email_update_bills

@shared_task
def bill_manager(state):
    return BillManager(state).run()


@shared_task
def legislator_manager(state):
    return LegislatorManager(state).run()


@shared_task
def committee_manager(state):
    return CommitteeManager(state).run()


@shared_task
def spawn_bill_updates():
    return iterate_states(BillManager, bill_manager)


@shared_task
def spawn_legislator_updates():
    return iterate_states(LegislatorManager, legislator_manager)


@shared_task
def spawn_committee_updates():
    return iterate_states(CommitteeManager, committee_manager)


@shared_task
def run_organization_updates():
    organizations = Organization.objects.filter(is_active=True)
    today = datetime.today()
    date_range = today - timedelta(days=1)
    for org in organizations:
        groups = Group.objects.filter(organization=org, active=True)

        for group in groups:
            wrappers = Wrapper.objects.filter(
                bill__action_dates__range=[str(date_range), str(today)],
                group=group
            )
            count = len(wrappers)
            p = inflect.engine()
            count = p.number_to_words(count)
            output = normalize_data(wrappers)
            if count:
                subject = '%s Bills Have Updates for %s' % (count, group.title)
                message = 'Bills for %s have new action or information.' % group.title
                message = capwords(message)
                email_update_bills(message=message, organization=org, subject=subject, bills=output)

