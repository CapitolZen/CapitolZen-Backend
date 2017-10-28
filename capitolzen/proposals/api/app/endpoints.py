import json
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch, RequestsHttpConnection

from django.db.models import Q
from django.conf import settings

from django_filters import rest_framework as filters

from rest_framework.decorators import list_route
from rest_framework import mixins, status
from rest_framework.response import Response

from rest_framework_elasticsearch import es_views, es_pagination, es_filters

from common.utils.filters.sets import OrganizationFilterSet, BaseModelFilterSet
from common.utils.filters.filters import UUIDInFilter

from config.viewsets import OwnerBasedViewSet, GenericBaseViewSet
from capitolzen.groups.models import Group
from capitolzen.proposals.models import Bill, Wrapper, Legislator, Committee
from capitolzen.proposals.documents import BillDocument
from capitolzen.proposals.api.app.serializers import (
    BillSerializer, WrapperSerializer, LegislatorSerializer,
    CommitteeSerializer
)


class BillFilter(BaseModelFilterSet):
    sponsor_name = filters.CharFilter(
        name='sponsor__name', method='sponsor_full_name'
    )
    state = filters.CharFilter(
        name='state',
        lookup_expr=['exact', 'contains'],
        label='State',
        help_text='State in which a Bill is located'
    )
    state_id = filters.CharFilter(
        name="state_id",
        lookup_expr=['exact', 'contains'],
        label="State ID",
        help_text="ID of State in which the Bill is located"
    )
    title = filters.CharFilter(
        name='title',
        lookup_expr=['exact', 'contains'],
        label="Title",
        help_text="Title of Bill"
    )
    introduced_in = filters.CharFilter(
        name='first', method='action_date_filter'
    )
    active_in = filters.CharFilter(
        name='last', method='action_date_filter'
    )

    def sponsor_full_name(self, queryset, name, value):
        return queryset.filter(Q(sponsor__first_name__contains=value) | Q(sponsor__last_name__contains=value))

    def action_date_filter(self, queryset, name, value):
        today = datetime.today()
        date_range = today - timedelta(days=int(value))
        params = {}
        key = "action_dates__%s__range" % name
        params[key] = [str(date_range), str(today)]
        return queryset.filter(**params)

    introduced_range = filters.CharFilter(name='first', method='action_date_range_filter')
    active_range = filters.CharFilter(name='last', method='action_date_range_filter')

    def action_date_range_filter(self, queryset, name, value):
        params = {}
        key = "action_dates__%s__range" % name
        parts = value.split(',')
        params[key] = [parts[0], parts[1]]
        return queryset.filter(**params)

    class Meta(BaseModelFilterSet.Meta):
        model = Bill


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

    @list_route(methods=['GET'])
    def list_saved(self, request):
        wrappers = Wrapper.objects.filter(organization__users=request.user).prefetch_related('bill')
        bill_list = []
        for wrapper in wrappers:
            if any(b.id == wrapper.bill.id for b in bill_list):
                bill_list.append(wrapper.bil)

        serializer = BillSerializer(bill_list, many=True)
        return Response(serializer.data)


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
        '^title',
    )


class LegislatorFilter(BaseModelFilterSet):
    class Meta:
        model = Legislator
        fields = {
            'first_name': ['exact', 'contains'],
            'last_name': ['exact', 'contains'],
            'party': ['exact'],
        }


class LegislatorViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        GenericBaseViewSet):
    serializer_class = LegislatorSerializer
    queryset = Legislator.objects.all()
    filter_class = LegislatorFilter
    ordering = ('state', 'last_name', 'first_name')


class CommitteeViewSet(mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       GenericBaseViewSet):
    serializer_class = CommitteeSerializer
    queryset = Committee.objects.all()
    ordering = ('state', 'name')


class WrapperFilter(OrganizationFilterSet):
    state = filters.CharFilter(
        name='state',
        label='State',
        method='filter_bill_by_state',
        help_text='State in which a Bill is located'
    )

    state_id = filters.CharFilter(
        name='state_id',
        label='State ID',
        method='filter_bill_by_state_id',
        help_text='ID of State in which a Bill is located'
    )

    bill_id = UUIDInFilter(
        name='bill_id',
        lookup_expr='exact',
        label='Bill ID',
        method='filter_bill_by_id',
        help_text='ID of Bill'
    )

    group = filters.CharFilter(
        name='group',
        lookup_expr='exact',
        label='Group',
        help_text='Group associated with the Bill'
    )

    def filter_bill_by_state(self, queryset, name, value):
        return queryset.filter(bill__state=value)

    def filter_bill_by_state_id(self, queryset, name, value):
        return queryset.filter(bill__state_id=value)

    def filter_bill_by_id(self, queryset, name, value):
        return queryset.filter(bill__id=value)

    class Meta(OrganizationFilterSet.Meta):
        model = Wrapper
        fields = {
            'organization': ['exact'],
            'position': ['exact'],
            'summary': ['in'],
            'starred': ['exact'],
            'group': ['exact']
        }


class WrapperViewSet(OwnerBasedViewSet):
    serializer_class = WrapperSerializer
    filter_class = WrapperFilter
    ordering = ('bill__state', 'bill__state_id')

    def get_queryset(self):
        return Wrapper.objects.filter(
            organization__users=self.request.user
        )

    @list_route(methods=['POST'])
    def filter_wrappers(self, request):
        data = json.loads(request.body)
        group = data.get('group', False)
        if not group:
            return Response({
                "message": "group required",
                "status_code": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST
            )
        group = Group.objects.get(pk=data['group'])
        wrappers = Wrapper.objects.filter(group=group)
        wrapper_filters = data.get('filters', False)
        if wrapper_filters:
            wrappers = wrappers.filter(**wrapper_filters)

        serialized = WrapperSerializer(wrappers, many=True)
        return Response(serialized.data)
