from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
import rest_framework_filters as drffilter
from dry_rest_permissions.generics import (DRYPermissions,
                                           DRYPermissionFiltersBase)
from capitolzen.proposals.models import Bill, Wrapper, Legislator, Committee
from .serializers import BillSerializer, WrapperSerializer, LegislatorSerializer, CommitteeSerializer


class BillFilter(drffilter.FilterSet):
    # sponsor = drffilter.RelatedFilter(LegislatorFilter, name='sponsor', queryset=Legislator.objects.all())

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


class LegislatorFilter(drffilter.FilterSet):
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


class WrapperFilter(drffilter.FilterSet):
    bill = drffilter.RelatedFilter(BillFilter, name='bill', queryset=Bill.objects.all())

    class Meta:
        model = Wrapper
        fields = {
                    'organization': ['exact'],
                    'group': ['in'],
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

