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
                     'categories', 'status', 'state', 'committee')


class WrapperViewSet(viewsets.ModelViewSet):
    permission_classes = (DRYPermissions,)
    serializer_class = WrapperSerializer
    queryset = Wrapper.objects.all()
