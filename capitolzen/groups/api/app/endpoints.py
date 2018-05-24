from logging import getLogger

from django.db.models import Count

from django_filters import rest_framework as filters

from rest_framework import status, exceptions
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from dry_rest_permissions.generics import (
   DRYPermissionFiltersBase
)


from common.utils.filters.sets import OrganizationFilterSet, GroupFilterSet
from common.utils.filters.filters import UUIDInFilter, IntInFilter

from config.viewsets import OwnerBasedViewSet

from capitolzen.proposals.models import Wrapper
from capitolzen.proposals.api.app.serializers import BillSerializer

from capitolzen.groups.models import Group, Report, File, Page, Link, Update
from capitolzen.groups.tasks import generate_report, email_report
from capitolzen.groups.api.app.serializers import (
    GroupSerializer, ReportSerializer, FileSerializer, PageSerializer, LinkSerializer, UpdateSerializer,
    AnonGroupSerializer, UpdateSerializerPageable, GeneratedReportDownloadSerializer
)

logger = getLogger('app')


class GroupFilter(OrganizationFilterSet):

    starred = filters.BooleanFilter(
        name='starred',
        label="Starred",
        help_text="Starred groups",
    )

    organization = filters.CharFilter(
        name="organization",
        label="Organization",
        help_text="Filter Groups based on Organization"
    )

    active = filters.BooleanFilter(
        name="active",
        label="Active",
        help_text="Filter Groups based on whether or not they are active"
    )

    without_bills = UUIDInFilter(
        name="wrapper__bill__id",
        label="without bill",
        exclude=True,
        help_text="Filter Groups on a Bill They Do Not Have"
    )

    has_page = filters.BooleanFilter(
        name="page",
        label="has page",
        help_text="Filter groups have page",
        method='filter_page'
    )

    def filter_page(self, queryset, name, value):
        if value:
            return queryset.exclude(page__isnull=True)
        else:
            return queryset.exclude(page__isnull=False)

    assigned_to = IntInFilter(
        name="assigned_to",
        label="Assigned To",
        help_text="Assigned to user by id."
    )

    class Meta(OrganizationFilterSet.Meta):
        model = Group
        fields = {
            'title': ['exact', 'icontains']
        }


class GroupViewSet(OwnerBasedViewSet):
    filter_class = GroupFilter
    queryset = Group.objects.all()
    ordering = ('title',)
    ordering_fields = ('title', 'created', 'modified', 'active')
    search_fields = ('title', 'description')

    def get_serializer_class(self):
        user = self.request.user
        if user.is_anonymous:
            return AnonGroupSerializer
        org = getattr(self.request, 'organization', False)
        if org and self.request.organization.is_guest(user):
            return AnonGroupSerializer

        return GroupSerializer


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

    @detail_route(methods=['GET'])
    def stats(self, request, pk=None):
        self.check_permissions(request)
        group = self.get_object()
        all_saved = Wrapper.objects.filter(group=group)
        lower_passed = all_saved.exclude(bill__action_dates__passed_lower__isnull=False).count()
        upper_passed = all_saved.exclude(bill__action_dates__passed_upper__isnull=False).count()
        signed = all_saved.exclude(bill__action_dates__signed__isnull=False).count()
        opposed = all_saved.filter(position='opposed').count()
        support = all_saved.filter(position='support').count()
        neutral = all_saved.filter(position='neutral').count()
        noposition = all_saved.filter(position='none').count()

        committee_bill_query = Wrapper.objects.filter(group=group)\
            .values('bill__current_committee__id', 'bill__current_committee__name', 'bill__current_committee__chamber')\
            .annotate(num_vals=Count('id'))\
            .order_by('-num_vals')[:5]


        top_committees = []
        for cmte in committee_bill_query:
            summary = {
                'cmte_id': str(cmte['bill__current_committee__id']),
                'name': cmte['bill__current_committee__name'],
                'chamber': cmte['bill__current_committee__chamber'],
                'count': cmte['num_vals'],
            }
            top_committees.append(summary)

        data = {
            'upper_passed_count': upper_passed,
            'saved_count': all_saved.count(),
            'lower_passed_count': lower_passed,
            'signed': signed,
            'top_committees': top_committees,
            'support_count': support,
            'oppose_count': opposed,
            'neutral_count': neutral,
            'none_count': noposition
        }
        return Response({"status_code": status.HTTP_200_OK, "stats": data})

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

    search_fields = (
        'title',
        'user__name',
        'group__title',
        'description'
    )

    # prefetch_for_includes = {
    #     '__all__': [],
    # }

    def perform_create(self, serializer):
        serializer.save()
        report = serializer.instance
        try:
            generate_report(report)
        except Exception as e:
            logger.exception(e)

    @detail_route(methods=['GET'])
    def url(self, request, pk):
        self.check_permissions(request)
        try:
            report = Report.objects.get(pk=pk)
            self.check_object_permissions(request, report)
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
        except Exception:
            return Response({
                "message": "report not found",
                "status_code": status.HTTP_404_NOT_FOUND
            })

    @detail_route(methods=['GET'])
    def send_report(self, request, pk):
        email_report.delay(report=pk, user=request.user.id)
        return Response({
            "status_code": status.HTTP_200_OK,
            "message": "Report hopefully emailed"
        })

    @list_route(methods=['POST'], serializer_class=GeneratedReportDownloadSerializer)
    def generate(self, request):
        self.check_permissions(request)
        data = request.data
        data['organization'] = str(request.organization.id)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        url = serializer.save()
        print(url)
        if url:
            return Response({
                "message": "report generated",
                "url": url,
                "status_code": status.HTTP_200_OK
            })
        else:
            return Response({
                "message": "error generating report",
                "status_code": status.HTTP_400_BAD_REQUEST
            })


class FileFilter(OrganizationFilterSet):
    group = filters.CharFilter(
        name='group',
        label='Group',
        help_text='Id of group',
        lookup_expr='exact'
    )
    class Meta:
        model = File
        fields = {
            'id': ['exact'],
            'created': ['lt', 'gt'],
            'modified': ['lt', 'gt'],
            'name': ['icontains'],
        }


class FileViewSet(OwnerBasedViewSet):

    def get_queryset(self):
        return File.objects.filter(organization__users=self.request.user)

    filter_class = FileFilter
    serializer_class = FileSerializer
    ordering = ['name']
    ordering_fields = ['created', 'modified']
    search_fields = ('file', 'name', 'description')



class PageFilter(GroupFilterSet):
    class Meta:
        model = Page
        fields = {
            'group': ['exact'],
            'author': ['exact'],
            'visibility': ['exact'],
            'published': ['exact'],
            **GroupFilterSet.Meta.fields
        }


class PageViewSet(OwnerBasedViewSet):
    filter_class = PageFilter
    serializer_class = PageSerializer
    queryset = Page.objects.all()
    ordering = ['title']
    search_fields = ('title', 'author__name', 'description', 'group__title')


class UpdateFilterBackend(DRYPermissionFiltersBase):
    def filter_list_queryset(self, request, queryset, view):
        org = getattr(request, 'organization', None)
        if org and org.is_admin(request.user):
            return queryset.filter()
        if getattr(request, 'page', False):
            return queryset.filter(page=request.page)

        return queryset

class UpdateFilterSet(GroupFilterSet):

    group_page = filters.CharFilter(
        method='filter_page',
        lookup_expr='exact',
        name='page',
    )

    def filter_page(self, queryset, name, value):
        return queryset.filter(page__id=value)

    class Meta:
        model = Update
        fields = {
            'user': ['exact'],
            'published': ['exact'],
            'group_page': ['exact'],
            **GroupFilterSet.Meta.fields
        }

class UpdateViewSet(OwnerBasedViewSet):
    queryset = Update.objects.all()
    ordering = ['-created']
    search_fields = ('title', 'document')
    filter_class = UpdateFilterSet
    filter_backends = (UpdateFilterBackend, DjangoFilterBackend, OrderingFilter)

    def get_serializer_class(self, *args, **kwargs):
        if self.request.GET.get('pageable', False) in ['True', 'true', 1, '1', 'yep', 'sure']:
            return UpdateSerializerPageable
        return UpdateSerializer

class LinkFilterSet(OrganizationFilterSet):
    class Meta:
        model = Link
        fields = {
            'group': ['exact']
        }


class LinkViewSet(OwnerBasedViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
    ordering = ['-created']
    search_fields = ('url', 'scraped_data')
