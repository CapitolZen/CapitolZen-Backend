from collections import namedtuple
from json import dumps, loads
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from capitolzen.meta.states import AVAILABLE_STATES
from capitolzen.meta.clients import aws_client
from .models import Bill


SEARCH_FUNCTION = 'capitolzen_search_bills'


@shared_task
def update_all_bills():
    for state in AVAILABLE_STATES:
        bills = Bill.objects.filter(state=state.name)
        for bill in bills:
            update_bill_from_source(state=state.name, bill_id=bill.state_id)


@shared_task
def get_new_bills():

    BillStruct = namedtuple('BillStruct', 'state_id')

    for state in AVAILABLE_STATES:
        lower_bills = Bill.objects \
            .filter(state=state.name, state_id__startswith=state.lower_bill_prefix) \
            .order_by('state_id')\
            .reverse()

        if not lower_bills.count():
            lower_start = "%s-%s" % (state.lower_bill_prefix, state.lower_bill_start)
            lower_bills = BillStruct(state_id=lower_start)
        else:
            lower_bills = lower_bills[0]

        upper_bills = Bill.objects \
            .filter(state=state.name, state_id__startswith=state.upper_bill_prefix) \
            .order_by('state_id')\
            .reverse()

        if not upper_bills.count():
            upper_start = "%s-%s" % (state.upper_bill_prefix, state.upper_bill_start)
            upper_bills = BillStruct(state_id=upper_start)
        else:
            upper_bills = upper_bills[0]

        billies = [lower_bills, upper_bills]
        for bill in billies:
            res = fetch_data(state.name, bill.state_id)
            data = res.get('data', None)
            if not data:
                continue

            create_bill_from_source(state.name, bill.state_id, data)

            next_bill = res.get('nextBill', False)
            if next_bill:
                new_res = fetch_data(state.name, next_bill)
                data = new_res.get('data', False)
                if data:
                    create_bill_from_source(data['state'], data['state_id'], data)


def create_bill_from_source(state, state_id, data):
    exists = bill_exists(state, state_id,)
    if exists:
        update_bill(state, state_id, data)
    else:
        new_bill = Bill.objects.create()

        setattr(new_bill, 'state_id', data['state_id'])
        setattr(new_bill, 'state', data['state'])
        setattr(new_bill, 'title', data['title'])
        setattr(new_bill, 'sponsor', data['sponsor'])
        setattr(new_bill, 'summary', data['summary'])
        setattr(new_bill, 'status', data['status'])
        setattr(new_bill, 'current_committee', data['current_committee'])
        setattr(new_bill, 'versions', data['versions'])
        setattr(new_bill, 'history', data['history'])
        setattr(new_bill, 'last_action_date', data['last_action_date'])
        setattr(new_bill, 'remote_url', data['remote_url'])
        # new_bill.serialize_categories(data.categories)
        new_bill.save()


def update_bill_from_source(state, bill_id):
    response = fetch_data(state=state, bill_id=bill_id)
    data = response.get('data', False)
    if not data:
        return None
    output = {'next_bill': False}
    try:
        bill = Bill.objects.get(state_id=data['stateId'], state=data['state'])
        bill.update_from_source(data)
        output['outcome'] = "Bill %s %s Updated" % (state, bill_id)
    except Exception:
        output['outcome'] = "Bill not found"

    return output


def bulk_import(state_id):
    state = AVAILABLE_STATES[state_id]
    lower_start = "%s-%s" % (state['lower_bill_prefix'], state['lower_bill_start'])
    upper_start = "%s-%s" % (state['upper_bill_prefix'], state['upper_bill_start'])
    update_bill_from_source(state['id'], lower_start)
    update_bill_from_source(state['id'], upper_start)


def fetch_data(state, bill_id):
    event = dumps({"state": state, "billId": bill_id})
    func = aws_client('lambda')
    res = func.invoke(FunctionName=SEARCH_FUNCTION,
                      InvocationType="RequestResponse",
                      Payload=event,
                      )
    status = res.get('StatusCode', False)
    if status != 200:
        return None

    response = res['Payload'].read()
    return loads(response)


def update_bill(state, state_id, data):
    bill = Bill.objects.get(state=state, state_id=state_id)
    bill.update_from_source(data)


def bill_exists(state, state_id):
    try:
        Bill.objects.get(state=state, state_id=state_id)
        return True
    except MultipleObjectsReturned:
        # TODO: add logging/error reporting here
        return True
    except ObjectDoesNotExist:
        return False
