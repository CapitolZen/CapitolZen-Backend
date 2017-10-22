import json
import base64
import requests_mock
from unittest import mock

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
        with open('capitolzen/proposals/tests/sample_data/bills/'
                  'MIB00012114.json') as data_file:
            m.get('%s%s/MIB00012114/' % (settings.OPEN_STATES_URL, "bills"),
                  json=json.load(data_file), status_code=200)
        with open('capitolzen/proposals/tests/sample_data/bills/'
                  '2017-HAR-0003.htm', 'rb') as data_file:
            m.get('http://www.legislature.mi.gov/documents/2017-2018/'
                  'resolutionadopted/House/htm/2017-HAR-0003.htm',
                  content=data_file.read(), status_code=200)
        response = self.manager(AVAILABLE_STATES[0].name).update(
            None, "MIB00012114", None
        )
        self.assertIn(
            "House Resolution No. A resolution",
            Bill.objects.get(remote_id='MIB00012114').summary
        )

    @requests_mock.mock(real_http=True)
    def test_get_remote_detail_summary_pdf(self, m):
        with open('capitolzen/proposals/tests/sample_data/bills/'
                  'ALB00011538.json') as data_file:
            m.get('%s%s/ALB00011538/' % (settings.OPEN_STATES_URL, "bills"),
                  json=json.load(data_file), status_code=200)
        with open('capitolzen/proposals/tests/sample_data/bills/'
                  'SB4-enr.pdf', 'rb') as data_file:
            m.get('http://alisondb.legislature.state.al.us/ALISON/'
                  'SearchableInstruments/2017rs/PrintFiles/SB4-enr.pdf',
                  content=data_file.read(), status_code=200)
        self.manager("AL").update(
            None, "ALB00011538", None
        )
        self.assertIn(
            'Services shall serve as Secretary of the Legislative Council  '
            '3 without salary other than his compensation as Director of the',
            Bill.objects.get(remote_id='ALB00011538').summary
        )

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
        self.assertEqual(count.get('count'), 3)


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
        self.assertEqual(Legislator.objects.count(), 3)


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
        self.assertEqual(Committee.objects.count(), 3)
