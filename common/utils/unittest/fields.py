import random
import datetime
from django.contrib.gis.geos import Point
from factory.fuzzy import BaseFuzzyAttribute, FuzzyDateTime
from psycopg2.extras import DateTimeTZRange


class FuzzyPoint(BaseFuzzyAttribute):
    """
    Random GIS point
    """
    def fuzz(self):
        return Point(random.uniform(-180.0, 180.0),
                     random.uniform(-90.0, 90.0))


class FuzzyDateTimeRange(FuzzyDateTime):
    """
    60 min datetime range...
    """
    def fuzz(self):
        start_date = super(FuzzyDateTimeRange, self).fuzz()
        end_date = start_date + datetime.timedelta(minutes=60)
        return DateTimeTZRange(start_date, end_date)