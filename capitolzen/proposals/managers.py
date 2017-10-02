from datetime import datetime
from pytz import UTC
from requests import get

from django.conf import settings
from django.core.cache import cache

from capitolzen.proposals.models import Legislator
from capitolzen.proposals.models import Bill, Committee


class CongressionalManager(object):
    headers = {
        "X-API-KEY": settings.OPEN_STATES_KEY
    }
    domain = settings.OPEN_STATES_URL
    state = None
    index = None
    cache_key = "%s-%s" % (index, state)
    cache_value = "updating"
    url = None

    def __init__(self, state):
        self.state = state
        self.url = "%s%s/" % (self.domain, self.index)

    def _time_convert(self, time):
        utc = UTC
        return utc.localize(datetime.strptime(time, '%Y-%m-%d %I:%M:%S'))

    def _get_remote_detail_response(self, identifier):
        return None

    def _get_remote_list_response(self):
        raise NotImplementedError()

    def _get_remote_list(self):
        try:
            return self._get_remote_list_response().json()
        except ValueError:
            return []

    def _get_remote_detail(self, identifier):
        response = self._get_remote_detail_response(identifier)
        if response is not None:
            try:
                return response.json()
            except ValueError:
                return {}
        return {}

    def update(self, local_id, remote_id, resource_info):
        raise NotImplementedError()

    def is_updating(self):
        return cache.get(self.cache_key) == self.cache_value

    def run(self):
        # Make sure this is thread / worker friendly and we're not trying
        # to update the same thing twice
        if cache.get(self.cache_key) is None:
            cache.set(self.cache_key, self.cache_value, None)
            for resource in self._get_remote_list():
                remote_id = resource.pop('id')
                self.update(None, remote_id, resource)
            cache.delete(self.cache_key)

        return True


class CommitteeManager(CongressionalManager):
    index = "committees"

    def _get_remote_list_response(self):
        return get(
            self.url, headers=self.headers, params={"state": self.state}
        )

    def update(self, local_id, remote_id, resource_info):
        committee, created = Committee.objects.get_or_create(
            remote_id=remote_id,
            defaults={
                'remote_id': remote_id,
                'state': resource_info['state'],
                'chamber': resource_info['chamber'],
                'name': resource_info['committee'],
                'subcommittee': resource_info.get('subcommittee', None),
                'parent_id': resource_info['parent_id']
            }
        )
        if committee.modified < self._time_convert(resource_info['updated_at']):
            committee.name = resource_info['committee']
            committee.subcommittee = resource_info.get('subcommittee', None)
            committee.save()
        return committee


class BillManager(CongressionalManager):
    chambers = ['upper', 'lower']
    index = "bills"

    def _get_remote_list(self):
        full_list_of_bills = []
        for chamber in self.chambers:
            response = get(
                self.url,
                params={
                    "state": self.state,
                    "chamber": chamber,
                    "search_window": "session"
                },
                headers=self.headers
            )
            try:
                full_list_of_bills += response.json()
            except ValueError:
                continue

        return full_list_of_bills

    def _get_remote_detail_response(self, identifier):
        url = "%s%s/%s/" % (self.url, self.state, identifier)
        return get(url, headers=self.headers)

    def update(self, local_id, remote_id, resource_info):
        resource_info.pop('bill_id')

        bill_info = self._get_remote_detail(remote_id)
        if bill_info.get('created_at'):
            bill_info['created_at'] = self._time_convert(
                bill_info.get('created_at')
            )
        if bill_info.get('updated_at'):
            resource_info['updated_at'] = self._time_convert(
                resource_info.pop('updated_at')
            )
        bill, created = Bill.objects.get_or_create(
            remote_id=remote_id,
            defaults={
                "state": self.state,
                **bill_info
            }
        )
        if bill.modified < self._time_convert(resource_info['updated_at']) or \
                created:
            source = self._get_remote_detail(bill.remote_id)
            bill.update_from_source(source)
            if bill.bill_versions:
                bill.current_version = bill.bill_versions[-1].get('url')
            bill.save()


class LegislatorManager(CongressionalManager):
    index = "legislators"

    def _get_remote_detail_response(self, identifier):
        return get("%s%s" % (self.url, identifier), headers=self.headers)

    def _get_remote_list_response(self):
        return get(
            self.url, params={"state": self.state, "active": True},
            headers=self.headers
        )

    def update(self, local_id, remote_id, resource_info):
        legislator = Legislator.objects.get_or_create(
            remote_id=remote_id,
            **resource_info
        )
        source = self._get_remote_detail(remote_id)
        legislator.update_from_source(source)

    def run(self):
        for human in self._get_remote_list():
            self.update(None, human['id'], human)
