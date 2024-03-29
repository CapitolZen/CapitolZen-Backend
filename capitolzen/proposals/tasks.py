import inflect
from string import capwords
from datetime import datetime
from celery import shared_task

from bs4 import BeautifulSoup
from requests import get

from django.conf import settings

from capitolzen.meta.states import AVAILABLE_STATES
from capitolzen.meta.notifications import create_asana_task

from capitolzen.proposals.managers import (
    BillManager, LegislatorManager, CommitteeManager, EventManager
)
from capitolzen.organizations.models import Organization
from capitolzen.users.models import User, Action

from capitolzen.proposals.models import Wrapper, Bill, Legislator
from capitolzen.groups.models import Group
from capitolzen.organizations.notifications import email_update_bills
from capitolzen.proposals.utils import (
    iterate_states, normalize_bill_data, #summarize
)
#from capitolzen.proposals.documents import BillDocument


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

    for org in organizations:
        groups = Group.objects.filter(organization=org, active=True)

        for group in groups:
            wrappers = Wrapper.objects.filter(
                bill__updated_at__gt=today,
                group=group
            )
            count = wrappers.count()
            if count:
                p = inflect.engine()
                count = p.number_to_words(count)
                output = normalize_bill_data(wrappers)
                subject = '%s Bills Have Updates for %s' % (
                    count.title(), group.title
                )
                message = 'Bills for %s have new action or information.' % (
                    group.title)
                message = capwords(message)
                emails = []
                for user in group.organization.users.all():
                    emails.append(user.username)
                    email_update_bills(
                        message=message,
                        subject=subject,
                        bills=output
                    )
                    for wrapper in wrappers:
                        a = Action.objects.create(
                            user=user,
                            wrapper=wrapper,
                            priority=4,
                            title='wrapper:updated'
                        )
                        a.save()


@shared_task
def create_bill_introduction_table():
    today = datetime.today()

    bills = Bill.objects.filter(created_at__gt=today)
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
                "sponsor":  bill.sponsor.full_name if bill.sponsor else None,
                # In order to not munge more email templates,
                # pass different data
                "status": bill.title,
                "link": "%s/bills/%s" % (settings.APP_FRONTEND, str(bill.id))
            }
            bill_list.append(data)

        for user in User.objects.all():

            subject = '%s New Bills Have Been Introduced' % (count.title(),)
            message = 'There were %s new bills introduced yesterday. ' \
                      '<a href="%s">Login into</a> your Capitol Zen account ' \
                      'to view them all.' % (
                        count.title(), settings.APP_FRONTEND
                      )
            email_update_bills(
                message=message,
                subject=subject,
                bills=bill_list,
                to=user.username
            )


@shared_task(retry_kwargs={'max_retries': 20})
def ingest_attachment(identifier):
    # from capitolzen.proposals.graphs import BillGraph
    #
    # instance = Bill.objects.get(id=identifier)
    # document = BillDocument.get(id=str(instance.id))
    # if not document:
    #     return True
    #     # This caused some messaging namespace errors for some reasons..
    #     # TODO: Another place to fix thi
    #     #raise ingest_attachment.retry(countdown=30)
    #
    # # Have to run save for some reason because python ES DSL doesn't invoke
    # # the pipeline by default.
    # document.save(pipeline="attachment")
    #
    # # Have to requery to get the new document with the attachment info included
    # # .save() just returns a boolean so can't get the info from the response
    # document = BillDocument.get(id=str(instance.id))
    # instance.bill_text_analysis = document.bill_text_analysis.to_dict()
    # instance.content = instance.bill_text_analysis.get('content', "").replace(
    #     '\n', ' ').replace(
    #     '\r', '').replace(
    #     '\xa0', ' ').strip()
    # instance.summary = summarize(instance.content)
    # instance.save()
    # try:
    #     BillGraph(instance.id).run()
    # except OSError:
    #     pass
    return True


@shared_task
def clean_missing_sponsors():
    for bill in Bill.objects.filter(sponsor=None):
        if bill.history:
            intro = list(bill.history)[0]
            if intro['type'] == ['bill:introduced']:
                if intro['action'].lower() == 'entire membership':
                    continue
                pieces = intro['action'].split(' ')
                fname = pieces[-2].lower().strip()
                lname = pieces[-1].lower().strip()

                legislator = Legislator.objects.get_by_name_pieces(lname, **{
                    'first_name': fname
                })
                if not legislator:
                    data = "Bill ID: %s | fname: %s | lname %s" % (
                        bill.id, fname, lname
                    )
                    create_asana_task("History legislator mismatch", data)
                else:
                    bill.sponsor = legislator
                    bill.save()
        else:
            create_asana_task("Bill Missing History", bill.id)


@shared_task
def process_bill_diffs(bill_id):
    try:
        bill = Bill.objects.get(id=bill_id)
        for version in bill.bill_versions:
            url = version.get('url', None)
            if not url:
                return False

            page = get(url)
            soup = BeautifulSoup(page, 'html.parser')


    except Exception:
        return False
