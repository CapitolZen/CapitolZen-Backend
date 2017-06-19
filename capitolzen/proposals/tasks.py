from celery import shared_task
from json import dumps, loads
from capitolzen.meta.states import AVAILABLE_STATES
from capitolzen.meta.clients import aws_client
from .models import Bill


SEARCH_FUNCTION = 'capitolzen_search_bills'


@shared_task
def update_all_bills():
    for state in AVAILABLE_STATES:
        bills = Bill.objects.filter(state=state['id'])
        for bill in bills:
            update_bill_from_source(state=state['id'], bill_id=bill['state_id'])


@shared_task
def get_new_bills():
    for state in AVAILABLE_STATES:
        lower_bills = Bill.objects \
            .filter(state=state['id'], state_id__startswith=state['lower_bill_prefix']) \
            .order_by('state_id')\
            .reverse()[0]

        upper_bills = Bill.objects \
            .filter(state=state['id'], state_id__startswith=state['upper_bill_prefix']) \
            .order_by('state_id')\
            .reverse()[0]

        billies = [lower_bills, upper_bills]
        for g in billies:
            res = fetch_data(state['id'], g.state_id)
            next_bill = res.get('nextBill', False)
            print(next_bill)
            if next_bill:
                new_res = fetch_data(state['id'], next_bill)
                data = new_res.get('data', False)
                if data:
                    create_bill_from_source(data)


def create_bill_from_source(data):
    new_bill = Bill.objects.create(
        state_id=data['stateId'],
        state=data['state'],
        title=data['title'],
        sponsor=data['sponsor'],
        summary=data['summary'],
        status=data['status'],
        committee=data['currentCommittee'],
    )

    # new_bill.serialize_history(data.history)
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

