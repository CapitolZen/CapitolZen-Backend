import json
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch, RequestsHttpConnection

from django.db.models import Q
from django.conf import settings
from django.http import HttpResponse

from django_filters import rest_framework as filters

from rest_framework.decorators import list_route, detail_route
from rest_framework import mixins, status
from rest_framework.response import Response

from rest_framework_elasticsearch import es_views, es_pagination, es_filters

from common.utils.filters.sets import OrganizationFilterSet, BaseModelFilterSet
from common.utils.filters.filters import UUIDInFilter

from config.viewsets import OwnerBasedViewSet, GenericBaseViewSet
from capitolzen.groups.models import Group, prepare_report_filters
from capitolzen.proposals.models import Bill, Wrapper, Legislator, Committee, Event
from capitolzen.proposals.documents import BillDocument
from capitolzen.proposals.api.app.serializers import (
    BillSerializer, WrapperSerializer, LegislatorSerializer,
    CommitteeSerializer, EventSerializer
)
from capitolzen.groups.models import Report


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

    committee = UUIDInFilter(
        name='current_committee__id',
        label='Committee ID',
        help_text='ID of Committee'
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
        'state',
        'state_id',
        'sponsor__party',
        'last_action_date',
    )
    search_fields = (
        'title',
        'sponsor__last_name',
        'sponsor__first_name',
        'state_id',
        'current_committee__name'
    )
    ordering = ('state', 'state_id', )

    @detail_route(methods=['GET'])
    def vote(self, request, pk=None):
        bill = self.get_object()
        data = {}
        for vote in bill.votes:

            yes_ids = [i['leg_id'] for i in vote['yes_votes']]
            no_ids = [i['leg_id'] for i in vote['no_votes']]

            yays = Legislator.objects.filter(id__in=yes_ids)
            nays = Legislator.objects.filter(id__in=no_ids)

            record_list = []

            for yay in yays:
                record = {
                    'vote': 'support',
                    'name': yay.full_name,
                    'id': str(yay.id),
                    'party': yay.party
                }
                record_list.append(record)

            for nay in nays:
                record = {
                    'vote': 'oppose',
                    'name': nay.full_name,
                    'id': str(nay.id),
                    'party': nay.party
                }
                record_list.append(record)

            data[vote['chamber']] = record_list

        return Response({'data': data})


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
        'title',
        'content',
        'summary',
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


class CommitteeFilter(BaseModelFilterSet):
    class Meta:
        model = Committee
        fields = {
            'chamber': ['exact'],
            'name': ['exact', 'contains'],
            'state': ['exact', 'contains']
        }

class CommitteeViewSet(mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       GenericBaseViewSet):
    serializer_class = CommitteeSerializer
    filter_class = CommitteeFilter
    queryset = Committee.objects.all()
    ordering = ('state', 'name')

    search_fields = (
        'name',
        'subcommittee'
    )


class EventFilter(BaseModelFilterSet):
    future = filters.BooleanFilter(
        method='future_events_filter'
    )

    def future_events_filter(self, queryset, name, value):
        return queryset.filter(time__gte=datetime.today())


    class Meta:
        model = Event
        fields = {
            'state': ['exact'],
            'chamber': ['exact'],
            'event_type': ['exact'],
            'time': ['lt', 'lte', 'gte', 'gt', 'exact']
        }


class EventViewSet(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   GenericBaseViewSet):
    serializer_class = EventSerializer
    filter_class = EventFilter
    queryset = Event.objects.all()

    ordering = ('time', )
    search_fields = (
        'description',
        'committee__name',
        'location_text'
    )


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
        name='bill__id',
        label='Bill ID',
        help_text='ID of Bill'
    )

    group = filters.CharFilter(
        name='group',
        lookup_expr='exact',
        label='Group',
        help_text='Group associated with the Bill'
    )

    group_title = filters.CharFilter(
        name='group__title',
        lookup_expr='contains',
        label='Group Title',
        help_text='title of group'
    )

    report = filters.UUIDFilter(
        name='report', label='Report', method='filter_report')

    introduced_range = filters.CharFilter(name='first', method='action_date_range_filter')
    active_range = filters.CharFilter(name='last', method='action_date_range_filter')

    def filter_bill_by_state(self, queryset, name, value):
        return queryset.filter(bill__state=value)

    def filter_bill_by_state_id(self, queryset, name, value):
        return queryset.filter(bill__state_id=value)

    def filter_bill_by_id(self, queryset, name, value):
        return queryset.filter(bill__id=value)

    def action_date_range_filter(self, queryset, name, value):
        params = {}
        key = "bill__action_dates__%s__range" % name
        parts = value.split(',')
        params[key] = [parts[0], parts[1]]
        return queryset.filter(**params)

    def filter_report(self, queryset, name, value):
        try:
            report = Report.objects.get(id=value)
        except Report.DoesNotExist:
            return queryset

        queryset = queryset.filter(group=report.group)
        if report.filter:
            prepared_filters = prepare_report_filters(report.filter)
            return queryset.filter(**prepared_filters)

        return queryset

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
    ordering_fields = ('bill__updated_at',)

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
            prepared_filters = prepare_report_filters(wrapper_filters)
            wrappers = wrappers.filter(**prepared_filters)

        serialized = WrapperSerializer(wrappers, many=True)
        return Response(serialized.data)
