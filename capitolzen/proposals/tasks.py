import inflect
from string import capwords
from datetime import datetime, timedelta
from celery import shared_task

from capitolzen.meta.states import AVAILABLE_STATES

from capitolzen.proposals.managers import (
    BillManager, LegislatorManager, CommitteeManager, EventManager
)
from capitolzen.organizations.models import Organization
from capitolzen.users.models import User, Action

from capitolzen.proposals.models import Wrapper, Bill, Event
from capitolzen.groups.models import Group
from capitolzen.organizations.notifications import email_update_bills
from capitolzen.proposals.utils import (
    iterate_states, summarize, normalize_bill_data
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
def spawn_committee_meeting_updates():
    for state in AVAILABLE_STATES:
        EventManager(state).run()


@shared_task
def run_organization_bill_updates():
    organizations = Organization.objects.filter(is_active=True)
    today = datetime.today()
    yesterday = today - timedelta(days=1)
    for org in organizations:
        groups = Group.objects.filter(organization=org, active=True)

        for group in groups:
            wrappers = Wrapper.objects.filter(
                bill__modified_at__range=[yesterday, today],
                group=group
            )
            count = len(wrappers)
            if count:
                p = inflect.engine()
                count = p.number_to_words(count)
                output = normalize_bill_data(wrappers)
                subject = '%s Bills Have Updates for %s' % (count.title(), group.title)
                message = 'Bills for %s have new action or information.' % (
                    group.title)
                message = capwords(message)
                email_update_bills(
                    message=message,
                    organization=org,
                    subject=subject,
                    bills=output
                )


@shared_task
def create_bill_introduction_actions():
    today = datetime.today()
    yesterday = today - timedelta(days=1)
    bills = Bill.objects.filter(created_at__range=[yesterday, today])
    count = len(bills)
    if count:
        p = inflect.engine()
        count = p.number_to_words(count)
        bill_list = []

        for bill in bills:
            data = {
                "state_id": bill.state_id,
                "state": bill.state,
                "id": str(bill.id),
                "sponsor": bill.sponsor.full_name,
                "summary": bill.title,
                "status": bill.remote_status,
            }
            bill_list.append(data)

        for user in User.objects.all():
            for bill in bills:
                action, created = Action.objects.get_or_create(
                    user=user,
                    title='bill:introduced',
                    action_object=bill,
                    priority=0
                )

                if not created:
                    continue

                action.save()
            subject = '%s New Bills Have Been Introduced' % (count.title(),)
            message = 'There were %s new bills introduced yesterday. ' \
                      'Login into your Capitol Zen account to view them all.'
            email_update_bills(
                message=message,
                subject=subject,
                bills=bill_list,
                to=user
            )


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
