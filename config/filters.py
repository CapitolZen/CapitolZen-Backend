from django_filters import rest_framework as filters


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
    class Meta(BaseModelFilter.Meta):
        fields = {
            **BaseModelFilter.Meta.fields,
            'organization': ['exact']
        }
