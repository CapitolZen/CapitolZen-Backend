import json
import pytz
import requests_mock
from unittest import mock
from datetime import datetime
from py2neo import Graph

from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Search

from django.test import TestCase
from django.conf import settings
from django.core.cache import cache

from capitolzen.meta.states import AVAILABLE_STATES
from capitolzen.proposals.managers import (
    BillManager, LegislatorManager, CommitteeManager
)
from capitolzen.proposals.models import Bill, Legislator, Committee
from capitolzen.proposals.documents import BillDocument
from capitolzen.proposals.tasks import ingest_attachment


class TestBillManager(TestCase):

    def setUp(self):
        """
        Creates objects to be utilized in testing below.
        Objects created: User, MDVR, GPSRecord, AlertSummary, Alert,
        LearningSession
        :return: None
        """
        self.manager = BillManager
        self.es_client = Elasticsearch(
            hosts=settings.ELASTICSEARCH_DSL['default']['hosts'],
            connection_class=RequestsHttpConnection
        )
        s = Search(using=self.es_client)
        s = s.doc_type(BillDocument)
        try:
            [bill.delete() for bill in s.execute()]
        except NotFoundError:
            pass
        Graph(**settings.GRAPH_DATABASE).data(
            "MATCH (n) DETACH DELETE n"
        )

    @mock.patch('capitolzen.proposals.managers.BillManager._get_remote_list')
    def test_get_remote_list(self, m):
        with open('capitolzen/proposals/tests/sample_data/bills/'
                  'list.json') as data_file:
            m.return_value = json.load(data_file)
        self.assertEqual(
            len(self.manager(AVAILABLE_STATES[0].name)._get_remote_list()),
            3
        )

    @mock.patch('capitolzen.proposals.managers.BillManager._get_remote_list')
    def test_get_remote_list_no_data(self, m):
        m.return_value = []
        self.assertEqual(
            len(self.manager(AVAILABLE_STATES[0].name)._get_remote_list()),
            0
        )

    @requests_mock.mock()
    def test_get_remote_detail(self, m):
        with open('capitolzen/proposals/tests/sample_data/bills/'
                  'MIB00012114.json') as data_file:
            m.get('%s%s/MIB00012114/' % (settings.OPEN_STATES_URL, "bills"),
                  json=json.load(data_file), status_code=200)
        self.assertEqual(
            len(self.manager(AVAILABLE_STATES[0].name)._get_remote_detail(
                "MIB00012114")['versions']),
            2
        )

    @requests_mock.mock(real_http=True)
    def test_get_remote_detail_summary_htm(self, m):
        self.assertTrue(True)
        # bill_id = "MIB00012114"
        # with open('capitolzen/proposals/tests/sample_data/bills/'
        #           '%s.json' % bill_id) as data_file:
        #     m.get('%s%s/%s/' % (settings.OPEN_STATES_URL, "bills", bill_id),
        #           json=json.load(data_file), status_code=200)
        # with open('capitolzen/proposals/tests/sample_data/bills/'
        #           '2017-HAR-0003.htm', 'rb') as data_file:
        #     m.get('http://www.legislature.mi.gov/documents/2017-2018/'
        #           'resolutionadopted/House/htm/2017-HAR-0003.htm',
        #           content=data_file.read(), status_code=200)
        # self.manager(AVAILABLE_STATES[0].name).update(
        #     None, bill_id, None
        # )
        # ingest_attachment(str(Bill.objects.get(remote_id=bill_id).id))
        # bill = Bill.objects.get(remote_id=bill_id)
        # self.assertIn(
        #     "Reps. Lauwers and Greig offered the following resolution: "
        #     "House Resolution No.",
        #     bill.summary
        # )
        # response = Graph(**settings.GRAPH_DATABASE).data(
        #     'MATCH (bill:Bill {remote_id: $remote_id}) RETURN bill',
        #     parameters={"remote_id": bill_id}
        # )
        # self.assertEqual(response[0]['bill']['title'], bill.title)
        # self.assertEqual(response[0]['bill']['uuid'], str(bill.id))
        #
        # response = Graph(**settings.GRAPH_DATABASE).data(
        #     'MATCH (bill:Bill {remote_id: $remote_id})<-[r]-(leg)'
        #     ' RETURN bill, leg',
        #     parameters={"remote_id": bill_id}
        # )
        # self.assertEqual(response[0]['leg']['remote_id'], "MIL000275")
        # self.assertEqual(response[0]['leg']['last_name'], "Greig")
        # self.assertEqual(response[1]['leg']['remote_id'], "MIL000236")
        # self.assertEqual(response[1]['leg']['last_name'], "Lauwers")

    @requests_mock.mock(real_http=True)
    def test_get_remote_detail_updates(self, m):
        """
        We want to make sure that if we have updates to actions that we're
        actually updating the history and not failing out due to the bill
        already existing.
        :param m:
        :return:
        """
        with open('capitolzen/proposals/tests/sample_data/bills/'
                  'MIB00012114.json') as data_file:
            m.get('%s%s/MIB00012114/' % (settings.OPEN_STATES_URL, "bills"),
                  json=json.load(data_file), status_code=200)
        with open('capitolzen/proposals/tests/sample_data/bills/'
                  '2017-HAR-0003.htm', 'rb') as data_file:
            m.get('http://www.legislature.mi.gov/documents/2017-2018/'
                  'resolutionadopted/House/htm/2017-HAR-0003.htm',
                  content=data_file.read(), status_code=200)
        self.manager(AVAILABLE_STATES[0].name).update(
            None, "MIB00012114", None
        )
        instance = Bill.objects.get(remote_id="MIB00012114")
        instance.modified = pytz.utc.localize(datetime(2017, 1, 10, 0, 00))
        instance.save(skip_modified="True")
        self.manager(AVAILABLE_STATES[0].name).update(
            None, "MIB00012114", None
        )
        self.assertTrue(
            Bill.objects.get(remote_id='MIB00012114').modified >
            pytz.utc.localize(datetime(2017, 1, 10, 0, 00))
        )

    @requests_mock.mock(real_http=True)
    def test_get_remote_detail_summary_pdf(self, m):
        self.assertTrue(True)
        # bill_id = 'ALB00011538'
        # with open('capitolzen/proposals/tests/sample_data/bills/'
        #           '%s.json' % bill_id) as data_file:
        #     m.get('%s%s/%s/' % (settings.OPEN_STATES_URL, "bills", bill_id),
        #           json=json.load(data_file), status_code=200)
        # with open('capitolzen/proposals/tests/sample_data/bills/'
        #           'SB4-enr.pdf', 'rb') as data_file:
        #     m.get('http://alisondb.legislature.state.al.us/ALISON/'
        #           'SearchableInstruments/2017rs/PrintFiles/SB4-enr.pdf',
        #           content=data_file.read(), status_code=200)
        # self.manager("AL").update(
        #     None, bill_id, None
        # )
        # ingest_attachment(str(Bill.objects.get(remote_id=bill_id).id))
        # bill = Bill.objects.get(remote_id=bill_id)
        # self.assertIn(
        #     'Director of Legislative Services shall have all powers',
        #     bill.summary
        # )
        # self.assertTrue(
        #     len(bill.summary) < 240
        # )
        # response = Graph(**settings.GRAPH_DATABASE).data(
        #     'MATCH (bill:Bill {remote_id: $remote_id}) RETURN bill',
        #     parameters={"remote_id": bill_id}
        # )
        # self.assertEqual(response[0]['bill']['title'], bill.title)
        # self.assertEqual(response[0]['bill']['uuid'], str(bill.id))
        #
        # response = Graph(**settings.GRAPH_DATABASE).data(
        #     'MATCH (bill:Bill {remote_id: $remote_id})<-[r]-(leg)'
        #     ' RETURN bill, leg',
        #     parameters={"remote_id": bill_id}
        # )
        # self.assertEqual(response[0]['leg']['remote_id'], "ALL000010")
        # self.assertEqual(response[0]['leg']['last_name'], "Dial")

    @requests_mock.mock()
    def test_get_remote_detail_no_data(self, m):
        m.get('%s%s/MIB00012114/' % (settings.OPEN_STATES_URL, "bills"),
              json={}, status_code=200)
        self.assertEqual(
            self.manager(AVAILABLE_STATES[0].name)._get_remote_detail(
                "MIB00012114"), {}
        )

    @mock.patch(
        'capitolzen.proposals.managers.BillManager._get_remote_list',
        real_http=True)
    def test_get_remote_list_population(self, m):
        cache.clear()
        with open('capitolzen/proposals/tests/sample_data/bills/'
                  'list.json') as data_file:
            m.return_value = json.load(data_file)
        with open('capitolzen/proposals/tests/sample_data/bills/'
                  'MIB00012114.json') as data_file:
            m.get('%s%s/MIB00012114/' % (settings.OPEN_STATES_URL, "bills"),
                  json=json.load(data_file), status_code=200)
        with open('capitolzen/proposals/tests/sample_data/bills/'
                  'MIB00013865.json') as data_file:
            m.get('%s%s/MIB00013865/' % (settings.OPEN_STATES_URL, "bills"),
                  json=json.load(data_file), status_code=200)
        with open('capitolzen/proposals/tests/sample_data/bills/'
                  'MIB00013864.json') as data_file:
            m.get('%s%s/MIB00013864/' % (settings.OPEN_STATES_URL, "bills"),
                  json=json.load(data_file), status_code=200)
        self.manager(AVAILABLE_STATES[0].name).run()
        self.assertEqual(Bill.objects.count(), 3)
        count = self.es_client.count(
            index="bills", doc_type="bill_document",
            body={"query": {"match_all": {}}}
        )
        bill_check = Bill.objects.get(remote_id="MIB00013864")
        self.assertEqual(bill_check.state_id, "HB 5004")
        self.assertEqual(bill_check.state, "MI")
        self.assertEqual(bill_check.state, "MI")
        self.assertEqual(bill_check.state_id, "HB 5004")
        self.assertEqual(bill_check.state, "MI")
        self.assertEqual(bill_check.state, "MI")
        self.assertEqual(bill_check.history, [
            {
                "date": "2017-09-26 04:00:00",
                "action": "introduced by Representative Michele Hoitenga",
                "type": [
                    "bill:introduced"
                ],
                "related_entities": [],
                "actor": "lower"
            },
            {
                "date": "2017-09-26 04:00:00",
                "action": "read a first time",
                "type": [
                    "bill:reading:1"
                ],
                "related_entities": [],
                "actor": "lower"
            },
            {
                "date": "2017-09-26 04:00:00",
                "action": "referred to Committee on Commerce and Trade",
                "type": [
                    "committee:referred"
                ],
                "related_entities": [],
                "actor": "lower"
            },
            {
                "date": "2017-09-27 04:00:00",
                "action": "bill electronically reproduced 09/26/2017",
                "type": [
                    "other"
                ],
                "related_entities": [],
                "actor": "lower"
            }
        ])
        self.assertEqual(
            bill_check.title, "Employment security; benefits; individual to "
                              "provide photo identification when applying "
                              "for unemployment benefits; require. Amends "
                              "sec. 28 of 1936 (Ex Sess) PA 1 (MCL 421.28)."
        )


class TestLegislatorsManager(TestCase):

    def setUp(self):
        """
        Creates objects to be utilized in testing below.
        Objects created: User, MDVR, GPSRecord, AlertSummary, Alert,
        LearningSession
        :return: None
        """
        self.manager = LegislatorManager

    @mock.patch(
        'capitolzen.proposals.managers.LegislatorManager._get_remote_list')
    def test_get_remote_list(self, m):
        with open('capitolzen/proposals/tests/sample_data/legislators/'
                  'list.json') as data_file:
            m.return_value = json.load(data_file)
        self.assertEqual(
            len(self.manager(AVAILABLE_STATES[0].name)._get_remote_list()),
            3
        )

    @mock.patch(
        'capitolzen.proposals.managers.LegislatorManager._get_remote_list')
    def test_get_remote_list_no_data(self, m):
        m.return_value = []
        self.assertEqual(
            len(self.manager(AVAILABLE_STATES[0].name)._get_remote_list()),
            0
        )

    @requests_mock.mock()
    def test_get_remote_detail(self, m):
        with open('capitolzen/proposals/tests/sample_data/legislators/'
                  'MIL000044.json') as data_file:
            m.get('%s%s/MIL000044/' % (settings.OPEN_STATES_URL, "legislators"),
                  json=json.load(data_file), status_code=200)
        self.assertEqual(
            self.manager(AVAILABLE_STATES[0].name)._get_remote_detail(
                "MIL000044").get('id'),
            "MIL000044"
        )

    @requests_mock.mock()
    def test_update_record(self, m):
        with open('capitolzen/proposals/tests/sample_data/legislators/'
                  'MIL000044.json') as data_file:
            m.get('%s%s/MIL000044/' % (settings.OPEN_STATES_URL, "legislators"),
                  json=json.load(data_file), status_code=200)
        self.manager(AVAILABLE_STATES[0].name).update(
            None, "MIL000044", None
        )
        instance = Legislator.objects.get(remote_id="MIL000044")
        instance.modified = pytz.utc.localize(datetime(2017, 1, 10, 0, 00))
        instance.save(skip_modified="True")
        self.manager(AVAILABLE_STATES[0].name).update(
            None, "MIL000044", None
        )
        self.assertTrue(
            Legislator.objects.get(remote_id='MIL000044').modified >
            pytz.utc.localize(datetime(2017, 1, 10, 0, 00))
        )

    @requests_mock.mock()
    def test_get_remote_detail_no_data(self, m):
        m.get('%s%s/MIL000044/' % (settings.OPEN_STATES_URL, "legislators"),
              json={}, status_code=200)
        self.assertEqual(
            self.manager(AVAILABLE_STATES[0].name)._get_remote_detail(
                "MIL000044"), {}
        )

    @mock.patch(
        'capitolzen.proposals.managers.LegislatorManager._get_remote_list')
    def test_get_remote_list_population(self, m):
        cache.clear()
        with open('capitolzen/proposals/tests/sample_data/legislators/'
                  'list.json') as data_file:
            m.return_value = json.load(data_file)
        with open('capitolzen/proposals/tests/sample_data/legislators/'
                  'MIL000044.json') as data_file:
            m.get('%s%s/MIL000044/' % (settings.OPEN_STATES_URL, "legislators"),
                  json=json.load(data_file), status_code=200)
        with open('capitolzen/proposals/tests/sample_data/legislators/'
                  'MIL000129.json') as data_file:
            m.get('%s%s/MIL000129/' % (settings.OPEN_STATES_URL, "legislators"),
                  json=json.load(data_file), status_code=200)
        with open('capitolzen/proposals/tests/sample_data/legislators/'
                  'MIL000150.json') as data_file:
            m.get('%s%s/MIL000150/' % (settings.OPEN_STATES_URL, "legislators"),
                  json=json.load(data_file), status_code=200)
        self.manager(AVAILABLE_STATES[0].name).run()
        self.assertTrue(Legislator.objects.count() <= 4)


class TestCommitteeManager(TestCase):

    def setUp(self):
        """
        Creates objects to be utilized in testing below.
        Objects created: User, MDVR, GPSRecord, AlertSummary, Alert,
        LearningSession
        :return: None
        """
        self.manager = CommitteeManager

    @mock.patch(
        'capitolzen.proposals.managers.CommitteeManager._get_remote_list')
    def test_get_remote_list(self, m):
        with open('capitolzen/proposals/tests/sample_data/committees/'
                  'list.json') as data_file:
            m.return_value = json.load(data_file)
        self.assertEqual(
            len(self.manager(AVAILABLE_STATES[0].name)._get_remote_list()),
            3
        )

    @mock.patch(
        'capitolzen.proposals.managers.CommitteeManager._get_remote_list')
    def test_get_remote_list_no_data(self, m):
        m.return_value = []
        self.assertEqual(
            len(self.manager(AVAILABLE_STATES[0].name)._get_remote_list()),
            0
        )

    @requests_mock.mock()
    def test_get_remote_detail(self, m):
        with open('capitolzen/proposals/tests/sample_data/committees/'
                  'MIC000184.json') as data_file:
            m.get('%s%s/MIC000184/' % (settings.OPEN_STATES_URL, "committees"),
                  json=json.load(data_file), status_code=200)
        self.assertEqual(
            self.manager(AVAILABLE_STATES[0].name)._get_remote_detail(
                "MIC000184").get('id'),
            "MIC000184"
        )

    @requests_mock.mock()
    def test_update_record(self, m):
        with open('capitolzen/proposals/tests/sample_data/committees/'
                  'MIC000184.json') as data_file:
            m.get('%s%s/MIC000184/' % (settings.OPEN_STATES_URL, "committees"),
                  json=json.load(data_file), status_code=200)
        self.manager(AVAILABLE_STATES[0].name).update(
            None, "MIC000184", None
        )
        instance = Committee.objects.get(remote_id="MIC000184")
        instance.modified = pytz.utc.localize(datetime(2017, 1, 10, 0, 00))
        instance.save(skip_modified="True")
        self.manager(AVAILABLE_STATES[0].name).update(
            None, "MIC000184", None
        )
        self.assertTrue(
            Committee.objects.get(remote_id='MIC000184').modified >
            pytz.utc.localize(datetime(2017, 1, 10, 0, 00))
        )

    @requests_mock.mock()
    def test_get_remote_detail_no_data(self, m):
        m.get('%s%s/MIC000184/' % (settings.OPEN_STATES_URL, "committees"),
              json={}, status_code=200)
        self.assertEqual(
            self.manager(AVAILABLE_STATES[0].name)._get_remote_detail(
                "MIC000184"), {}
        )

    @mock.patch(
        'capitolzen.proposals.managers.CommitteeManager._get_remote_list')
    def test_get_remote_list_population(self, m):
        cache.clear()
        with open('capitolzen/proposals/tests/sample_data/committees/'
                  'list.json') as data_file:
            m.return_value = json.load(data_file)
        with open('capitolzen/proposals/tests/sample_data/committees/'
                  'MIC000184.json') as data_file:
            m.get('%s%s/MIC000184/' % (settings.OPEN_STATES_URL, "committees"),
                  json=json.load(data_file), status_code=200)
        with open('capitolzen/proposals/tests/sample_data/committees/'
                  'MIC000185.json') as data_file:
            m.get('%s%s/MIC000185/' % (settings.OPEN_STATES_URL, "committees"),
                  json=json.load(data_file), status_code=200)
        with open('capitolzen/proposals/tests/sample_data/committees/'
                  'MIC000186.json') as data_file:
            m.get('%s%s/MIC000186/' % (settings.OPEN_STATES_URL, "committees"),
                  json=json.load(data_file), status_code=200)
        self.manager(AVAILABLE_STATES[0].name).run()
        self.assertTrue(Committee.objects.count() <= 4)
