from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from dry_rest_permissions.generics import (DRYPermissions,
                                           DRYPermissionFiltersBase)
from capitolzen.proposals.models import Bill, Wrapper, Legislator, Committee
from .serializers import BillSerializer, WrapperSerializer, LegislatorSerializer, CommitteeSerializer


class BillFilterBackend(DRYPermissionFiltersBase):
    def filter_list_queryset(self, request, queryset, view):
        # TODO: Add in org/state availability filtering
        return queryset


class BillViewSet(viewsets.ReadOnlyModelViewSet):
    class Meta:
        ordering = ['state', 'state_id']

    permission_classes = (IsAuthenticated,)
    serializer_class = BillSerializer
    queryset = Bill.objects.all()
    filter_backends = (BillFilterBackend, DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    ordering_fields = ('last_action_date', 'state', 'state_id', 'sponsor__party')
    search_fields = ('title', 'sponsor__last_name', 'sponsor__first_name', 'state_id')


class LegislatorViewSet(viewsets.ReadOnlyModelViewSet):
    class Meta:
        ordering = ['state', 'last_name', 'first_name']

    permission_classes = (IsAuthenticated, )
    serializer_class = LegislatorSerializer
    queryset = Legislator.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)


class CommitteeViewSet(viewsets.ReadOnlyModelViewSet):
    class Meta:
        ordering = ['state', 'name']

    permission_classes = (IsAuthenticated,)
    serializer_class = CommitteeSerializer
    queryset = Committee.objects.all()


class WrapperFilter(filters.FilterSet):
    class Meta:
        model = Wrapper
        fields = ['bill__state', 'bill__state_id', 'bill__id', 'organization', 'group']


class WrapperViewSet(viewsets.ModelViewSet):
    class Meta:
        ordering = ['bill__state', 'bill__state_id']

    permission_classes = (DRYPermissions,)
    serializer_class = WrapperSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filter_class = WrapperFilter

    def get_queryset(self):
        return Wrapper.objects.filter(organization__users=self.request.user)

