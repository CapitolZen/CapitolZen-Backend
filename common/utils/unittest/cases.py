from rest_framework.test import APITestCase as RestAPITestCase
from capitolzen.users.tests.factories import UserFactory
from rest_framework.reverse import reverse
from django.http import QueryDict
from rest_framework import status
from datetime import datetime
import pytz
from psycopg2.extras import DateTimeTZRange


class ResourceAPITestCase(RestAPITestCase):
    """
    Non-Authorization base simple rest support.
    "Easy"(er) testing for typical happy-path crud endpoints.
    """

    def build_url_query_string(self, base_url, values):
        qdict = QueryDict('', mutable=True)
        qdict.update(values)
        return '%s?%s' % (base_url, qdict.urlencode())

    def assertQueryFilterCountIsEqual(self, values, count):
        """
        This is probably named a little too close to built in methods
        for how much it does.
        :param values:
        :param count:
        :return:
        """
        url = self.build_url_query_string(
            self.list_url,
            values
        )
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], count)

    def setUp(self):

        #
        # Make the all important user.
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

        #
        # Create the actual model that is under test.
        if (hasattr(self.__class__, '_create_resource_under_test') and
                callable(getattr(self.__class__,
                                 '_create_resource_under_test'))):

            resource = self._create_resource_under_test()
            if resource:
                self.resource = resource

        #
        # Using the resource and the resource type, we can
        # figure out most urls.
        if (getattr(self, 'resource_type_under_test', None) and
                getattr(self, 'resource', None)):
            self.detail_url = reverse(
                '%s-detail' % self.resource_type_under_test,
                kwargs={'pk': str(self.resource.id)}
            )

            self.list_url = reverse(
                '%s-list' % self.resource_type_under_test
            )


class MixinResourceListCreatedModifiedTest(object):
    """
    This is mixed with ResourceAPITestCase, and will fail without.
    """

    def test_resource_list_created_modified_filter(self):
        #
        # Setup Data
        # Delete the existing resource so we know what data we're dealing with.
        self.resource.delete()

        self._create_resource_under_test(
            created=datetime(2013, 6, 1, 0, 00),
            modified=datetime(2013, 6, 1, 0, 00))

        self._create_resource_under_test(
            created=datetime(2014, 6, 1, 0, 00),
            modified=datetime(2014, 6, 1, 0, 00))

        self._create_resource_under_test(
            created=datetime(2015, 6, 1, 0, 00),
            modified=datetime(2015, 6, 1, 0, 00))

        #
        # Created Before
        date = datetime(2015, 1, 1, 0, 00)
        filters = {
            'created_before': date.isoformat(),
        }
        count = self.resource_model.objects.filter(created__lte=date).count()
        self.assertQueryFilterCountIsEqual(filters, count)

        #
        # Created After
        date = datetime(2015, 1, 1, 0, 00)
        filters = {
            'created_after': date.isoformat(),
        }
        count = self.resource_model.objects.filter(created__gte=date).count()
        self.assertQueryFilterCountIsEqual(filters, count)

        #
        # Modified Before
        date = datetime(2015, 1, 1, 0, 00)
        filters = {
            'modified_before': date.isoformat(),
        }
        count = self.resource_model.objects.filter(modified__lte=date).count()
        self.assertQueryFilterCountIsEqual(filters, count)

        #
        # Modified After
        date = datetime(2015, 1, 1, 0, 00)
        filters = {
            'modified_after': date.isoformat(),
        }
        count = self.resource_model.objects.filter(modified__gte=date).count()
        self.assertQueryFilterCountIsEqual(filters, count)


class MixinResourceListTimeframeTest(object):
    """
    This is mixed with ResourceAPITestCase, and will fail without.
    """

    def test_resource_list_timeframe_filter(self):
        #
        # Setup Data
        # Delete the existing resource so we know what data we're dealing with.
        self.resource.delete()

        self._create_resource_under_test(
            timeframe=DateTimeTZRange(datetime(2013, 6, 1, 0, 00),
                                      datetime(2013, 6, 2, 0, 00))
        )



        #
        # Timeframe At (Has Results)
        date = datetime(2013, 6, 1, 12, 00, tzinfo=pytz.utc)
        filters = {
            'timeframe_at': date.isoformat(),
        }
        count = self.resource_model.objects.filter(
            timeframe__contains=date).count()
        self.assertQueryFilterCountIsEqual(filters, count)

        #
        # Timeframe Range (Has Results)
        start = datetime(2013, 6, 1, 0, 00, tzinfo=pytz.utc)
        end = datetime(2013, 6, 3, 0, 00, tzinfo=pytz.utc)

        filters = {
            'timeframe_range': '%s,%s' % (start.isoformat(), end.isoformat()),
        }

        count = self.resource_model.objects.filter(
            timeframe__overlap=DateTimeTZRange(start, end)).count()
        self.assertQueryFilterCountIsEqual(filters, count)

        #
        # Timeframe At (No Results)
        date = datetime(2012, 6, 1, 12, 00, tzinfo=pytz.utc)
        filters = {
            'timeframe_at': date.isoformat(),
        }
        count = self.resource_model.objects.filter(
            timeframe__contains=date).count()
        self.assertQueryFilterCountIsEqual(filters, count)

        #
        # Timeframe Range  (No Results)
        start = datetime(2012, 6, 1, 0, 00, tzinfo=pytz.utc)
        end = datetime(2012, 6, 3, 0, 00, tzinfo=pytz.utc)

        filters = {
            'timeframe_range': '%s,%s' % (start.isoformat(), end.isoformat()),
        }

        count = self.resource_model.objects.filter(
            timeframe__overlap=DateTimeTZRange(start, end)).count()
        self.assertQueryFilterCountIsEqual(filters, count)
