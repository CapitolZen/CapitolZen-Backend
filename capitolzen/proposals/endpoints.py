from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from dry_rest_permissions.generics import (DRYPermissions,
                                           DRYPermissionFiltersBase)
from .models import Bill, Wrapper
from .serializers import BillSerializer, WrapperSerializer


class BillViewSet(viewsets.ReadOnlyModelViewSet):
    class Meta:
        ordering = ['state', 'state_id']

    permission_classes = (IsAuthenticated,)
    serializer_class = BillSerializer
    queryset = Bill.objects.all().order_by('state', 'state_id')
