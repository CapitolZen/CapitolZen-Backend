from datetime import datetime
from pytz import UTC
from json import dumps
from requests import get
from celery import shared_task
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from capitolzen.meta.clients import aws_client
from capitolzen.proposals.models import Bill, Legislator, Committee
from capitolzen.proposals.api.app.serializers import BillSerializer
from capitolzen.meta.states import AVAILABLE_STATES

OPEN_STATES_KEY = settings.OPEN_STATES_KEY
OPEN_STATES_URL = settings.OPEN_STATES_URL
INDEX_LAMBDA = settings.INDEX_LAMBDA


HEADERS = {
    "X-API-KEY": OPEN_STATES_KEY
}


@shared_task
def update_all_bills():
    for state in AVAILABLE_STATES:
        update_state_bills(state.name)


@shared_task
def update_state_bills(state):
    chambers = ['upper', 'lower']
    for chamber in chambers:
        bills = _list_state_bills(state, chamber)
        for b in bills:
            try:
                bill = Bill.objects.get(remote_id=b['id'])
                if bill.modified < _time_convert(b['updated_at']):
                    update_bill.delay(localid=str(bill.id), sourceid=b['id'])
            except ObjectDoesNotExist:
                new_bill = Bill.objects.create(remote_id=b['id'], state=state)
                new_bill.save()
                update_bill.delay(localid=str(new_bill.id), sourceid=b['id'])


@shared_task
def update_bill(localid, sourceid):
    bill = Bill.objects.get(id=localid)
    source = _get_state_bill(sourceid)
    bill.update_from_source(source)
    serializer = BillSerializer(bill)
    c = aws_client()

    versions = bill.bill_versions

    if len(versions):
        v = versions[-1]
        payload = {
            "url": v["url"],
            "state": bill.state,
            "bill": serializer.data
        }
        payload = dumps(payload)
        c.invoke(
            FunctionName=INDEX_LAMBDA,
            InvocationType='Event',
            Payload=payload
        )



@shared_task
def update_state_legislators(state):
    humans = _list_state_legislators(state)
    for human in humans:
        try:
            l = Legislator.objects.get(remote_id=human['id'])
            if l.modified < _time_convert(human['updated_at']):
                update_legislator.delay(localid=l.id, remoteid=human['id'])
        except ObjectDoesNotExist:
            new_leg = Legislator.objects.create(remote_id=human['id'])
            new_leg.save()
            update_legislator.delay(localid=new_leg.id, remoteid=human['id'])


@shared_task
def update_legislator(localid, remoteid):
    leg = Legislator.objects.get(id=localid)
    source = _get_legislator(remoteid)
    leg.update_from_source(source)


@shared_task
def update_state_committees(state):
    cmtes = _get_committees(state)
    for cm in cmtes:
        try:
            c = Committee.objects.get(remote_id=cm['id'])

            if c.modified < _time_convert(cm['updated_at']):
                c.name = cm['committee']
                c.subcommittee = cm.get('subcommittee', None)
                c.save()

        except ObjectDoesNotExist:
            c = Committee.objects.create(
                remote_id=cm['id'],
                state=cm['state'],
                chamber=cm['chamber'],
                name=cm['committee'],
                subcommittee=cm.get('subcommittee', None),
                parent_id=cm['parent_id'],
            )
            c.save()


def _list_state_bills(state, chamber):
    url = "%s/bills/" % OPEN_STATES_URL

    r = get(url,
            params={"state": state, "chamber": chamber, "search_window": "session"},
            headers=HEADERS
            )
    return r.json()


def _get_state_bill(bill):
    url = "%s/bills/%s/" % (OPEN_STATES_URL, bill)
    r = get(url, headers=HEADERS)
    return r.json()


def _list_state_legislators(state):
    url = "%s/legislators/" % OPEN_STATES_URL
    r = get(url, params={"state": state, "active": True}, headers=HEADERS)
    return r.json()


def _get_legislator(remoteid):
    url = "%s/legislators/%s/" % (OPEN_STATES_URL, remoteid)
    r = get(url, headers=HEADERS)
    return r.json()


def _get_committees(state):
    url = "%s/committees/" % OPEN_STATES_URL
    r = get(url, headers=HEADERS, params={"state": state})
    return r.json()


def _time_convert(time):
    utc = UTC
    return utc.localize(datetime.strptime(time, '%Y-%m-%d %I:%M:%S'))


def bootstrap(state):
    print('updating committees')
    update_state_committees(state)
    chambers = ['upper', 'lower']
    for chamber in chambers:
        print('getting bills for chamber')
        bills = _list_state_bills(state, chamber)
        for b in bills:
            try:
                bill = Bill.objects.get(remote_id=b['id'])
                if bill.modified < _time_convert(b['updated_at']):
                    update_bill(localid=bill.id, sourceid=b['id'])
            except ObjectDoesNotExist:
                new_bill = Bill.objects.create(remote_id=b['id'], state=state)
                new_bill.save()
                update_bill(localid=new_bill.id, sourceid=b['id'])


def import_leg(state):
    humans = _list_state_legislators(state)
    for human in humans:
        l = Legislator.objects.create(remote_id=human['id'])
        l.save()
        update_legislator(l.id, human['id'])

