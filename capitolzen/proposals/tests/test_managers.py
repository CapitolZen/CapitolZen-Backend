import json
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
    BillManager
)
from capitolzen.proposals.models import Bill
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

    @requests_mock.mock()
    def test_get_remote_detail_no_data(self, m):
        m.get('%s%s/MIB00012114/' % (settings.OPEN_STATES_URL, "bills"),
              json={}, status_code=200)
        self.assertEqual(
            self.manager(AVAILABLE_STATES[0].name)._get_remote_detail(
                "MIB00012114"), {}
        )

    @mock.patch(
        'capitolzen.proposals.managers.BillManager._get_remote_list')
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
