from json import loads
from logging import getLogger

from django_filters import rest_framework as filters
from rest_framework import status, exceptions
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from common.utils.filters.sets import OrganizationFilterSet
from config.viewsets import OwnerBasedViewSet
from capitolzen.proposals.models import Bill, Wrapper
from capitolzen.proposals.api.app.serializers import BillSerializer
from capitolzen.groups.models import Group, Report, File
from capitolzen.groups.tasks import generate_report, email_report
from capitolzen.groups.api.app.serializers import (
    GroupSerializer, ReportSerializer, FileSerializer
)

logger = getLogger('app_logger')


class GroupFilter(OrganizationFilterSet):
    title = filters.CharFilter(
        name='title',
        label='Title',
        help_text='Title of a Group',
        lookup_expr='exact')

    starred = filters.CharFilter(
        name='starred',
        label="Starred",
        help_text="Starred groups",
        lookup_expr='exact'
    )

    organization = filters.CharFilter(
        name="organization",
        label="Organization",
        help_text="Filter Groups based on Organziation"
    )

    active = filters.BooleanFilter(
        name="active",
        label="Active",
        help_text="Filter Groups based on whether or not they are active"
    )

    without_bill = filters.CharFilter(
        method='without_bill_filter',
        help_text="Filter Groups on a Bill They Do Not Have"
    )

    def without_bill_filter(self, queryset, name, value):
        return queryset.exclude(wrapper__bill__id=value)

    class Meta(OrganizationFilterSet.Meta):
        model = Group


class GroupViewSet(OwnerBasedViewSet):
    serializer_class = GroupSerializer
    filter_class = GroupFilter
    queryset = Group.objects.all()

    @list_route(methods=['GET'], serializer_class=BillSerializer)
    def bills(self, request):
        # TODO do we want to grab bills for a single group or is this meant
        # to retrieve all the bills for all the groups under an org?
        # If we want to do the first one this should be a detail route
        group = self.filter_queryset(self.get_queryset()).last()
        if group is None:
            raise exceptions.NotFound()
        organization = group.organization
        queryset = [wrapper.bill for wrapper in organization.wrapper_set.all()]
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['POST'])
    def add_bill(self, request, pk=None):
        if not pk:
            Response(
                {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "message": "Missing requirement"
                }
            ).status_code(status.HTTP_400_BAD_REQUEST)
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
            bill_list.append(w.id)

        return Response({"status_code": status.HTTP_200_OK,
                         "message": "Bill(s) added", "bills": bill_list})


class ReportFilter(OrganizationFilterSet):
    user = filters.CharFilter(
        name='user',
        label='User',
        method='filter_user',
    )

    title = filters.CharFilter(
        name='title',
        label='Title',
        help_text='Title of a Report',
        lookup_expr='exact')

    group = filters.CharFilter(
        name='group',
        label='Group',
        help_text='Id of group',
        lookup_expr='exact'
    )

    def filter_user(self, queryset, name, value):
        return queryset.filter(user__username=value)

    class Meta(OrganizationFilterSet.Meta):
        model = Report


class ReportViewSet(OwnerBasedViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    filter_class = ReportFilter
    filter_fields = (
        'organization',
        'group',
        'status',
        'title',
        'user'
    )

    def perform_create(self, serializer):
        serializer.save()
        report = serializer.instance
        try:
            generate_report(report)
        except Exception as e:
            logger.exception(e)

    @detail_route(methods=['GET'])
    def url(self, request, pk):
        report = Report.objects.get(pk=pk)
        url = generate_report(report)
        if url:
            return Response({
                "message": "report generated",
                "url": url,
                "status_code": status.HTTP_200_OK
            })
        else:
            return Response({
                "message": "error generating report",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
            })

    @detail_route(methods=['GET'])
    def send_report(self, request, pk):
        email_report.delay(report=pk, user=request.user.id)
        return Response({
            "status_code": status.HTTP_200_OK,
            "message": "Report hopefully emailed"
        })


class FileFilter(OrganizationFilterSet):
    class Meta:
        model = File
        ordering = ['name']
        fields = {
            'id': ['exact'],
            'created': ['lt', 'gt'],
            'modified': ['lt', 'gt'],
            'name': ['icontains'],
        }
    search_fields = ('file', 'name', 'description')


class FileViewSet(OwnerBasedViewSet):

    def get_queryset(self):
        return File.objects.filter(organization__users=self.request.user)

    filter_class = FileFilter
    serializer_class = FileSerializer
