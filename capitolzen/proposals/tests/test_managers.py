import json
import requests_mock
from unittest import mock

from django.test import TestCase
from django.conf import settings
from django.core.cache import cache

from capitolzen.meta.states import AVAILABLE_STATES
from capitolzen.proposals.managers import (
    BillManager
)
from capitolzen.proposals.models import Bill


class TestBillManager(TestCase):

    def setUp(self):
        """
        Creates objects to be utilized in testing below.
        Objects created: User, MDVR, GPSRecord, AlertSummary, Alert,
        LearningSession
        :return: None
        """
        self.manager = BillManager

    @mock.patch('capitolzen.proposals.managers.BillManager._get_remote_list')
    def test_get_remote_list(self, m):
        """
        Tests get_average_idle_time_last_day: tests that zero is returned
        :return: 0 (ZeroDivisionError)
        """
        with open('capitolzen/proposals/tests/sample_data/bills/'
                  'list.json') as data_file:
            m.return_value = json.load(data_file)
        self.assertEqual(
            len(self.manager(AVAILABLE_STATES[0].name)._get_remote_list()),
            3
        )

    @mock.patch('capitolzen.proposals.managers.BillManager._get_remote_list')
    def test_get_remote_list_no_data(self, m):
        """
        Tests get_average_idle_time_last_day: tests that zero is returned
        :return: 0 (ZeroDivisionError)
        """
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
    def test_get_remote_detail(self, m):
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
