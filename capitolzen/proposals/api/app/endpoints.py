from json import loads
from django.db.models import Q
from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import list_route
from rest_framework.response import Response
from dry_rest_permissions.generics import (DRYPermissions, )
from capitolzen.groups.models import Group
from capitolzen.proposals.models import Bill, Wrapper, Legislator, Committee
from .serializers import BillSerializer, WrapperSerializer, LegislatorSerializer, CommitteeSerializer


class BillFilter(FilterSet):
    sponsor_name = CharFilter(name='sponsor__name', method='sponsor_full_name')

    def sponsor_full_name(self, queryset, name, value):
        return queryset.filter(Q(sponsor__first_name__contains=value) | Q(sponsor__last_name__contains=value))

    class Meta:
        model = Bill
        fields = {
            'state': ['exact', 'contains'],
            'state_id': ['exact', 'contains'],
            'title': ['contains', 'exact'],
        }


class BillViewSet(viewsets.ReadOnlyModelViewSet):
    class Meta:
        ordering = ['state', 'state_id']

    permission_classes = (IsAuthenticated,)
    serializer_class = BillSerializer
    queryset = Bill.objects.all()
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    filter_class = BillFilter
    ordering_fields = ('last_action_date', 'state', 'state_id',)
    search_fields = ('title', 'sponsor__last_name', 'sponsor__first_name', 'state_id')


class LegislatorFilter(FilterSet):
    class Meta:
        model = Legislator
        fields = {
            'first_name': ['exact', 'contains'],
            'last_name': ['exact', 'contains'],
            'party': ['exact'],
        }


class LegislatorViewSet(viewsets.ReadOnlyModelViewSet):
    class Meta:
        ordering = ['state', 'last_name', 'first_name']

    permission_classes = (IsAuthenticated, )
    serializer_class = LegislatorSerializer
    queryset = Legislator.objects.all()
    filter_class = LegislatorFilter
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)


class CommitteeViewSet(viewsets.ReadOnlyModelViewSet):
    class Meta:
        ordering = ['state', 'name']

    permission_classes = (IsAuthenticated,)
    serializer_class = CommitteeSerializer
    queryset = Committee.objects.all()


class WrapperFilter(FilterSet):
    state_id = CharFilter(name='bill__state_id')
    state = CharFilter(name='bill__state')

    class Meta:
        model = Wrapper
        fields = {
                    'organization': ['exact'],
                    'group': ['exact'],
                    'position': ['exact'],
                    'summary': ['in'],
                    'starred': ['exact']
                 }


class WrapperViewSet(viewsets.ModelViewSet):
    class Meta:
        ordering = ['bill__state', 'bill__state_id']

    permission_classes = (DRYPermissions,)
    serializer_class = WrapperSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filter_class = WrapperFilter

    def get_queryset(self):
        return Wrapper.objects.filter(organization__users=self.request.user)

    @list_route(methods=['POST'])
    def filter_wrappers(self, request):
        data = loads(request.body)
        group = data.get('group', False)
        if not group:
            return Response({"message": "group required", "status_code": status.HTTP_400_BAD_REQUEST},
                            status=status.HTTP_400_BAD_REQUEST)
        group = Group.objects.get(pk=data['group'])
        wrappers = Wrapper.objects.filter(group=group)
        wrapper_filters = data.get('filters', False)
        if wrapper_filters:
            wrappers = wrappers.filter(**wrapper_filters)

        serialized = WrapperSerializer(wrappers, many=True)
        return Response(serialized.data)
