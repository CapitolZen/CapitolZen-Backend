from celery import shared_task
from boto3 import client
from json import dumps
from capitolzen.meta.states import AVAILABLE_STATES
from .models import Bill
from pprint import pprint


SEARCH_FUNCTION = 'downdraft_search_bills'


@shared_task
def update_all_bills():
    for state in AVAILABLE_STATES:
        lower_start = "%s-%s" % state.lower_bill_prefx, state.lower_bill_start
        upper_start = "%s-%s" % state.upper_bill_prefx, state.upper_bill_start
        trigger_function(state.id, lower_start)
        trigger_function(state.id, upper_start)


def trigger_function(state, bill_id):
    event = dumps({"state": state, "billId": bill_id})
    func = client('lambda')
    res = func.invoke(
        FunctionName=SEARCH_FUNCTION,
        InvocationType="RequestResponse",
        Payload=event
                      )

    data = res.Payload.read()
    pprint(data)
    # if data.nextBill:
    #     trigger_function(state, data.nextBill)

