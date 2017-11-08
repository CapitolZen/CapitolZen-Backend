from requests import get

from django.conf import settings
from django.core.cache import cache

from capitolzen.proposals.models import Bill
from capitolzen.proposals.api.app.serializers import (
    BillSerializer, LegislatorSerializer, CommitteeSerializer
)


class CongressionalManager(object):
    headers = {
        "X-API-KEY": settings.OPEN_STATES_KEY,
        'content-type': 'application/json'
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

    def _get_remote_detail_response(self, identifier):
        return get("%s%s/" % (self.url, identifier), headers=self.headers)

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
                response_json = response.json()
                return response_json
            except ValueError as e:
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
        source = self._get_remote_detail(remote_id)
        source['name'] = source.pop('committee', None)
        serializer = CommitteeSerializer(data={
            'remote_id': remote_id,
            **source
        })
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return instance


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

    def update(self, local_id, remote_id, resource_info):
        source = self._get_remote_detail(remote_id)

        if source.get('bill_id'):
            source['state_id'] = source.pop('bill_id')
        if source.get('actions'):
            source['history'] = source.pop('actions')
        if source.get('versions'):
            source['bill_versions'] = source.pop('versions')
        if isinstance(source.get('type'), list):
            source['type'] = ",".join(source.get('type'))
        try:
            instance = Bill.objects.get(remote_id=remote_id)
        except Bill.DoesNotExist:
            instance = None
        serializer = BillSerializer(instance, data={
            'remote_id': remote_id,
            **source
        })
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return instance


class LegislatorManager(CongressionalManager):
    index = "legislators"

    def _get_remote_list_response(self):
        return get(
            self.url, params={"state": self.state, "active": True},
            headers=self.headers
        )

    def update(self, local_id, remote_id, resource_info):
        source = self._get_remote_detail(remote_id)
        serializer = LegislatorSerializer(data={
            'remote_id': remote_id,
            **source
        })
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return instance

    def run(self):
        for human in self._get_remote_list():
            self.update(None, human['id'], human)
