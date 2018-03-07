from django_filters import rest_framework as filters
from django_filters import STRICTNESS
from .filters import UUIDInFilter


class BaseModelFilterSet(filters.FilterSet):
    """
    Filtering for attributes that are included on almost all models.
    """
    id = UUIDInFilter(
        name='id',
        label='ID',
        help_text='Id of resource. Multiple values can be '
                  'provided by separating them with a comma')

    created_before = filters.IsoDateTimeFilter(
        name='created',
        label='Created Before',
        help_text='ISO-8601. Example: 2017-09-16T15:16:12Z',
        lookup_expr='lte')

    created_after = filters.IsoDateTimeFilter(
        name='created',
        label='Created After',
        help_text='ISO-8601. Example: 2017-09-16T15:16:12Z',
        lookup_expr='gte')

    modified_before = filters.IsoDateTimeFilter(
        name='modified',
        label='modified Before',
        help_text='ISO-8601. Example: 2017-09-16T15:16:12Z',
        lookup_expr='lte')

    modified_after = filters.IsoDateTimeFilter(
        name='modified',
        label='modified After',
        help_text='ISO-8601. Example: 2017-09-16T15:16:12Z',
        lookup_expr='gte')

    class Meta:
        strict = STRICTNESS.RAISE_VALIDATION_ERROR
        fields = {
            'created': ['lt', 'gt'],
            'modified': ['lt', 'gt'],
        }


class OrganizationFilterSet(BaseModelFilterSet):
    """
    Filter Set
    Filtering for models that are owned by a user.
    Note: Need to hide this from the swagger docs.
    """
    organization = filters.CharFilter(
        name='organization',
        lookup_expr='exact',
        label='Organization',
        method='filter_organization',
        help_text='Only used for super-accounts'
    )

    def filter_organization(self, queryset, name, value):
        return queryset.filter(owner__username=value)

    class Meta(BaseModelFilterSet.Meta):
        fields = {**BaseModelFilterSet.Meta.fields}


class GroupFilterSet(BaseModelFilterSet):
    group = filters.CharFilter(
        method='filter_group'
    )

    def filter_group(self, queryset, name, value):
        return queryset.filter(group__id=value)

    class Meta(BaseModelFilterSet):
        fields = {**BaseModelFilterSet.Meta.fields}
