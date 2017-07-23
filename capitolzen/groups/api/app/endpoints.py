from json import loads
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from dry_rest_permissions.generics import (DRYPermissions,
                                           DRYPermissionFiltersBase)

from capitolzen.proposals.models import Bill, Wrapper
from capitolzen.groups.models import Group, Report
from capitolzen.groups.tasks import generate_report, async_generate_report
from .serializers import GroupSerializer, ReportSerializer


class GroupFilterBackend(DRYPermissionFiltersBase):
    def filter_list_queryset(self, request, queryset, view):
        # TODO Add filtering here
        return queryset


class GroupViewSet(viewsets.ModelViewSet):

    def get_serializer_class(self):
        return GroupSerializer

    def get_queryset(self):
        user = self.request.user
        return Group.objects.filter(organization__users=user)

    @list_route(methods=['GET'])
    def bills(self, request):
        # TODO: Finish this
        return Response({"stuff": "here"})

    @detail_route(methods=['POST'])
    def add_bill(self, request, pk=None):
        if not pk:
            Response({"status_code": status.HTTP_400_BAD_REQUEST, "message": "Missing requirement"})\
                .status_code(status.HTTP_400_BAD_REQUEST)
        group = Group.objects.get(pk=pk)
        data = request.body.decode('utf-8')
        data = loads(data)
        bills = Bill.objects.filter(id__in=data['bills'])
        bill_list = []
        for bill in bills:
            w = Wrapper.objects.create(
                                       organization=group.organization,
                                       bill=bill,
                                       )
            w.save()
            bill_list.append(w.id)

        return Response({"status_code": status.HTTP_200_OK, "message": "Bill(s) added", "bills": bill_list})

    permission_classes = (DRYPermissions,)
    filter_backends = (GroupFilterBackend, DjangoFilterBackend)


class ReportViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        queryset = Report.objects.filter(organization__users=self.request.user)
        return queryset

    serializer_class = ReportSerializer
    permission_classes = (DRYPermissions,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    filter_fields = ('organization', 'group', 'created', 'status', 'title', 'user')

    def perform_create(self, serializer):
        serializer.save()
        report = serializer.instance
        report.generate()

    @detail_route(methods=['GET'])
    def url(self, request, pk):
        report = Report.objects.get(pk=pk)
        url = generate_report(report)
        return Response({"uhoh": "hotdog", "url": url, "status_code": status.HTTP_200_OK})
