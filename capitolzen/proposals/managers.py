from pytz import timezone
from django.conf import settings
from django.core.cache import cache

from requests import get
import feedparser
from bs4 import BeautifulSoup

import dateutil.parser

from capitolzen.meta.notifications import create_asana_task

from capitolzen.proposals.models import (
    Bill, Legislator, Committee, Event, Wrapper
)
from capitolzen.proposals.api.app.serializers import (
    BillSerializer, LegislatorSerializer, CommitteeSerializer
)

from capitolzen.users.models import Action

from logging import getLogger

logger = getLogger('app')


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
        """
        TODO: If error, delete cache key so we can re-run
        :return:
        """
        # Make sure this is thread / worker friendly and we're not trying
        # to update the same thing twice
        if cache.get(self.cache_key) is None:
            cache.set(self.cache_key, self.cache_value, None)
            for resource in self._get_remote_list():
                remote_id = resource.pop('id')
                self.update(None, remote_id, resource)
            cache.delete(self.cache_key)

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
        try:
            instance = Committee.objects.get(remote_id=remote_id)
        except Committee.DoesNotExist:
            instance = None
        serializer = CommitteeSerializer(instance, data={
            'remote_id': remote_id,
            **source
        })
        if not serializer.is_valid():
            logger.error(serializer.errors)
            logger.error(serializer.initial_data)
            return None
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
            except ValueError as e:
                continue

        return full_list_of_bills

    @staticmethod
    def _cleanup_source(source):
        if source.get('bill_id'):
            source['state_id'] = source.pop('bill_id')
        if source.get('actions'):
            source['history'] = source.pop('actions')
        if source.get('versions'):
            source['bill_versions'] = source.pop('versions')
        if isinstance(source.get('type'), list):
            source['type'] = ",".join(source.get('type'))
        return source

    def update(self, local_id, remote_id, resource_info):
        source = self._get_remote_detail(remote_id)

        source = self._cleanup_source(source)

        try:
            instance = Bill.objects.get(remote_id=remote_id)
        except Bill.DoesNotExist:
            instance = None
        serializer = BillSerializer(instance, data={
            'remote_id': remote_id,
            **source
        })
        if not serializer.is_valid():
            logger.error(serializer.errors)
            logger.error(serializer.initial_data)
            return None
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
        from capitolzen.proposals.graphs import LegislatorGraph
        source = self._get_remote_detail(remote_id)
        try:
            instance = Legislator.objects.get(remote_id=remote_id)
        except Legislator.DoesNotExist:
            instance = None
        serializer = LegislatorSerializer(instance, data={
            'remote_id': remote_id,
            **source
        })
        if not serializer.is_valid():
            logger.error(serializer.errors)
            logger.error(serializer.initial_data)
            return None
        instance = serializer.save()
        try:
            LegislatorGraph(identifier=instance.id).run()
        except OSError:
            pass
        return instance

    def run(self):
        for human in self._get_remote_list():
            self.update(None, human['id'], human)


class EventManager(object):
    current_session = settings.CURRENT_SESSION
    index = "committee_meetings"

    def __init__(self, state):
        self.url = state.committee_rss
        self.state = state.name
        self.timezone = timezone(state.timezone)
        self.committee = None

    def _get_remote_list_response(self):
        feed = feedparser.parse(self.url)
        return feed['items']

    def update(self, entry):
        parts = entry['description'].split('-')
        chamber = 'lower' if parts[0].lower() == 'house' else 'upper'

        committee = Committee.objects.filter(
            chamber=chamber,
            name__icontains=parts[1].strip(),
        ).first()

        if not committee:
            logger.error("No commitee matching string found")
            msg = 'Committee Remote name: `%s`' % parts[1].strip()
            msg += "no committee found for meeeting %s" % entry['link']
            create_asana_task('Committee:Missing %s' % parts[1].strip(), msg)
            return None

        self.committee = committee

        args = {
            "chamber": chamber,
            "url": entry['link'],
            "remote_id": entry['guid'],
            "committee": committee,
            "state": self.state,
        }

        events = Event.objects.filter(**args)

        if not events:
            try:
                self.populate_model(entry, args)
            except Exception:
                logger.error('problem creating `event` model')
        else:
            if parts[-1] == 'canceled' and len(events) == 1:
                events[0].objects.delete()

    def populate_model(self, entry, args):
        page = get(entry['link'])

        soup = BeautifulSoup(page.content, 'html.parser')
        table = soup.find('table',  id="frg_committeemeeting_MeetingTable")
        rows = table.find_all('tr')
        # Set location
        args['location_text'] = rows[2].contents[2].string

        # Set Date/Time
        date = rows[3].contents[2].string
        parts = date.split(',')
        date = parts[1].strip()
        time = rows[4].find_all('td')[1].string.lower().replace('.', '').strip()

        # Need to add this here to split for these random type of times
        time_pieces = time.split('or immed')
        time = time_pieces[0]
        time = time.replace('noon', 'pm')
        time_string = "%s %s %s" % (date, time, self.timezone)
        time_object = dateutil.parser.parse(time_string)
        args['time'] = time_object

        agenda = rows[5].find_all('td')[1]

        bill_list = []
        for link in agenda.find_all('a'):
            bill_list.append(link.string)

        for a in agenda.find_all('a'):
            a.unwrap()

        args['description'] = str(agenda)

        if len(bill_list):
            uuid_list = []
            for state_id in bill_list:
                try:
                    b = Bill.objects.get(state_id=state_id)
                    uuid_list.append(b.id)
                except Exception:
                    continue
            args['attachments'] = [{"billlist": uuid_list}]
        event = Event.objects.create(**args)
        event.save()
        if len(bill_list):
            self.generate_actions(event, bill_list)


    def generate_actions(self, event, bill_list):
        meta = {
            'eventid': event.id
        }
        if self.committee:
            meta["committee_id"] = self.committee.id
        for bill in bill_list:
            for wrapper in Wrapper.objects.filter(bill__state_id=bill):
                if wrapper.group.active:
                    for user in wrapper.group.assigned_to.all():
                        action = Action.objects.create(
                            title='wrapper:committee_scheduled',
                            priority=2,
                            user=user,
                            action_object=wrapper,
                            metadata=meta
                        )
                        action.save()


    def is_updating(self):
        return False

    def run(self):
        items = self._get_remote_list_response()
        for item in items:
            self.update(item)


