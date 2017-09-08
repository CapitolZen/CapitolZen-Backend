from django_filters import rest_framework as filters
from django_filters import Filter, fields


class BaseModelFilter(filters.FilterSet):
    """
    Filter Set
    Filtering for attributes that are included on almost all models.
    """
    class Meta:
        fields = {
            'id': ['exact'],
            'created': ['lt', 'gt'],
            'modified': ['lt', 'gt'],
        }


class OrganizationFilter(BaseModelFilter):
    """
    Filter Set
    Filtering for models that are owned by a user.
    """
    organization = filters.CharFilter(
        name='organization',
        label='Organization',
        method='filter_organization',
    )

    def filter_organization(self, queryset, name, value):
        return queryset.filter(owner__username=value)

    class Meta(BaseModelFilter.Meta):
        fields = {
            **BaseModelFilter.Meta.fields,
            'organization': ['exact']
        }
