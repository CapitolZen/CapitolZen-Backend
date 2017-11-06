import inflect
from string import capwords
from datetime import datetime, timedelta
from celery import shared_task

from capitolzen.proposals.managers import (
    BillManager, LegislatorManager, CommitteeManager
)
from capitolzen.proposals.utils import iterate_states, normalize_data
from capitolzen.organizations.models import Organization
from capitolzen.proposals.models import Wrapper
from capitolzen.groups.models import Group
from capitolzen.organizations.notifications import email_update_bills
from capitolzen.proposals.utils import (
    iterate_states, summarize, normalize_data
)
from capitolzen.proposals.documents import BillDocument


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
def run_organization_bill_updates():
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


@shared_task(retry_kwargs={'max_retries': 20})
def ingest_attachment(identifier):
    instance = Bill.objects.get(id=identifier)
    document = BillDocument.get(id=str(instance.id))
    if not document:
        raise ingest_attachment.retry(countdown=30)

    # Have to run save for some reason because python ES DSL doesn't invoke
    # the pipeline by default.
    document.save(pipeline="attachment")

    # Have to requery to get the new document with the attachment info included
    # .save() just returns a boolean so can't get the info from the response
    document = BillDocument.get(id=str(instance.id))
    instance.bill_text_analysis = document.bill_text_analysis.to_dict()
    instance.content = instance.bill_text_analysis.get('content', "").replace(
        '\n', ' ').replace(
        '\r', '').replace(
        '\xa0', ' ').strip()
    instance.summary = summarize(instance.content)
    instance.save()
    return True
