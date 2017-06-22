from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from dry_rest_permissions.generics import (DRYPermissions,
                                           DRYPermissionFiltersBase)

from capitolzen.proposals.models import Bill, Wrapper
from .models import Group
from .serializers import GroupSerializer


class GroupFilterBackend(DRYPermissionFiltersBase):
    def filter_list_queryset(self, request, queryset, view):
        # TODO Add filtering here
        return queryset


class GroupViewSet(viewsets.ModelViewSet):

    def get_serializer_class(self):
        return GroupSerializer

    @detail_route(methods=['post'])
    def add_bill(self, request):
        group = self.get_object()
        print(request['bill_id'])
        bill = Bill.objects.get(request['bill_id'])
        w = Wrapper(
            organization=request.user.organization,
            bill=bill
        )
        w.update_group(group.id, request.position)
        w.save()
        Response({"status_code": status.HTTP_200_OK, "detail": "Bill added", "wrapper": w})

    permission_classes = (DRYPermissions,)
    queryset = Group.objects.all()
    filter_backends = (GroupFilterBackend, DjangoFilterBackend)
