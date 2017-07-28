from collections import namedtuple
from json import dumps, loads
from requests import get
from celery import shared_task
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from capitolzen.proposals.models import Bill, Legislator, Committee
from capitolzen.meta.states import AVAILABLE_STATES

OPEN_STATES_KEY = settings.OPEN_STATES_KEY
OPEN_STATES_URL = settings.OPEN_STATES_URL

HEADERS = {
    "X-API-KEY": OPEN_STATES_KEY
}


@shared_task
def update_bills():
    for state in AVAILABLE_STATES:
        update_state_bills.delay(state)


@shared_task
def update_state_bills(state):
    chambers = ['upper', 'lower']
    for chamber in chambers:
        bills = _list_state_bills(state, chamber)
        for b in bills:
            try:
                bill = Bill.objects.get(remote_id=b.id)
                update_bill.delay(localid=bill.id, sourceid=b.id)
            except ObjectDoesNotExist:
                new_bill = Bill.objects.create(remote_id=b.id)
                new_bill.save()
                update_bill.delay(localid=new_bill.id, sourceid=b.id)


@shared_task
def update_bill(localid, sourceid):
    bill = Bill.objects.get(id=localid)
    source = _get_state_bill(sourceid)
    bill.update_from_source(source)


def _list_state_bills(state, chamber):
    url = "%s/bills/" % OPEN_STATES_URL

    r = get(url, params={"state": state, "chamber": chamber})
    return loads(r.json())


def _get_state_bill(bill):
    url = "%s/bills/%s/" % (OPEN_STATES_URL, bill)
    r = get(url)
    return loads(r.json())
