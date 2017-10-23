from django_filters import rest_framework as filters
from psycopg2.extras import DateTimeTZRange

__all__ = ['UUIDInFilter',
           'DateTimeRangeContainsFilter',
           'DateTimeRangeOverlapFilter']


class UUIDInFilter(filters.BaseInFilter, filters.UUIDFilter):
    """
    Mixing an In Filter + uuid filter will validate uuid formats
    and allow for multiple values to be filtered on.
    """
    pass


class DateTimeRangeContainsFilter(filters.IsoDateTimeFilter):
    """
    Given a specific datetime, give me all the things that were happening
    """
    def filter(self, qs, value):
        filter = {
            '%s__%s' % (self.name, 'contains'): value,
        }
        return qs.filter(**filter)


class DateTimeRangeOverlapFilter(filters.BaseRangeFilter, filters.IsoDateTimeFilter):
    """
    Given two datetimes, give me all the things that were happening.
    """
    def filter(self, qs, value):
        datetime_range = DateTimeTZRange(value[0], value[1])
        filter = {
            '%s__%s' % (self.name, 'overlap'): datetime_range,
        }
        return qs.filter(**filter)
