from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from dry_rest_permissions.generics import (DRYPermissions,
                                           DRYPermissionFiltersBase)
from capitolzen.proposals.models import Bill, Wrapper
from .serializers import BillSerializer, WrapperSerializer


class BillViewSet(viewsets.ReadOnlyModelViewSet):
    class Meta:
        ordering = ['state', 'state_id']

    permission_classes = (IsAuthenticated,)
    serializer_class = BillSerializer
    queryset = Bill.objects.all().order_by('state', 'state_id')
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('sponsor', 'title', 'state_id', 'summary',
                     'categories', 'status', 'state', 'current_committee')


class WrapperViewSet(viewsets.ModelViewSet):
    class Meta:
        ordering = ['bill__state', 'bill__state_id']

    permission_classes = (DRYPermissions,)
    serializer_class = WrapperSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filter_fields = ('bill__state', 'group')

    def get_queryset(self):
        return Wrapper.objects.filter(organization__user=self.request.user),

