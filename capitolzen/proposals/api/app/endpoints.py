from elasticsearch import Elasticsearch, RequestsHttpConnection

from django.conf import settings
from rest_framework import mixins
from rest_framework_elasticsearch import es_views, es_pagination, es_filters


from config.viewsets import OwnerBasedViewSet, GenericBaseViewSet
from config.filters import OrganizationFilter, BaseModelFilter
from capitolzen.proposals.models import Bill, Wrapper, Legislator, Committee
from capitolzen.proposals.documents import BillDocument
from capitolzen.proposals.api.app.serializers import (
    BillSerializer, WrapperSerializer, LegislatorSerializer,
    CommitteeSerializer
)


class BillFilter(BaseModelFilter):

    class Meta(BaseModelFilter.Meta):
        model = Bill

        fields = {
            **BaseModelFilter.Meta.fields,
            'state': ['exact'],
        }


class BillViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  GenericBaseViewSet):
    serializer_class = BillSerializer
    queryset = Bill.objects.all()
    filter_class = BillFilter
    ordering_fields = (
        'last_action_date',
        'state',
        'state_id',
        'sponsor__party'
    )
    search_fields = (
        'title',
        'sponsor__last_name',
        'sponsor__first_name',
        'state_id'
    )
    ordering = ('state', 'state_id', )


class BillSearchView(es_views.ListElasticAPIView):
    es_client = Elasticsearch(
        hosts=settings.ELASTICSEARCH_DSL['default']['hosts'],
        connection_class=RequestsHttpConnection
    )
    es_model = BillDocument
    es_paginator_class = es_pagination.ElasticLimitOffsetPagination
    es_filter_backends = (
        es_filters.ElasticFieldsFilter,
        es_filters.ElasticSearchFilter
    )
    es_filter_fields = (
        es_filters.ESFieldFilter('state', 'states'),
    )
    es_search_fields = (
        'id',
        'states',
        'status',
        'title',
        'summary',
        'created'
    )


class LegislatorViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        GenericBaseViewSet):
    serializer_class = LegislatorSerializer
    queryset = Legislator.objects.all()
    ordering = ('state', 'last_name', 'first_name')


class CommitteeViewSet(mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       GenericBaseViewSet):
    serializer_class = CommitteeSerializer
    queryset = Committee.objects.all()
    ordering = ('state', 'name')


class WrapperFilter(OrganizationFilter):
    class Meta(OrganizationFilter.Meta):
        model = Wrapper
        fields = {
            **OrganizationFilter.Meta.fields,
            'bill__state': ['exact'],
            'bill__state_id': ['exact'],
            'bill__id': ['exact'],
            'group': ['exact']
        }


class WrapperViewSet(OwnerBasedViewSet):
    serializer_class = WrapperSerializer
    filter_class = WrapperFilter
    queryset = Wrapper.objects.all()
    ordering = ('bill__state', 'bill__state_id')
