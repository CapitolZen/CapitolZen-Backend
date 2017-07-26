from collections import namedtuple
from json import dumps, loads
from requests import request
from celery import shared_task
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

OPEN_STATES_KEY = settings.OPEN_STATES_KEY
OPEN_STATES_URL = 'https://openstates.org/api/v1/'

HEADERS = {
    "X-API-KEY": OPEN_STATES_KEY
}


def list_state_bills(state=False):
    url = "%s/bills/" % OPEN_STATES_URL

    r = request('get', )
